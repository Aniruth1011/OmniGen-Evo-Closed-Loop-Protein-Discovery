from omnigent_client import tool
from omnievo.omnigent_tools_core import prepare_critic_input as _impl

@tool(strict=False)
def prepare_critic_input(run_id: str, round_number: int, output_path: str):
    """Create an observed-data-only diagnostic packet."""
    return _impl(run_id, round_number, output_path)
