from omnigent_client import tool
from omnievo.omnigent_tools_core import record_critic_to_planner_handoff as _impl

@tool(strict=False)
def record_critic_to_planner_handoff(run_id: str, planner_round: int, critic_report_path: str, handoff_log_path: str = "logs/omnigent_handoffs.jsonl"):
    """Validate clearance and record the visible critic/planner handoff."""
    return _impl(run_id, planner_round, critic_report_path, handoff_log_path)
