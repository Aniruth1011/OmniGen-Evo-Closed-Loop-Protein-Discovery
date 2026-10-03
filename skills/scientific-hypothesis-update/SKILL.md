---
name: scientific-hypothesis-update
description: "Turn round results into explicit scientific hypotheses rather than ad hoc strategy changes. Use this skill when executing the scientific hypothesis update stage of the OmniEvo project under Databricks Omnigent."
---

# scientific-hypothesis-update

## Goal
Turn round results into explicit scientific hypotheses rather than ad hoc strategy changes.

## Template
```yaml
observation: ...
mechanism_hypothesis: ...
alternative_explanation: ...
prediction: ...
falsifier: ...
next_discriminating_test: ...
strategy_implication: ...
```

## Rule
One round may justify a local strategy update but not a project-level scientific conclusion.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
