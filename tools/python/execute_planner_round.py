from omnigent_client import tool
from omnievo.omnigent_tools_core import execute_planner_round as _impl

@tool(strict=False)
def execute_planner_round(run_id: str, round_number: int, planner_decision_path: str, candidate_pools_path: str, critic_report_path: str, run_dir: str):
    """Execute one validated post-initialization 24-assay round."""
    return _impl(run_id, round_number, planner_decision_path, candidate_pools_path, critic_report_path, run_dir)
