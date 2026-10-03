---
name: visualize-discovery
description: "Create figures that make the science and Omnigent adaptation immediately understandable. Use this skill when executing the visualize discovery stage of the OmniEvo project under Databricks Omnigent."
---

# visualize-discovery

## Goal
Create figures that make the science and Omnigent adaptation immediately understandable.

## Required figures
1. best fitness vs assay count,
2. terminal best-fitness distribution,
3. top-1% hit rate,
4. round-by-round adaptive allocation,
5. acquisition-source yield,
6. optional residue combination heatmap or sequence-space projection.

## Visual honesty
- label representative runs,
- distinguish development from confirmation,
- show uncertainty/error bars,
- do not hide failed seeds.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
