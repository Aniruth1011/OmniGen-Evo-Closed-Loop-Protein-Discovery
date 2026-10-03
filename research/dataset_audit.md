# Dataset Audit

Status: **PASS — official ProteinGym v1.3 Wu 2016 assay prepared privately**.

The raw and normalized tables are stored in the owner-only sibling directory
`../gb1_omnigent_private/`, not in this repository. The scientific agents must
not receive that directory as a mount or environment variable.

Integrity record:

- Source: ProteinGym v1.3 `SPG1_STRSG_Wu_2016.csv`.
- Official archive SHA-256: `3a83766254ac9ac9984ec25cb73c6e010ea4418f5e35f143933e6b6e6473b921`.
- Extracted source SHA-256: `d8faee338a3a53ba89b9ddc4be8dbdc244d3d2c84ddbc1ccc00ff4418ae71fcc`.
- Normalized private oracle SHA-256: `bb1c63f63500eb6843ac40ccfe0130ea368be39a4585d8fad5b99ee08b7d98f4`.
- 149,360 unique measured mutants; 160,000 theoretical sequences.
- Full-protein positions 265, 266, 267, and 280 map to GB1 positions 39, 40, 41, and 54.
- Every mutation label, residue, score, and four-site sequence passed validation.
- Wild type `VDGV` is public prior knowledge with relative fitness `1.0`; it is excluded from the paid-assay oracle and candidate generators.
- The remaining 10,639 theoretical mutants are unavailable experiments. Together with the prior-known WT, 10,640 theoretical sequences are absent from the paid-assay table.

No per-variant fitness, optimum identity, ranking, or distribution statistic is recorded here.
