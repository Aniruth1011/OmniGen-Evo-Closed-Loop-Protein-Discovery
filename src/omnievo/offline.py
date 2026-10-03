"""Post-run oracle evaluator; never register this module as an Omnigent tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import write_csv, write_json
from .evaluation import discover_completed_runs, read_jsonl
from .lab.oracle import PrivateOracle


def evaluate_completed_runs(
    oracle_path: str | Path,
    runs_root: str | Path,
    output_dir: str | Path,
    sequence_column: str = "sequence",
    fitness_column: str = "fitness",
) -> dict[str, Any]:
    """Compute top-tail/regret metrics only after runs are complete and frozen."""
    oracle = PrivateOracle.from_csv(oracle_path, sequence_column, fitness_column)
    values = sorted(oracle._values.values())  # Deliberately private/offline process only.
    maximum = values[-1]
    top_one = values[max(0, int(0.99 * (len(values) - 1)))]
    top_point_one = values[max(0, int(0.999 * (len(values) - 1)))]
    rows = []
    for summary in discover_completed_runs(runs_root):
        ledger = Path(runs_root) / summary["strategy"] / f"seed_{summary['seed']:03d}" / "assay_ledger.jsonl"
        observed = read_jsonl(ledger)
        fitness = [float(item["fitness"]) for item in observed]
        rows.append(
            {
                "run_id": summary["run_id"],
                "strategy": summary["strategy"],
                "seed": summary["seed"],
                "terminal_best_fitness": max(fitness),
                "normalized_regret": 0.0 if maximum == 0 else (maximum - max(fitness)) / abs(maximum),
                "top_1_percent_hit": int(any(value >= top_one for value in fitness)),
                "top_0_1_percent_hit": int(any(value >= top_point_one for value in fitness)),
            }
        )
    output = Path(output_dir)
    write_csv(
        output / "offline_run_metrics.csv",
        rows,
        [
            "run_id",
            "strategy",
            "seed",
            "terminal_best_fitness",
            "normalized_regret",
            "top_1_percent_hit",
            "top_0_1_percent_hit",
        ],
    )
    metadata = {
        "n_runs": len(rows),
        "oracle_checksum": oracle.audit.checksum_sha256,
        "oracle_rows": oracle.audit.row_count,
        "evaluation_stage": "offline_after_completed_runs",
    }
    write_json(output / "offline_evaluation_metadata.json", metadata)
    return metadata
