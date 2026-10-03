"""Fair fixed-policy controls. Adaptive allocation is intentionally absent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import write_json, write_yaml_compatible
from .candidates import (
    annotate_distance_to_best,
    generate_diversity_pool,
    generate_exploitation_pool,
    generate_local_pool,
    generate_random_pool,
    generate_ucb_pool,
    generate_uncertainty_pool,
    select_from_allocations,
)
from .constants import FIXED_MIXTURE, ROUND_SIZE
from .errors import ProtocolError
from .lab.client import LabClient
from .protocol import execute_common_initialization, execute_source_preserving_allocation
from .surrogate import fit_and_score, load_score_records


BASELINE_STRATEGIES = ("random", "greedy_local", "fixed_exploit", "fixed_ucb", "fixed_mixture")


def common_initialization_candidates(seed: int, pool_size: int = 256) -> list[dict[str, Any]]:
    return generate_random_pool([], pool_size, seed)


def _allocation_for(strategy: str) -> dict[str, int]:
    if strategy == "random":
        return {"RANDOM_SAMPLE": ROUND_SIZE}
    if strategy == "greedy_local":
        return {"LOCAL_MUTATE": ROUND_SIZE}
    if strategy == "fixed_exploit":
        return {"EXPLOIT_MODEL": ROUND_SIZE}
    if strategy == "fixed_ucb":
        return {"EXPLORE_UNCERTAIN": ROUND_SIZE}
    if strategy == "fixed_mixture":
        return dict(FIXED_MIXTURE)
    raise ProtocolError(f"unknown baseline strategy: {strategy}")


def run_baseline(
    client: LabClient,
    strategy: str,
    seed: int,
    runs_root: str | Path,
    candidate_pool_size: int = 128,
    surrogate_n_estimators: int = 128,
) -> dict[str, Any]:
    """Execute one preregistered fixed policy using the common accounting path."""
    if strategy not in BASELINE_STRATEGIES:
        raise ProtocolError(f"unsupported strategy: {strategy}")
    run_id = f"{strategy}_seed_{seed:03d}"
    run_dir = Path(runs_root) / strategy / f"seed_{seed:03d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    client.create_run(run_id, strategy, seed)
    manifest = {
        "run_id": run_id,
        "strategy": strategy,
        "seed": seed,
        "round_size": 24,
        "total_budget": 96,
        "initialization": "seeded uniform theoretical-space order shared by paired seed",
        "surrogate": None if strategy in {"random", "greedy_local"} else "ExtraTreesRegressor",
        "encoding": None if strategy in {"random", "greedy_local"} else "4x20 one-hot",
        "initialization_candidates": str(run_dir / "initialization_candidates.json"),
    }
    initialization = common_initialization_candidates(seed)
    write_json(run_dir / "initialization_candidates.json", initialization)
    write_yaml_compatible(run_dir / "run_manifest.yaml", manifest)
    execute_common_initialization(client, run_id, initialization, run_dir)

    round_summaries = []
    for round_number in range(2, 5):
        observations = client.observations(run_id)
        measured = [item["sequence"] for item in observations]
        allocation = _allocation_for(strategy)
        pool_seed = seed * 10_000 + round_number
        pool_target = max(candidate_pool_size, ROUND_SIZE * 4)
        pools: dict[str, list[dict[str, Any]]] = {}
        score_records = None
        if strategy not in {"random", "greedy_local"}:
            report = fit_and_score(
                observations,
                run_dir / f"round_{round_number:02d}",
                run_id,
                round_number,
                pool_seed,
                n_estimators=surrogate_n_estimators,
            )
            score_records = load_score_records(report["artifacts"]["candidate_scores"])
        if "RANDOM_SAMPLE" in allocation:
            pools["RANDOM_SAMPLE"] = generate_random_pool(measured, pool_target, pool_seed)
        if "LOCAL_MUTATE" in allocation:
            pools["LOCAL_MUTATE"] = generate_local_pool(observations, pool_target, pool_seed, elite_parents=8)
        if "EXPLOIT_MODEL" in allocation:
            assert score_records is not None
            pools["EXPLOIT_MODEL"] = generate_exploitation_pool(score_records, measured, pool_target, pool_seed)
        if "EXPLORE_UNCERTAIN" in allocation:
            assert score_records is not None
            pools["EXPLORE_UNCERTAIN"] = (
                generate_ucb_pool(score_records, measured, pool_target, pool_seed)
                if strategy == "fixed_ucb"
                else generate_uncertainty_pool(score_records, measured, pool_target, pool_seed)
            )
        if "EXPLORE_DIVERSE" in allocation:
            pools["EXPLORE_DIVERSE"] = generate_diversity_pool(measured, pool_target, pool_seed)
        pools = annotate_distance_to_best(pools, observations)
        selected, fallbacks = select_from_allocations(pools, allocation, measured)
        decision = {
            "run_id": run_id,
            "round": round_number,
            "budget": ROUND_SIZE,
            "batch_id": f"{run_id}-r{round_number:02d}",
            "allocation": allocation,
            "selected_sequences": selected,
            "rationale": [
                {
                    "evidence_id": "PREREGISTERED_FIXED_POLICY",
                    "implication": "Allocation is fixed by the baseline definition and cannot react to outcomes.",
                }
            ],
            "validation": {"unique": True, "unmeasured": True, "count": ROUND_SIZE},
        }
        write_json(run_dir / f"round_{round_number:02d}" / "candidate_pools.json", pools)
        summary = execute_source_preserving_allocation(
            client, run_id, round_number, decision, fallbacks, run_dir
        )
        round_summaries.append(summary)
    return {
        "run_id": run_id,
        "strategy": strategy,
        "seed": seed,
        "status": client.status(run_id),
        "terminal_best_fitness": max(float(item["fitness"]) for item in client.observations(run_id)),
        "rounds": round_summaries,
    }
