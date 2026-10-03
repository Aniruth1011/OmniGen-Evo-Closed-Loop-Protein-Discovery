---
name: final-claim-writing
description: "Write the final scientific claim at the strength supported by evidence. Use this skill when executing the final claim writing stage of the OmniEvo project under Databricks Omnigent."
---

# final-claim-writing

## Goal
Write the final scientific claim at the strength supported by evidence.

## Template
```text
Across N paired confirmatory runs under an identical 96-assay budget, the adaptive Omnigent controller achieved [metric] compared with [baseline], with [effect size/CI]. The strongest evidence for an agentic contribution is the comparison to the fixed-mixture controller, which used the same surrogate, sequence encoding, candidate primitives, initialization, and assay budget. [State limitations].
```

## Required limitations
Consider:

- simulated retrospective laboratory,
- one protein landscape,
- four-site combinatorial library,
- possible dependence on surrogate choice,
- agent/model nondeterminism,
- no wet-lab validation performed during the project.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
