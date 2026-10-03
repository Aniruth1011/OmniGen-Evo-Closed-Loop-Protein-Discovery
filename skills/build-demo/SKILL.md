---
name: build-demo
description: "Create a two-minute demonstration centered on Omnigent-driven scientific adaptation. Use this skill when executing the build demo stage of the OmniEvo project under Databricks Omnigent."
---

# build-demo

## Goal
Create a two-minute demonstration centered on Omnigent-driven scientific adaptation.

## Demo sequence
1. show 96-assay constraint,
2. show hidden lab boundary,
3. show Round N results,
4. show Critic diagnosis,
5. show Planner change in allocation,
6. submit next 24 variants,
7. show improved or changed outcome,
8. show aggregate benchmark.

## Required Omnigent evidence
Capture:

- root session,
- sub-agent calls,
- structured planner output,
- tool call to virtual lab,
- critic-to-planner handoff.

Do not reduce Omnigent to a logo or a single wrapper call.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
