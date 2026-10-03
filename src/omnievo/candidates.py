"""Deterministic candidate primitives shared by adaptive and fixed strategies."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Iterable

from .constants import ACTIONS, ROUND_SIZE, WILD_TYPE_SEQUENCE
from .errors import ProtocolError
from .space import hamming, hamming_neighbors, seeded_tie_key, theoretical_sequences, validate_sequence


Candidate = dict[str, Any]


def _measured_set(measured: Iterable[str]) -> set[str]:
    # WT fitness is public prior knowledge and must never consume a paid assay.
    return {WILD_TYPE_SEQUENCE, *(validate_sequence(item) for item in measured)}


def annotate_distance_to_best(
    pools: dict[str, list[Candidate]], observations: list[dict[str, Any]]
) -> dict[str, list[Candidate]]:
    if not observations:
        raise ProtocolError("distance-to-best annotation requires observations")
    best = validate_sequence(max(observations, key=lambda item: float(item["fitness"]))["sequence"])
    return {
        action: [
            {**item, "distance_to_best": hamming(validate_sequence(item["sequence"]), best)}
            for item in pool
        ]
        for action, pool in pools.items()
    }


def generate_random_pool(measured: Iterable[str], pool_size: int, seed: int) -> list[Candidate]:
    excluded = _measured_set(measured)
    available = [item for item in theoretical_sequences() if item not in excluded]
    rng = random.Random(seed)
    rng.shuffle(available)
    return [
        {
            "sequence": sequence,
            "source_action": "RANDOM_SAMPLE",
            "source_agent": "deterministic-random-tool",
            "rank": rank,
            "score": None,
            "score_definition": "seeded_uniform_order_over_theoretical_space",
        }
        for rank, sequence in enumerate(available[:pool_size], start=1)
    ]


def generate_local_pool(
    observations: list[dict[str, Any]],
    pool_size: int,
    seed: int,
    elite_parents: int = 4,
) -> list[Candidate]:
    if not observations:
        raise ProtocolError("local search requires at least one observed sequence")
    measured = _measured_set(item["sequence"] for item in observations)
    ranked_observations = sorted(
        observations,
        key=lambda item: (-float(item["fitness"]), seeded_tie_key(validate_sequence(item["sequence"]), seed)),
    )
    output: list[Candidate] = []
    emitted: set[str] = set()
    best_sequence = validate_sequence(ranked_observations[0]["sequence"])
    for parent in ranked_observations[:elite_parents]:
        parent_sequence = validate_sequence(parent["sequence"])
        neighbors = sorted(hamming_neighbors(parent_sequence), key=lambda item: seeded_tie_key(item, seed))
        for sequence in neighbors:
            if sequence in measured or sequence in emitted:
                continue
            emitted.add(sequence)
            output.append(
                {
                    "sequence": sequence,
                    "source_action": "LOCAL_MUTATE",
                    "source_agent": "local-search-specialist",
                    "parent": parent_sequence,
                    "parent_observed_fitness": float(parent["fitness"]),
                    "hamming_distance": 1,
                    "distance_to_best": hamming(sequence, best_sequence),
                    "rank": len(output) + 1,
                    "score": float(parent["fitness"]),
                    "score_definition": "parent_observed_fitness_then_seeded_order",
                }
            )
            if len(output) >= pool_size:
                return output
    return output


def generate_exploitation_pool(
    score_records: Iterable[dict[str, Any]], measured: Iterable[str], pool_size: int, seed: int
) -> list[Candidate]:
    excluded = _measured_set(measured)
    ranked = sorted(
        (item for item in score_records if validate_sequence(item["sequence"]) not in excluded),
        key=lambda item: (-float(item["predicted_fitness"]), seeded_tie_key(item["sequence"], seed)),
    )
    return [
        {
            "sequence": item["sequence"],
            "source_action": "EXPLOIT_MODEL",
            "source_agent": "exploitation-specialist",
            "rank": rank,
            "score": float(item["predicted_fitness"]),
            "model_score": float(item["predicted_fitness"]),
            "model_uncertainty": float(item["uncertainty"]),
            "score_definition": "predicted_mean",
        }
        for rank, item in enumerate(ranked[:pool_size], start=1)
    ]


def generate_uncertainty_pool(
    score_records: Iterable[dict[str, Any]], measured: Iterable[str], pool_size: int, seed: int
) -> list[Candidate]:
    excluded = _measured_set(measured)
    ranked = sorted(
        (item for item in score_records if validate_sequence(item["sequence"]) not in excluded),
        key=lambda item: (-float(item["uncertainty"]), seeded_tie_key(item["sequence"], seed)),
    )
    return [
        {
            "sequence": item["sequence"],
            "source_action": "EXPLORE_UNCERTAIN",
            "source_agent": "exploration-specialist",
            "rank": rank,
            "score": float(item["uncertainty"]),
            "model_score": float(item["predicted_fitness"]),
            "model_uncertainty": float(item["uncertainty"]),
            "score_definition": "extra_trees_across_tree_standard_deviation",
        }
        for rank, item in enumerate(ranked[:pool_size], start=1)
    ]


def generate_ucb_pool(
    score_records: Iterable[dict[str, Any]],
    measured: Iterable[str],
    pool_size: int,
    seed: int,
    beta: float = 1.0,
) -> list[Candidate]:
    excluded = _measured_set(measured)
    ranked = sorted(
        (item for item in score_records if validate_sequence(item["sequence"]) not in excluded),
        key=lambda item: (
            -(float(item["predicted_fitness"]) + beta * float(item["uncertainty"])),
            seeded_tie_key(item["sequence"], seed),
        ),
    )
    return [
        {
            "sequence": item["sequence"],
            "source_action": "EXPLORE_UNCERTAIN",
            "source_agent": "fixed-ucb-policy",
            "rank": rank,
            "score": float(item["predicted_fitness"]) + beta * float(item["uncertainty"]),
            "model_score": float(item["predicted_fitness"]),
            "model_uncertainty": float(item["uncertainty"]),
            "score_definition": f"predicted_mean_plus_{beta:g}_times_ensemble_std",
        }
        for rank, item in enumerate(ranked[:pool_size], start=1)
    ]


def generate_diversity_pool(
    measured: Iterable[str], pool_size: int, seed: int, candidate_limit: int | None = None
) -> list[Candidate]:
    observed = sorted(_measured_set(measured))
    universe = [item for item in theoretical_sequences() if item not in set(observed)]
    if candidate_limit is not None and candidate_limit < len(universe):
        universe = sorted(universe, key=lambda item: seeded_tie_key(item, seed))[:candidate_limit]
    if not observed:
        return generate_random_pool([], pool_size, seed)
    try:
        import numpy as np

        encoded = np.frombuffer("".join(universe).encode("ascii"), dtype=np.uint8).reshape(-1, 4)
        minimum = np.full(len(universe), 4, dtype=np.uint8)
        for item in observed:
            parent = np.frombuffer(item.encode("ascii"), dtype=np.uint8)
            minimum = np.minimum(minimum, np.count_nonzero(encoded != parent, axis=1))
        tie_breaker = np.random.default_rng(seed).random(len(universe))
        order = np.lexsort((tie_breaker, -minimum.astype(np.int8)))[:pool_size]
        ranked = [(int(minimum[index]), universe[int(index)]) for index in order]
    except ImportError:
        ranked = sorted(
            (
                (min(sum(a != b for a, b in zip(sequence, item)) for item in observed), sequence)
                for sequence in universe
            ),
            key=lambda item: (-item[0], seeded_tie_key(item[1], seed)),
        )[:pool_size]
    return [
        {
            "sequence": sequence,
            "source_action": "EXPLORE_DIVERSE",
            "source_agent": "exploration-specialist",
            "rank": rank,
            "score": distance,
            "distance_to_observed": distance,
            "score_definition": "minimum_hamming_distance_to_observed",
        }
        for rank, (distance, sequence) in enumerate(ranked[:pool_size], start=1)
    ]


def select_from_allocations(
    pools: dict[str, list[Candidate]],
    allocation: dict[str, int],
    measured: Iterable[str],
    round_size: int = ROUND_SIZE,
) -> tuple[list[Candidate], list[Candidate]]:
    """Deduplicate by source priority and return selected candidates plus fallbacks."""
    unknown = set(allocation).difference(ACTIONS)
    if unknown or sum(allocation.values()) != round_size:
        raise ProtocolError("allocation must use allowed actions and sum to the round size")
    excluded = _measured_set(measured)
    selected: list[Candidate] = []
    used = set(excluded)
    cursors = defaultdict(int)
    for action, slots in allocation.items():
        pool = pools.get(action, [])
        taken = 0
        while cursors[action] < len(pool) and taken < slots:
            item = dict(pool[cursors[action]])
            cursors[action] += 1
            sequence = validate_sequence(item["sequence"])
            if sequence in used:
                continue
            if item.get("source_action") != action:
                raise ProtocolError(f"candidate source mismatch for {sequence}")
            used.add(sequence)
            selected.append(item)
            taken += 1
        if taken != slots:
            raise ProtocolError(f"pool {action} cannot fill its {slots} allocated slots")
    fallbacks: list[Candidate] = []
    for action in allocation:
        for raw in pools.get(action, [])[cursors[action] :]:
            item = dict(raw)
            sequence = validate_sequence(item["sequence"])
            if sequence not in used:
                used.add(sequence)
                fallbacks.append(item)
    return selected, fallbacks
