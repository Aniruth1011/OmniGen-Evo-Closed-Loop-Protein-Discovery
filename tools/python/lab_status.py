from omnigent_client import tool
from omnievo.omnigent_tools_core import lab_status as _impl

@tool(strict=False)
def lab_status(run_id: str):
    """Return authoritative assay counts and remaining budget."""
    return _impl(run_id)
