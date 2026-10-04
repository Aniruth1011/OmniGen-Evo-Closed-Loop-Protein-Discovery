"""Narrow deterministic tools exposed to the Omnigent Scientific Director.

Install the repository package in the Omnigent host before registering this agent
image. None of these tools accepts or reads the private oracle dataset path.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from omnievo.artifacts import (
    append_jsonl as _append_jsonl,
    timestamp as _timestamp,
    validate_planner_decision as _validate_planner_decision,
    write_json as _write_json,
)
from omnievo.baselines import common_initialization_candidates as _common_initialization_candidates
from omnievo.candidates import (
    annotate_distance_to_best as _annotate_distance_to_best,
    generate_diversity_pool as _generate_diversity_pool,
    generate_exploitation_pool as _generate_exploitation_pool,
    generate_local_pool as _generate_local_pool,
    generate_random_pool as _generate_random_pool,
    generate_uncertainty_pool as _generate_uncertainty_pool,
)
from omnievo.critique import summarize_round as _summarize_round
from omnievo.lab.client import LabClient as _LabClient
from omnievo.protocol import (
    execute_common_initialization as _execute_common_initialization,
    execute_source_preserving_allocation as _execute_source_preserving_allocation,
)
from omnievo.surrogate import fit_and_score as _fit_and_score, load_score_records as _load_score_records

__all__ = [
    "lab_status",
    "initialize_adaptive_run",
    "fit_observed_surrogate",
    "generate_all_candidate_pools",
    "prepare_critic_input",
    "save_hypothesis_report",
    "save_critic_report",
    "save_planner_decision",
    "record_critic_to_planner_handoff",
    "execute_planner_round",
]


def _client() -> _LabClient:
    # OMNIGENT_* survives the CLI -> daemon boundary; the legacy OMNIEVO_*
    # names remain supported for direct Python and test execution.
    url = os.environ.get("OMNIGENT_LAB_URL", os.environ.get("OMNIEVO_LAB_URL"))
    token = os.environ.get("OMNIGENT_LAB_TOKEN", os.environ.get("OMNIEVO_LAB_TOKEN"))
    if not url or not token:
        raise RuntimeError("authenticated virtual-lab client configuration is unavailable")
    return _LabClient(url, token)


def _load_structured(path: str | Path) -> Any:
    content = Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("non-JSON YAML requires PyYAML") from exc
        return yaml.safe_load(content)


def _safe_artifact_path(path: str | Path) -> Path:
    destination = Path(path).resolve()
    root = Path.cwd().resolve()
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise ValueError("agent artifacts must remain inside the project workspace") from exc
    if destination.suffix.lower() not in {".json", ".yaml", ".yml"}:
        raise ValueError("structured agent artifacts must use JSON or YAML paths")
    return destination


def lab_status(run_id: str) -> dict[str, Any]:
    """Return assay counts and remaining budget; never returns oracle-wide data."""
    return _client().status(run_id)


def initialize_adaptive_run(run_id: str, seed: int, run_dir: str) -> dict[str, Any]:
    """Create an adaptive run and execute its common, paired Round-1 initialization."""
    client = _client()
    client.create_run(run_id, "adaptive", seed)
    candidates = _common_initialization_candidates(seed)
    _write_json(Path(run_dir) / "initialization_candidates.json", candidates)
    _write_json(
        Path(run_dir) / "run_manifest.yaml",
        {
            "run_id": run_id,
            "strategy": "adaptive",
            "seed": seed,
            "round_size": 24,
            "total_budget": 96,
            "surrogate": "ExtraTreesRegressor",
            "encoding": "4x20 one-hot",
            "initialization_candidates": str(Path(run_dir) / "initialization_candidates.json"),
        },
    )
    result = _execute_common_initialization(
        client,
        run_id,
        candidates,
        run_dir,
    )
    # Make the terminal condition impossible to confuse with completion of a
    # single round. The run is complete only after 96 successful assays.
    status = result["status"]
    result["run_status"] = status["status"]
    result["terminal_condition_met"] = (
        status["status"] == "COMPLETE" and status["successful_assays"] == 96
    )
    result["required_next_action"] = (
        "FINALIZE" if result["terminal_condition_met"] else "ANALYZE_ROUND_1_THEN_PLAN_ROUND_2"
    )
    return result


def fit_observed_surrogate(
    run_id: str, round_number: int, seed: int, round_dir: str
) -> dict[str, Any]:
    """Fit ExtraTrees only on observations already returned by the lab."""
    return _fit_and_score(
        _client().observations(run_id),
        round_dir,
        run_id,
        round_number,
        seed,
    )


def generate_all_candidate_pools(
    run_id: str,
    round_number: int,
    seed: int,
    candidate_scores_path: str,
    output_path: str,
    pool_size: int = 128,
) -> dict[str, Any]:
    """Generate shared adaptive/fixed acquisition primitives without hidden labels."""
    observations = _client().observations(run_id)
    measured = [item["sequence"] for item in observations]
    scores = _load_score_records(candidate_scores_path)
    pools = {
        "EXPLOIT_MODEL": _generate_exploitation_pool(scores, measured, pool_size, seed),
        "EXPLORE_UNCERTAIN": _generate_uncertainty_pool(scores, measured, pool_size, seed),
        "EXPLORE_DIVERSE": _generate_diversity_pool(measured, pool_size, seed),
        "LOCAL_MUTATE": _generate_local_pool(observations, pool_size, seed, elite_parents=8),
        "RANDOM_SAMPLE": _generate_random_pool(measured, pool_size, seed),
    }
    pools = _annotate_distance_to_best(pools, observations)
    _write_json(output_path, pools)
    return {
        "run_id": run_id,
        "round": round_number,
        "pool_size": pool_size,
        "actions": {action: len(pool) for action, pool in pools.items()},
        "artifact": output_path,
    }


def prepare_critic_input(run_id: str, round_number: int, output_path: str) -> dict[str, Any]:
    """Create an observed-data-only diagnostic packet for the Scientific Critic."""
    summary = _summarize_round(_client().observations(run_id), round_number)
    _write_json(output_path, summary)
    return {"artifact": output_path, **summary}


def save_hypothesis_report(
    run_id: str, round_number: int, report: dict[str, Any], output_path: str
) -> dict[str, Any]:
    """Persist the Hypothesis Scientist's structured, concise report."""
    required = {"observations", "hypotheses", "strategy_implications", "uncertainties", "recommended_tests"}
    missing = required.difference(report)
    if missing:
        raise ValueError(f"hypothesis report is missing fields: {sorted(missing)}")
    value = {"run_id": run_id, "round": round_number, **report}
    destination = _safe_artifact_path(output_path)
    _write_json(destination, value)
    _append_jsonl(
        "logs/agent_events.jsonl",
        {
            "timestamp": _timestamp(),
            "agent": "hypothesis-scientist",
            "action": "scientific_hypothesis_update",
            "run_id": run_id,
            "round": round_number,
            "output": str(destination),
            "status": "success",
        },
    )
    return {"artifact": str(destination), "status": "saved"}


def save_critic_report(
    run_id: str, round_number: int, report: dict[str, Any], output_path: str
) -> dict[str, Any]:
    """Persist a critic report after validating clearance fields."""
    status = str(report.get("status", "")).upper()
    if status not in {"PASS", "WARN", "BLOCK"}:
        raise ValueError("critic status must be PASS, WARN, or BLOCK")
    required = {"findings", "policy_change_recommended", "recommended_change"}
    missing = required.difference(report)
    if missing:
        raise ValueError(f"critic report is missing fields: {sorted(missing)}")
    value = {"run_id": run_id, "round": round_number, **report}
    destination = _safe_artifact_path(output_path)
    _write_json(destination, value)
    _append_jsonl(
        "logs/agent_events.jsonl",
        {
            "timestamp": _timestamp(),
            "agent": "scientific-critic",
            "action": "critic_round_review",
            "run_id": run_id,
            "round": round_number,
            "output": str(destination),
            "status": status.lower(),
        },
    )
    return {"artifact": str(destination), "status": status}


def save_planner_decision(
    run_id: str, round_number: int, decision: dict[str, Any], output_path: str
) -> dict[str, Any]:
    """Persist an exact Omnigent planner batch after schema/budget validation."""
    observations = _client().observations(run_id)
    value = {"run_id": run_id, "round": round_number, **decision}
    _validate_planner_decision(value, (item["sequence"] for item in observations))
    destination = _safe_artifact_path(output_path)
    _write_json(destination, value)
    _append_jsonl(
        "logs/agent_events.jsonl",
        {
            "timestamp": _timestamp(),
            "agent": "experiment-planner",
            "action": "allocate_assay_budget",
            "run_id": run_id,
            "round": round_number,
            "output": str(destination),
            "allocation": value["allocation"],
            "status": "success",
        },
    )
    return {"artifact": str(destination), "allocation": value["allocation"], "status": "saved"}


def record_critic_to_planner_handoff(
    run_id: str,
    planner_round: int,
    critic_report_path: str,
    handoff_log_path: str = "logs/omnigent_handoffs.jsonl",
) -> dict[str, Any]:
    """Validate critic clearance and record the required visible Omnigent handoff."""
    critic = _load_structured(critic_report_path)
    status = str(critic.get("status", critic.get("leakage_check", ""))).upper()
    if status in {"BLOCK", "FAIL"} or str(critic.get("leakage_check", "pass")).lower() == "fail":
        raise ValueError("critic blocked the next experimental round")
    if str(critic.get("fairness_check", "pass")).lower() == "fail":
        raise ValueError("critic reported a baseline-fairness failure")
    if status not in {"PASS", "WARN", "RETAIN", "MODIFY", "MAJOR_REVISION"}:
        raise ValueError("critic report does not contain a recognized clearance status")
    if critic.get("run_id") not in {None, run_id}:
        raise ValueError("critic report belongs to a different run")
    if int(critic.get("round", planner_round - 1)) != planner_round - 1:
        raise ValueError("critic report must review the immediately preceding round")
    handoff = {
        "handoff_id": f"HO-{run_id}-r{planner_round:02d}",
        "timestamp": _timestamp(),
        "from_agent": "scientific-critic",
        "to_agent": "experiment-planner",
        "run_id": run_id,
        "round": planner_round,
        "request": "Allocate the next 24 assays using the critic's evidence and frozen action space.",
        "artifacts": [critic_report_path],
        "status": "ready",
    }
    _append_jsonl(handoff_log_path, handoff)
    return handoff


def execute_planner_round(
    run_id: str,
    round_number: int,
    planner_decision_path: str,
    candidate_pools_path: str,
    critic_report_path: str,
    run_dir: str,
) -> dict[str, Any]:
    """Validate an Omnigent plan and perform the next budgeted lab call.

    A post-initialization measurement is refused without a non-blocking critic
    report and an explicit 24-slot planner decision.
    """
    if round_number not in {2, 3, 4}:
        raise ValueError("adaptive planner rounds must be 2, 3, or 4")
    record_critic_to_planner_handoff(run_id, round_number, critic_report_path)
    # The protocol function expects the run root and creates round_XX itself.
    # Normalize a common agent mistake so results never land in
    # round_XX/round_XX and the canonical assay ledger remains complete.
    normalized_run_dir = Path(run_dir)
    if normalized_run_dir.name == f"round_{round_number:02d}":
        normalized_run_dir = normalized_run_dir.parent
    client = _client()
    observations = client.observations(run_id)
    decision = _load_structured(planner_decision_path)
    pools = _load_structured(candidate_pools_path)
    _validate_planner_decision(decision, (item["sequence"] for item in observations))
    selected_sequences = {item["sequence"] for item in decision["selected_sequences"]}
    fallbacks = [
        item
        for action in decision["allocation"]
        for item in pools.get(action, [])
        if item["sequence"] not in selected_sequences
    ]
    result = _execute_source_preserving_allocation(
        client,
        run_id,
        round_number,
        decision,
        fallbacks,
        normalized_run_dir,
    )
    _append_jsonl(
        "logs/tool_calls.jsonl",
        {
            "timestamp": _timestamp(),
            "tool": "execute_planner_round",
            "run_id": run_id,
            "round": round_number,
            "planner_decision": planner_decision_path,
            "critic_report": critic_report_path,
            "measurements_returned": result["assays_successful"],
        },
    )
    return result
