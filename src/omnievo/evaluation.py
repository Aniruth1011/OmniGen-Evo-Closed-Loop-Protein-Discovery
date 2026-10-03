"""Observed-run aggregation and paired statistics without active-run oracle access."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .artifacts import write_csv, write_json
from .constants import ROUND_SIZE, TOTAL_BUDGET
from .errors import ProtocolError


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def summarize_observations(
    observations: list[dict[str, Any]], strategy: str, seed: int, run_id: str
) -> dict[str, Any]:
    ordered = sorted(observations, key=lambda item: int(item["assay_index_global"]))
    if len(ordered) != TOTAL_BUDGET:
        raise ProtocolError(f"completed evaluation requires exactly {TOTAL_BUDGET} observations")
    best = -math.inf
    trajectory = []
    improvements = 0
    for item in ordered:
        value = float(item["fitness"])
        if value > best:
            best = value
            improvements += 1
        trajectory.append(best)
    round_best = {f"best_{count}": trajectory[count - 1] for count in (24, 48, 72, 96)}
    source_counts: dict[str, int] = defaultdict(int)
    source_improvements: dict[str, int] = defaultdict(int)
    entering_best = -math.inf
    for item in ordered:
        action = item["source_action"]
        source_counts[action] += 1
        value = float(item["fitness"])
        if value > entering_best:
            source_improvements[action] += 1
            entering_best = value
    return {
        "run_id": run_id,
        "strategy": strategy,
        "seed": int(seed),
        **round_best,
        "terminal_best_fitness": trajectory[-1],
        "best_so_far_auc": sum(trajectory) / len(trajectory),
        "n_record_improvements": improvements,
        "source_counts": dict(source_counts),
        "source_record_improvements": dict(source_improvements),
        "trajectory": trajectory,
    }


def discover_completed_runs(runs_root: str | Path) -> list[dict[str, Any]]:
    root = Path(runs_root)
    summaries = []
    for manifest_path in sorted(root.glob("*/seed_*/run_manifest.yaml")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        ledger_path = manifest_path.parent / "assay_ledger.jsonl"
        if not ledger_path.exists():
            continue
        observations = read_jsonl(ledger_path)
        if len(observations) != TOTAL_BUDGET:
            continue
        summaries.append(
            summarize_observations(
                observations,
                manifest["strategy"],
                int(manifest["seed"]),
                manifest["run_id"],
            )
        )
    return summaries


def _percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute percentile of empty values")
    position = fraction * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def paired_bootstrap(
    differences: list[float], n_resamples: int = 10_000, seed: int = 2026
) -> dict[str, float]:
    if not differences:
        raise ProtocolError("paired bootstrap requires at least one paired difference")
    rng = random.Random(seed)
    samples = []
    for _ in range(n_resamples):
        samples.append(statistics.fmean(rng.choice(differences) for _ in differences))
    samples.sort()
    return {
        "mean_difference": statistics.fmean(differences),
        "median_difference": statistics.median(differences),
        "ci_95_low": _percentile(samples, 0.025),
        "ci_95_high": _percentile(samples, 0.975),
        "win_rate": sum(value > 0 for value in differences) / len(differences),
    }


def paired_contrast(
    summaries: Iterable[dict[str, Any]],
    treatment: str = "adaptive",
    control: str = "fixed_mixture",
) -> dict[str, Any]:
    indexed = {(item["strategy"], int(item["seed"])): item for item in summaries}
    seeds = sorted(
        seed
        for strategy, seed in indexed
        if strategy == treatment and (control, seed) in indexed
    )
    differences = [
        float(indexed[(treatment, seed)]["terminal_best_fitness"])
        - float(indexed[(control, seed)]["terminal_best_fitness"])
        for seed in seeds
    ]
    result: dict[str, Any] = {
        "primary_endpoint": "best observed fitness after 96 successful assays",
        "treatment": treatment,
        "control": control,
        "paired_seeds": seeds,
        "n_pairs": len(seeds),
        "differences": differences,
    }
    if differences:
        result.update(paired_bootstrap(differences))
        try:
            from scipy.stats import wilcoxon

            statistic, p_value = wilcoxon(differences, alternative="two-sided")
            result["wilcoxon_sensitivity"] = {
                "statistic": float(statistic),
                "two_sided_p_value": float(p_value),
            }
        except (ImportError, ValueError):
            result["wilcoxon_sensitivity"] = None
    return result


def strategy_summaries(summaries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for item in summaries:
        grouped[item["strategy"]].append(float(item["terminal_best_fitness"]))
    output = []
    for strategy, values in sorted(grouped.items()):
        ordered = sorted(values)
        output.append(
            {
                "strategy": strategy,
                "n_runs": len(values),
                "mean_terminal_best": statistics.fmean(values),
                "median_terminal_best": statistics.median(values),
                "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0.0,
                "q1": _percentile(ordered, 0.25),
                "q3": _percentile(ordered, 0.75),
            }
        )
    return output


def write_analysis(runs_root: str | Path, artifacts_root: str | Path) -> dict[str, Any]:
    summaries = discover_completed_runs(runs_root)
    output = Path(artifacts_root)
    output.mkdir(parents=True, exist_ok=True)
    flat_fields = [
        "run_id",
        "strategy",
        "seed",
        "best_24",
        "best_48",
        "best_72",
        "best_96",
        "terminal_best_fitness",
        "best_so_far_auc",
        "n_record_improvements",
    ]
    write_csv(output / "run_summary.csv", summaries, flat_fields)
    grouped = strategy_summaries(summaries)
    write_csv(
        output / "strategy_summary.csv",
        grouped,
        [
            "strategy",
            "n_runs",
            "mean_terminal_best",
            "median_terminal_best",
            "standard_deviation",
            "q1",
            "q3",
        ],
    )
    contrast = paired_contrast(summaries)
    write_json(output / "primary_contrast.json", contrast)
    return {"n_completed_runs": len(summaries), "primary_contrast": contrast}
