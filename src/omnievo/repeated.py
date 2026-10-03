"""Repeated fixed-control execution; adaptive runs remain Omnigent-orchestrated."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .artifacts import append_jsonl, timestamp
from .baselines import BASELINE_STRATEGIES, run_baseline
from .errors import ProtocolError
from .lab.client import LabClient


def _confirmatory_approved(approval_path: str | Path) -> bool:
    path = Path(approval_path)
    return path.exists() and "CONFIRMATORY_PROTOCOL_APPROVED" in path.read_text(encoding="utf-8")


def run_repeated_baselines(
    client: LabClient,
    seeds: Iterable[int],
    runs_root: str | Path,
    scope: str = "development",
    strategies: Iterable[str] = BASELINE_STRATEGIES,
    approval_path: str | Path = "logs/approvals.md",
) -> list[dict]:
    if scope not in {"development", "confirmatory"}:
        raise ProtocolError("scope must be development or confirmatory")
    if scope == "confirmatory" and not _confirmatory_approved(approval_path):
        raise ProtocolError("confirmatory execution requires recorded human protocol approval")
    results = []
    for seed in seeds:
        for strategy in strategies:
            started = timestamp()
            result = run_baseline(client, strategy, int(seed), runs_root)
            results.append(result)
            append_jsonl(
                Path(runs_root).parent / "logs" / "run_index.jsonl",
                {
                    "run_id": result["run_id"],
                    "strategy": strategy,
                    "seed": int(seed),
                    "scope": scope,
                    "status": result["status"]["status"],
                    "started_at": started,
                    "completed_at": timestamp(),
                },
            )
    return results

