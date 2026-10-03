"""Honest aggregate figures generated only from completed run artifacts."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from .evaluation import discover_completed_runs, read_jsonl


def build_figures(runs_root: str | Path, output_dir: str | Path) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("figure generation requires the analysis dependencies") from exc
    summaries = discover_completed_runs(runs_root)
    if not summaries:
        raise ValueError("no completed runs are available for visualization")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in summaries:
        grouped[item["strategy"]].append(item)
    artifacts = []

    figure, axis = plt.subplots(figsize=(8, 4.5))
    for strategy, rows in sorted(grouped.items()):
        mean = [sum(row["trajectory"][i] for row in rows) / len(rows) for i in range(96)]
        axis.plot(range(1, 97), mean, label=strategy)
    axis.set(xlabel="Successful assays", ylabel="Mean best-observed fitness", title="GB1 search trajectory")
    axis.legend(fontsize=8)
    axis.grid(alpha=0.25)
    path = output / "best_fitness_trajectory.png"
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
    artifacts.append(str(path))

    figure, axis = plt.subplots(figsize=(8, 4.5))
    labels = sorted(grouped)
    values = [[row["terminal_best_fitness"] for row in grouped[label]] for label in labels]
    axis.boxplot(values, tick_labels=labels, showfliers=True)
    axis.set(ylabel="Best fitness after 96 assays", title="Terminal distribution (all completed seeds)")
    axis.tick_params(axis="x", rotation=25)
    axis.grid(axis="y", alpha=0.25)
    path = output / "terminal_distribution.png"
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)
    artifacts.append(str(path))

    indexed = {(row["strategy"], int(row["seed"])): row for row in summaries}
    paired_seeds = sorted(
        seed for strategy, seed in indexed if strategy == "adaptive" and ("fixed_mixture", seed) in indexed
    )
    if paired_seeds:
        differences = [
            indexed[("adaptive", seed)]["terminal_best_fitness"]
            - indexed[("fixed_mixture", seed)]["terminal_best_fitness"]
            for seed in paired_seeds
        ]
        figure, axis = plt.subplots(figsize=(8, 4.5))
        colors = ["#238b45" if value > 0 else "#cb181d" if value < 0 else "#777777" for value in differences]
        axis.axhline(0, color="black", linewidth=1)
        axis.bar([str(seed) for seed in paired_seeds], differences, color=colors)
        axis.set(
            xlabel="Paired seed",
            ylabel="Adaptive − fixed-mixture terminal best",
            title="Primary paired differences (all completed pairs)",
        )
        axis.tick_params(axis="x", rotation=90, labelsize=7)
        axis.grid(axis="y", alpha=0.25)
        path = output / "paired_terminal_differences.png"
        figure.tight_layout()
        figure.savefig(path, dpi=180)
        plt.close(figure)
        artifacts.append(str(path))

    adaptive_ledgers = []
    root = Path(runs_root)
    for summary in grouped.get("adaptive", []):
        ledger_path = root / "adaptive" / f"seed_{int(summary['seed']):03d}" / "assay_ledger.jsonl"
        if ledger_path.exists():
            adaptive_ledgers.append(read_jsonl(ledger_path))
    if adaptive_ledgers:
        actions = sorted(
            {
                row["source_action"]
                for ledger in adaptive_ledgers
                for row in ledger
                if int(row["round"]) > 1
            }
        )
        means = {action: [] for action in actions}
        yields = {action: [0, 0] for action in actions}
        for round_number in (2, 3, 4):
            for action in actions:
                counts = [
                    sum(int(row["round"]) == round_number and row["source_action"] == action for row in ledger)
                    for ledger in adaptive_ledgers
                ]
                means[action].append(sum(counts) / len(counts))
        for ledger in adaptive_ledgers:
            entering_best = max(float(row["fitness"]) for row in ledger if int(row["round"]) == 1)
            for row in sorted(ledger, key=lambda item: int(item["assay_index_global"])):
                if int(row["round"]) == 1:
                    continue
                action = row["source_action"]
                yields[action][1] += 1
                value = float(row["fitness"])
                if value > entering_best:
                    yields[action][0] += 1
                    entering_best = value

        figure, axis = plt.subplots(figsize=(8, 4.5))
        bottoms = [0.0, 0.0, 0.0]
        for action in actions:
            axis.bar([2, 3, 4], means[action], bottom=bottoms, label=action)
            bottoms = [left + right for left, right in zip(bottoms, means[action])]
        axis.set(
            xticks=[2, 3, 4],
            xlabel="Adaptive round",
            ylabel="Mean successful assay slots",
            title="Omnigent adaptive allocation by round",
        )
        axis.legend(fontsize=7)
        path = output / "adaptive_round_allocation.png"
        figure.tight_layout()
        figure.savefig(path, dpi=180)
        plt.close(figure)
        artifacts.append(str(path))

        figure, axis = plt.subplots(figsize=(8, 4.5))
        rates = [yields[action][0] / yields[action][1] if yields[action][1] else 0.0 for action in actions]
        axis.bar(actions, rates)
        axis.set(ylabel="Record-improvement yield", title="Adaptive acquisition-source yield")
        axis.tick_params(axis="x", rotation=25)
        axis.grid(axis="y", alpha=0.25)
        path = output / "adaptive_source_yield.png"
        figure.tight_layout()
        figure.savefig(path, dpi=180)
        plt.close(figure)
        artifacts.append(str(path))

    offline_path = Path(runs_root).parent / "artifacts" / "tables" / "offline_run_metrics.csv"
    if offline_path.exists():
        hits: dict[str, list[int]] = defaultdict(list)
        with offline_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                hits[row["strategy"]].append(int(row["top_1_percent_hit"]))
        labels = sorted(hits)
        rates = [sum(hits[label]) / len(hits[label]) for label in labels]
        figure, axis = plt.subplots(figsize=(8, 4.5))
        axis.bar(labels, rates)
        axis.set(ylabel="Top-1% hit rate", ylim=(0, 1), title="Offline top-tail discovery")
        axis.tick_params(axis="x", rotation=25)
        axis.grid(axis="y", alpha=0.25)
        path = output / "top_1_percent_hit_rate.png"
        figure.tight_layout()
        figure.savefig(path, dpi=180)
        plt.close(figure)
        artifacts.append(str(path))
    return artifacts
