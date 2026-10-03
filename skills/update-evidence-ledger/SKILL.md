---
name: update-evidence-ledger
description: "Maintain cumulative scientific evidence without overstating single-run observations. Use this skill when executing the update evidence ledger stage of the OmniEvo project under Databricks Omnigent."
---

# update-evidence-ledger

## Goal
Maintain cumulative scientific evidence without overstating single-run observations.

## Entry fields
```text
evidence_id
scope
run_id
round
observation
supports
weakens
confidence
limitations
artifact_paths
```

## Rule
Label single-run evidence as preliminary.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
