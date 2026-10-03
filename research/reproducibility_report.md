# Reproducibility Audit

## Passing

- Protocol constants are centralized and tested.
- The raw oracle is excluded by repository policy and rejected if configured under the agent-readable root.
- Virtual-lab budget state is transactional and restart-safe.
- Seeds, candidate order, source metadata, model settings, proposals, rejections, and measurements have artifact schemas.
- CPU-only dependencies are declared in `pyproject.toml`.
- Unit, integration, 160,000-candidate surrogate, and four-round fixed-mixture fixture tests exist.
- Confirmatory execution is approval-gated.

## Pending external inputs

- No Git repository/commit metadata is available in the supplied directory.
- Private GB1 dataset provenance/checksum and real dataset audit are missing.
- Databricks workspace credentials and Omnigent session validation are missing.
- Confirmatory protocol approval is missing.
- No real run logs, statistics, figures, or Omnigent trace exist yet.

