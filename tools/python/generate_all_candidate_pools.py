from omnigent_client import tool
from omnievo.omnigent_tools_core import generate_all_candidate_pools as _impl

@tool(strict=False)
def generate_all_candidate_pools(run_id: str, round_number: int, seed: int, candidate_scores_path: str, output_path: str, pool_size: int = 128):
    """Generate shared acquisition pools without hidden labels."""
    return _impl(run_id, round_number, seed, candidate_scores_path, output_path, pool_size)
