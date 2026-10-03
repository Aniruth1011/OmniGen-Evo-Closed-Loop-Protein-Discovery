# Native Omnigent Skills Index

Each folder below contains a valid `SKILL.md` entrypoint used by the OmniEvo root agent. The master behavior and invocation order are documented in the repository-level `SKILLS.md`.

## Skills

- `allocate-assay-budget`
- `analyze-agent-value`
- `analyze-sample-efficiency`
- `baseline-protocol`
- `bootstrap-project`
- `build-demo`
- `critic-round-review`
- `databricks-omnigent-runbook`
- `dataset-audit`
- `deduplicate-candidate-pools`
- `failure-recovery`
- `final-claim-writing`
- `final-project-gate`
- `fit-surrogate`
- `generate-diversity-pool`
- `generate-exploitation-pool`
- `generate-local-pool`
- `generate-random-pool`
- `generate-uncertainty-pool`
- `initialize-run`
- `leakage-audit`
- `literature-survey`
- `m5-compute-plan`
- `omnigent-orchestration`
- `preregister-confirmatory-run`
- `reproducibility-audit`
- `run-assay-round`
- `run-fixed-baseline`
- `run-repeated-benchmark`
- `scientific-hypothesis-update`
- `statistical-review`
- `update-evidence-ledger`
- `virtual-lab-audit`
- `visualize-discovery`

## Orchestration rule

Use Databricks Omnigent to select and compose these skills during the scientific workflow. Do not run all skills eagerly. Load only the skill needed for the current stage, preserve the hidden-oracle boundary, and write every required artifact before moving to the next stage.
