---
name: dataset-audit
description: "Verify dataset integrity without leaking hidden fitness to the scientific planner. Use this skill when executing the dataset audit stage of the OmniEvo project under Databricks Omnigent."
---

# dataset-audit

## Goal
Verify dataset integrity without leaking hidden fitness to the scientific planner.

## Procedure
Use a data steward or offline setup script with private oracle access to verify:

- expected row count,
- sequence format,
- duplicate handling,
- missing sequence count,
- wild-type sequence/value,
- fitness column parsing,
- dataset checksum,
- no accidental zero-filling of missing variants.

## Output
`research/dataset_audit.md`

## Important
Return only integrity facts needed for setup. Do not expose candidate fitness values or the identity of the global optimum to the planner.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
