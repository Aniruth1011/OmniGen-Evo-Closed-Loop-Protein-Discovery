---
name: bootstrap-project
description: "Create the reproducible repository structure and initialize research state before experiments. Use this skill when executing the bootstrap project stage of the OmniEvo project under Databricks Omnigent."
---

# bootstrap-project

## Goal
Create the reproducible repository structure and initialize research state before experiments.

## Inputs
- repository root,
- problem statement,
- challenge brief,
- dataset location metadata,
- Omnigent runtime context.

## Procedure
1. Read `AGENTS.md`.
2. Verify this is an Omnigent-run session.
3. Create `research/`, `runs/`, `logs/`, and `artifacts/` if absent.
4. Initialize `research/project_state.yaml`.
5. Record git commit, Python version, machine information, and Omnigent mode.
6. Record whether execution is managed Databricks Sandbox or local host.
7. Do not touch hidden fitness data.

## Outputs
- `research/project_state.yaml`
- `research/plan.md`
- `logs/run_index.csv`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
