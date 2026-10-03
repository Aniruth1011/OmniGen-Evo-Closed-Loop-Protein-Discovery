---
name: reproducibility-audit
description: "Verify another researcher can rerun the experiment. Use this skill when executing the reproducibility audit stage of the OmniEvo project under Databricks Omnigent."
---

# reproducibility-audit

## Goal
Verify another researcher can rerun the experiment.

## Checklist
- exact commit,
- environment file,
- dependencies,
- dataset provenance/checksum,
- seed lists,
- run configs,
- raw assay ledgers,
- baseline configs,
- analysis scripts,
- final plot scripts,
- clear one-command or few-command run instructions.

## Output
`research/reproducibility_report.md`

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
