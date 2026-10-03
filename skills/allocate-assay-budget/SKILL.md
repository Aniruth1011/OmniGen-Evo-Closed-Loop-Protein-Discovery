---
name: allocate-assay-budget
description: "Choose how the next 24 assays are divided among acquisition primitives. Use this skill when executing the allocate assay budget stage of the OmniEvo project under Databricks Omnigent."
---

# allocate-assay-budget

## Goal
Choose how the next 24 assays are divided among acquisition primitives.

## Inputs
- observed history,
- current best fitness,
- surrogate report,
- specialist candidate-pool summaries,
- critic report,
- hypotheses,
- remaining budget.

## Required reasoning table
```text
Action | expected gain | information gain | redundancy | risk | slots
```

## Constraints
- slots sum to 24,
- no measured sequence repeated,
- no hidden fitness,
- every change from the previous allocation has an evidence-based reason,
- final decision stored in YAML.

## Output
`planner_decision.yaml`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
