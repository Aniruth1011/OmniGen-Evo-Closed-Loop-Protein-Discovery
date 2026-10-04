from omnigent_client import tool
from omnievo.omnigent_tools_core import initialize_adaptive_run as _impl

@tool(strict=False)
def initialize_adaptive_run(run_id: str, seed: int, run_dir: str):
    """Create an adaptive run and execute only common Round 1."""
    return _impl(run_id, seed, run_dir)
