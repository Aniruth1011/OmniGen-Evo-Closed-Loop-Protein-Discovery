from typing import Any
from omnigent_client import tool
from omnievo.omnigent_tools_core import save_planner_decision as _impl

@tool(strict=False)
def save_planner_decision(run_id: str, round_number: int, decision: dict[str, Any], output_path: str):
    """Validate and save an exact 24-slot planner decision."""
    return _impl(run_id, round_number, decision, output_path)
