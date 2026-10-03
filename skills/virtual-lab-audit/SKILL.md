---
name: virtual-lab-audit
description: "Validate that the GB1 CSV behaves like a hidden laboratory oracle. Use this skill when executing the virtual lab audit stage of the OmniEvo project under Databricks Omnigent."
---

# virtual-lab-audit

## Goal
Validate that the GB1 CSV behaves like a hidden laboratory oracle.

## Checks
- agent cannot directly read the raw dataset,
- only the measurement tool can reveal new fitness,
- 24 successful assays max per round,
- 96 successful assays max per run,
- duplicate assays are rejected or handled consistently,
- unavailable variants return `UNAVAILABLE`, not zero,
- every successful assay is appended to an immutable ledger,
- budget survives process restarts,
- run IDs are isolated.

## Output
`research/virtual_lab_audit.md`

## Gate
No scientific run begins until this skill passes.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
