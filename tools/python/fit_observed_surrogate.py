from omnigent_client import tool
from omnievo.omnigent_tools_core import fit_observed_surrogate as _impl

@tool(strict=False)
def fit_observed_surrogate(run_id: str, round_number: int, seed: int, round_dir: str):
    """Fit the preregistered surrogate using observed data only."""
    return _impl(run_id, round_number, seed, round_dir)
