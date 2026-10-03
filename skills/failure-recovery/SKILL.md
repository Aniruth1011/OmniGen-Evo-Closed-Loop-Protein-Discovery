---
name: failure-recovery
description: "Recover from experimental or engineering failure without corrupting scientific validity. Use this skill when executing the failure recovery stage of the OmniEvo project under Databricks Omnigent."
---

# failure-recovery

## Goal
Recover from experimental or engineering failure without corrupting scientific validity.

## Cases

### Surrogate failure
Check data/encoding/target before changing models.

### Planner schema failure
Reject malformed output and re-request within the same round; do not consume assays.

### Oracle unavailable
Pause run; do not substitute synthetic fitness.

### Missing variant rejection
Refill from planner-approved fallback.

### Agent adaptivity underperforms
Preserve result; run predefined ablations rather than retuning on confirmatory seeds.

### Log corruption
Stop and reconstruct from immutable assay ledger before proceeding.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
