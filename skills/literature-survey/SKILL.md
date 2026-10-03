---
name: literature-survey
description: "Establish scientific context and novelty risk before claims are made. Use this skill when executing the literature survey stage of the OmniEvo project under Databricks Omnigent."
---

# literature-survey

## Goal
Establish scientific context and novelty risk before claims are made.

## Search clusters
- GB1 fitness landscape / Wu et al. 2016,
- ML-assisted directed evolution on GB1,
- active learning for protein engineering,
- Bayesian optimization of protein sequences,
- adaptive acquisition strategies,
- low-data surrogate modeling,
- autonomous science / agentic experiment planning,
- 2024–2026 related work.

## Procedure
1. Start from primary papers.
2. Extract dataset, budget, acquisition, evaluation, and limitations.
3. Search later papers citing the primary GB1 work.
4. Search conceptually overlapping methods, not only exact title words.
5. Record whether strategies are adaptive or fixed.
6. Record whether a paper isolates controller value from surrogate value.
7. Write a novelty-risk memo.

## Outputs
- `research/literature_matrix.csv`
- `research/novelty_memo.md`

## Quality rule
Never write "novel" solely because no identical project title exists.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
