from typing import Any
from omnigent_client import tool
from omnievo.omnigent_tools_core import save_hypothesis_report as _impl

@tool(strict=False)
def save_hypothesis_report(run_id: str, round_number: int, report: dict[str, Any], output_path: str):
    """Validate and save the Hypothesis Scientist report."""
    return _impl(run_id, round_number, report, output_path)
