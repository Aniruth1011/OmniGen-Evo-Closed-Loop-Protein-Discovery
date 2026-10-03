"""Round execution gates shared by Omnigent and fixed controls."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .artifacts import append_jsonl, validate_planner_decision, write_csv, write_json, write_yaml_compatible
from .constants import ROUND_SIZE
from .errors import ProtocolError
from .lab.client import LabClient
from .space import validate_sequence


OBSERVATION_FIELDS = [
    "round",
    "assay_index_global",
    "sequence",
    "fitness",
    "source_action",
    "proposal_agent",
    "planner_batch_id",
    "source_rank",
    "model_score",
    "model_uncertainty",
    "distance_to_best",
    "parent",
    "proposal_metadata",
    "measured_at",
]


def execute_source_preserving_allocation(
    client: LabClient,
    run_id: str,
    round_number: int,
    decision: dict[str, Any],
    fallbacks: list[dict[str, Any]],
    run_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Measure exactly the requested successful slots per source, refilling in-source."""
    observations = client.observations(run_id)
    validate_planner_decision(decision, (item["sequence"] for item in observations))
    selected = decision["selected_sequences"]
    queues: dict[str, list[dict[str, Any]]] = {action: [] for action in decision["allocation"]}
    for raw in selected + fallbacks:
        action = raw.get("source_action")
        if action in queues:
            item = dict(raw)
            item["sequence"] = validate_sequence(item["sequence"])
            item.setdefault("proposal_agent", item.get("source_agent", "experiment-planner"))
            queues[action].append(item)

    all_measurements: list[dict[str, Any]] = []
    all_rejections: list[dict[str, Any]] = []
    for action, desired in decision["allocation"].items():
        successful = 0
        cursor = 0
        attempt = 0
        while successful < desired:
            needed = desired - successful
            proposal_slice = queues[action][cursor : cursor + needed]
            if not proposal_slice:
                raise ProtocolError(f"fallback pool exhausted while filling {action}")
            cursor += len(proposal_slice)
            attempt += 1
            result = client.measure_batch(
                run_id,
                round_number,
                proposal_slice,
                f"{decision.get('batch_id', f'{run_id}-r{round_number:02d}')}-{action.lower()}-{attempt}",
            )
            all_measurements.extend(result["measurements"])
            all_rejections.extend(result["rejections"])
            successful += len(result["measurements"])

    if len(all_measurements) != ROUND_SIZE:
        raise ProtocolError(f"round execution produced {len(all_measurements)}, expected {ROUND_SIZE}")
    result = {
        "run_id": run_id,
        "round": round_number,
        "assays_requested": ROUND_SIZE,
        "assays_successful": len(all_measurements),
        "unavailable_rejections": sum(item["status"] == "UNAVAILABLE" for item in all_rejections),
        "measurements": all_measurements,
        "rejections": all_rejections,
        "status": client.status(run_id),
    }
    if run_dir is not None:
        root = Path(run_dir)
        round_dir = root / f"round_{round_number:02d}"
        write_yaml_compatible(round_dir / "planner_decision.yaml", decision)
        write_json(round_dir / "round_result.json", result)
        write_csv(round_dir / "measurements.csv", all_measurements, OBSERVATION_FIELDS)
        all_observations = client.observations(run_id)
        write_csv(round_dir / "observations.csv", all_observations, OBSERVATION_FIELDS)
        for item in all_measurements:
            append_jsonl(root / "assay_ledger.jsonl", item)
    return result


def execute_common_initialization(
    client: LabClient,
    run_id: str,
    candidates: list[dict[str, Any]],
    run_dir: str | Path | None = None,
) -> dict[str, Any]:
    cursor = 0
    all_measurements: list[dict[str, Any]] = []
    all_rejections: list[dict[str, Any]] = []
    attempt = 0
    while len(all_measurements) < ROUND_SIZE:
        needed = ROUND_SIZE - len(all_measurements)
        proposal_slice = candidates[cursor : cursor + needed]
        if not proposal_slice:
            raise ProtocolError("common-initialization fallback pool exhausted")
        cursor += len(proposal_slice)
        attempt += 1
        result = client.measure_batch(run_id, 1, proposal_slice, f"{run_id}-common-init-{attempt}")
        all_measurements.extend(result["measurements"])
        all_rejections.extend(result["rejections"])
    result = {
        "run_id": run_id,
        "round": 1,
        "assays_successful": len(all_measurements),
        "measurements": all_measurements,
        "rejections": all_rejections,
        "status": client.status(run_id),
    }
    if run_dir is not None:
        root = Path(run_dir)
        round_dir = root / "round_01"
        write_json(round_dir / "round_result.json", result)
        write_csv(round_dir / "measurements.csv", all_measurements, OBSERVATION_FIELDS)
        write_csv(round_dir / "observations.csv", all_measurements, OBSERVATION_FIELDS)
        for item in all_measurements:
            append_jsonl(root / "assay_ledger.jsonl", item)
    return result


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
