"""Leakage-safe round summaries supplied to the Omnigent Critic."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from .constants import ROUND_SIZE, TOTAL_BUDGET
from .errors import ProtocolError


def summarize_round(observations: list[dict[str, Any]], round_number: int) -> dict[str, Any]:
    current = [item for item in observations if int(item["round"]) == round_number]
    previous = [item for item in observations if int(item["round"]) < round_number]
    if len(current) != ROUND_SIZE:
        raise ProtocolError(f"critic requires a complete {ROUND_SIZE}-assay round")
    previous_best = max((float(item["fitness"]) for item in previous), default=None)
    round_best = max(float(item["fitness"]) for item in current)
    best_after = max(round_best, previous_best) if previous_best is not None else round_best
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in current:
        by_source[item["source_action"]].append(item)
    action_yield = {}
    for action, rows in sorted(by_source.items()):
        values = [float(item["fitness"]) for item in rows]
        improvements = 0 if previous_best is None else sum(value > previous_best for value in values)
        predicted = [
            (float(item["model_score"]), float(item["fitness"]))
            for item in rows
            if item.get("model_score") is not None
        ]
        rmse = None
        if predicted:
            rmse = math.sqrt(sum((prediction - actual) ** 2 for prediction, actual in predicted) / len(predicted))
        action_yield[action] = {
            "n": len(rows),
            "best_fitness": max(values),
            "mean_fitness": sum(values) / len(values),
            "improvements_over_previous_best": improvements,
            "new_point_prediction_rmse": rmse,
        }
    return {
        "round": round_number,
        "assays_in_round": len(current),
        "assays_total": len(observations),
        "remaining_budget": TOTAL_BUDGET - len(observations),
        "best_before": previous_best,
        "round_best": round_best,
        "best_after": best_after,
        "improved_best": previous_best is None or best_after > previous_best,
        "action_yield": action_yield,
        "leakage_inputs": "observed_measurements_and_proposal_metadata_only",
        "questions_for_critic": [
            "Which source produced improvements relative to the entering best?",
            "Did new-point prediction error improve or deteriorate?",
            "Did uncertainty sampling provide decision-relevant information?",
            "Are local candidates concentrated around one parent or plateau?",
            "Does this evidence justify changing allocation next round?",
        ],
    }
