---
name: preregister-confirmatory-run
description: "Freeze the final experiment before confirmatory execution. Use this skill when executing the preregister confirmatory run stage of the OmniEvo project under Databricks Omnigent."
---

# preregister-confirmatory-run

## Goal
Freeze the final experiment before confirmatory execution.

## Must freeze
- primary endpoint,
- primary contrast,
- confirmatory seed list,
- baseline definitions,
- surrogate,
- encoding,
- fixed-mixture allocation,
- initialization rule,
- adaptive action space,
- round count and budget,
- statistics plan.

## Output
`research/preregistration.md`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
