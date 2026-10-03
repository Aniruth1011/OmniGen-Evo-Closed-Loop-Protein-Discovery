"""Transactional, restart-safe assay accounting for the private lab."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from ..constants import N_ROUNDS, ROUND_SIZE, TOTAL_BUDGET
from ..errors import BudgetError, ProtocolError
from ..space import validate_sequence
from .oracle import PrivateOracle


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LabState:
    def __init__(self, database_path: str | Path, ledger_path: str | Path):
        self.database_path = Path(database_path).resolve()
        self.ledger_path = Path(ledger_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_lock = threading.Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    strategy TEXT NOT NULL,
                    seed INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS assays (
                    run_id TEXT NOT NULL,
                    round INTEGER NOT NULL,
                    assay_index_global INTEGER NOT NULL,
                    assay_index_round INTEGER NOT NULL,
                    sequence TEXT NOT NULL,
                    fitness REAL NOT NULL,
                    source_action TEXT NOT NULL,
                    proposal_agent TEXT NOT NULL,
                    planner_batch_id TEXT NOT NULL,
                    source_rank INTEGER,
                    model_score REAL,
                    model_uncertainty REAL,
                    distance_to_best INTEGER,
                    parent TEXT,
                    proposal_metadata TEXT NOT NULL DEFAULT '{}',
                    measured_at TEXT NOT NULL,
                    PRIMARY KEY (run_id, sequence),
                    UNIQUE (run_id, assay_index_global),
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                );
                CREATE TABLE IF NOT EXISTS rejections (
                    rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    round INTEGER NOT NULL,
                    sequence TEXT,
                    reason TEXT NOT NULL,
                    source_action TEXT,
                    planner_batch_id TEXT,
                    rejected_at TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                );
                """
            )
            existing = {
                row["name"] for row in connection.execute("PRAGMA table_info(assays)").fetchall()
            }
            migrations = {
                "source_rank": "INTEGER",
                "model_score": "REAL",
                "model_uncertainty": "REAL",
                "distance_to_best": "INTEGER",
                "parent": "TEXT",
                "proposal_metadata": "TEXT NOT NULL DEFAULT '{}'",
            }
            for column, definition in migrations.items():
                if column not in existing:
                    connection.execute(f"ALTER TABLE assays ADD COLUMN {column} {definition}")

    def create_run(self, run_id: str, strategy: str, seed: int) -> dict[str, Any]:
        if not run_id or any(char.isspace() for char in run_id):
            raise ProtocolError("run_id must be non-empty and contain no whitespace")
        if not strategy:
            raise ProtocolError("strategy is required")
        with self._connect() as connection:
            try:
                connection.execute(
                    "INSERT INTO runs(run_id, strategy, seed, created_at) VALUES (?, ?, ?, ?)",
                    (run_id, strategy, int(seed), utc_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise ProtocolError(f"run already exists: {run_id}") from exc
        return self.status(run_id)

    def status(self, run_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            run = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
            if run is None:
                raise ProtocolError(f"unknown run: {run_id}")
            by_round = {
                int(row["round"]): int(row["n"])
                for row in connection.execute(
                    "SELECT round, COUNT(*) AS n FROM assays WHERE run_id = ? GROUP BY round",
                    (run_id,),
                )
            }
            total = sum(by_round.values())
            return {
                "run_id": run["run_id"],
                "strategy": run["strategy"],
                "seed": run["seed"],
                "status": run["status"],
                "successful_assays": total,
                "remaining_budget": TOTAL_BUDGET - total,
                "round_counts": {str(i): by_round.get(i, 0) for i in range(1, N_ROUNDS + 1)},
            }

    def measure(
        self,
        oracle: PrivateOracle,
        run_id: str,
        round_number: int,
        proposals: Iterable[dict[str, Any]],
        planner_batch_id: str,
    ) -> dict[str, Any]:
        if round_number not in range(1, N_ROUNDS + 1):
            raise ProtocolError(f"round must be between 1 and {N_ROUNDS}")
        if not planner_batch_id:
            raise ProtocolError("planner_batch_id is required")
        proposal_list = list(proposals)
        if not proposal_list:
            raise ProtocolError("at least one proposal is required")

        appended: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        with self._write_lock, self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                run = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
                if run is None:
                    raise ProtocolError(f"unknown run: {run_id}")
                if run["status"] != "ACTIVE":
                    raise BudgetError(f"run is not active: {run_id}")
                counts = {
                    int(row["round"]): int(row["n"])
                    for row in connection.execute(
                        "SELECT round, COUNT(*) AS n FROM assays WHERE run_id = ? GROUP BY round",
                        (run_id,),
                    )
                }
                for prior_round in range(1, round_number):
                    if counts.get(prior_round, 0) != ROUND_SIZE:
                        raise ProtocolError(
                            f"round {prior_round} must have exactly {ROUND_SIZE} successful assays before round {round_number}"
                        )
                if any(key > round_number and value for key, value in counts.items()):
                    raise ProtocolError("cannot submit an earlier round after a later round")
                round_count = counts.get(round_number, 0)
                total_count = sum(counts.values())
                if round_count >= ROUND_SIZE or total_count >= TOTAL_BUDGET:
                    raise BudgetError("requested round or run budget is already exhausted")

                seen_in_request: set[str] = set()
                for raw in proposal_list:
                    if round_count >= ROUND_SIZE or total_count >= TOTAL_BUDGET:
                        break
                    sequence = validate_sequence(raw.get("sequence", ""))
                    source_action = str(raw.get("source_action", "UNKNOWN"))
                    proposal_agent = str(raw.get("proposal_agent", "unknown"))
                    reason: str | None = None
                    if sequence in seen_in_request:
                        reason = "DUPLICATE_IN_REQUEST"
                    elif connection.execute(
                        "SELECT 1 FROM assays WHERE run_id = ? AND sequence = ?", (run_id, sequence)
                    ).fetchone():
                        reason = "ALREADY_MEASURED"
                    seen_in_request.add(sequence)
                    fitness = None if reason else oracle.lookup(sequence)
                    if reason is None and fitness is None:
                        reason = "UNAVAILABLE"
                    if reason:
                        item = {
                            "sequence": sequence,
                            "status": reason,
                            "source_action": source_action,
                        }
                        rejected.append(item)
                        connection.execute(
                            """INSERT INTO rejections(
                                run_id, round, sequence, reason, source_action, planner_batch_id, rejected_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (run_id, round_number, sequence, reason, source_action, planner_batch_id, utc_now()),
                        )
                        continue
                    round_count += 1
                    total_count += 1
                    record = {
                        "run_id": run_id,
                        "strategy": run["strategy"],
                        "seed": run["seed"],
                        "round": round_number,
                        "assay_index_global": total_count,
                        "assay_index_round": round_count,
                        "sequence": sequence,
                        "fitness": float(fitness),
                        "source_action": source_action,
                        "proposal_agent": proposal_agent,
                        "planner_batch_id": planner_batch_id,
                        "source_rank": raw.get("source_rank", raw.get("rank")),
                        "model_score": raw.get("model_score"),
                        "model_uncertainty": raw.get("model_uncertainty"),
                        "distance_to_best": raw.get("distance_to_best"),
                        "parent": raw.get("parent"),
                        "proposal_metadata": {
                            key: raw[key]
                            for key in (
                                "score",
                                "score_definition",
                                "distance_to_observed",
                                "hamming_distance",
                                "mutation",
                            )
                            if key in raw
                        },
                        "measured_at": utc_now(),
                    }
                    connection.execute(
                        """INSERT INTO assays(
                            run_id, round, assay_index_global, assay_index_round, sequence, fitness,
                            source_action, proposal_agent, planner_batch_id, source_rank, model_score,
                            model_uncertainty, distance_to_best, parent, proposal_metadata, measured_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        tuple(record[key] for key in (
                            "run_id", "round", "assay_index_global", "assay_index_round", "sequence",
                            "fitness", "source_action", "proposal_agent", "planner_batch_id", "source_rank",
                            "model_score", "model_uncertainty", "distance_to_best", "parent"
                        )) + (json.dumps(record["proposal_metadata"], sort_keys=True), record["measured_at"]),
                    )
                    appended.append(record)
                if total_count == TOTAL_BUDGET:
                    connection.execute("UPDATE runs SET status = 'COMPLETE' WHERE run_id = ?", (run_id,))
                connection.execute("COMMIT")
            except Exception:
                connection.execute("ROLLBACK")
                raise

        if appended:
            with self.ledger_path.open("a", encoding="utf-8") as handle:
                for record in appended:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        return {
            "run_id": run_id,
            "round": round_number,
            "measurements": appended,
            "rejections": rejected,
            "status": self.status(run_id),
        }

    def observations(self, run_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT round, assay_index_global, sequence, fitness, source_action,
                          proposal_agent, planner_batch_id, source_rank, model_score,
                          model_uncertainty, distance_to_best, parent, proposal_metadata, measured_at
                   FROM assays WHERE run_id = ? ORDER BY assay_index_global""",
                (run_id,),
            ).fetchall()
        if not rows and not self._run_exists(run_id):
            raise ProtocolError(f"unknown run: {run_id}")
        output = []
        for row in rows:
            item = dict(row)
            item["proposal_metadata"] = json.loads(item["proposal_metadata"] or "{}")
            output.append(item)
        return output

    def _run_exists(self, run_id: str) -> bool:
        with self._connect() as connection:
            return connection.execute("SELECT 1 FROM runs WHERE run_id = ?", (run_id,)).fetchone() is not None
