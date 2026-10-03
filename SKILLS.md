# SKILLS.md — OmniEvo Research Skill Catalog

This file is the master map for reusable scientific workflows used by the Omnigent agent system. Native Omnigent skills should live under `skills/<name>/SKILL.md`; this file documents how they fit together and what outputs each skill must create.

The project is:

> **Adaptive Agentic Directed Evolution on the GB1 Protein Fitness Landscape Under a 96-Assay Budget**

The skills are deliberately narrow, auditable, and composable. Use deterministic code/tools for calculations and model fitting. Use agents for scientific interpretation, planning, critique, and evidence-driven adaptation.

---

# 1. `bootstrap-project`

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

# 2. `omnigent-orchestration`

## Goal
Ensure Databricks Omnigent is the actual scientific orchestration layer.

## Procedure
1. Keep the Scientific Director as the root agent.
2. Delegate to specialist sub-agents through Omnigent.
3. Require structured handoff outputs.
4. Keep tool boundaries explicit.
5. Use Omnigent policies to constrain risky or excessive tool use where appropriate.
6. Maintain one persistent session per major research run or one clearly indexed session tree.
7. Preserve handoff traces for the demo.
8. Do not replace the agent loop with a hidden end-to-end Python optimizer.

## Success criterion
A reviewer can inspect the Omnigent session and identify:

```text
result → critic → planner → changed round plan → lab measurement
```

---

# 3. `databricks-omnigent-runbook`

## Goal
Run the project correctly on Databricks Omnigent.

## Managed path
1. Open `<workspace-url>/omnigent`.
2. Start a new session.
3. Prefer Databricks Sandbox when available.
4. Load/register the OmniEvo agent image.
5. Confirm model access is routed through the workspace-managed path.
6. Confirm project files are mounted or checked out.
7. Confirm hidden GB1 oracle is exposed only through the lab tool/service.
8. Run a smoke-test assay with a known allowed test fixture, not the real hidden dataset if that would leak.

## Local M5 path
1. Run the Omnigent host on the Mac.
2. Use the same agent image.
3. Keep raw oracle data outside the agent-readable working tree.
4. Connect to the managed Omnigent server if using the Databricks-managed control plane.

## Warning
Do not assume custom Python policies are available on managed Databricks Omnigent. Prefer built-ins or supported CEL policies.

---

# 4. `literature-survey`

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

# 5. `dataset-audit`

## Goal
Verify dataset integrity without leaking hidden fitness to the scientific planner.

## Procedure
Use a data steward or offline setup script with private oracle access to verify:

- expected row count,
- sequence format,
- duplicate handling,
- missing sequence count,
- wild-type sequence/value,
- fitness column parsing,
- dataset checksum,
- no accidental zero-filling of missing variants.

## Output
`research/dataset_audit.md`

## Important
Return only integrity facts needed for setup. Do not expose candidate fitness values or the identity of the global optimum to the planner.

---

# 6. `virtual-lab-audit`

## Goal
Validate that the GB1 CSV behaves like a hidden laboratory oracle.

## Checks
- agent cannot directly read the raw dataset,
- only the measurement tool can reveal new fitness,
- 24 successful assays max per round,
- 96 successful assays max per run,
- duplicate assays are rejected or handled consistently,
- unavailable variants return `UNAVAILABLE`, not zero,
- every successful assay is appended to an immutable ledger,
- budget survives process restarts,
- run IDs are isolated.

## Output
`research/virtual_lab_audit.md`

## Gate
No scientific run begins until this skill passes.

---

# 7. `baseline-protocol`

## Goal
Freeze a fair baseline suite.

## Required baselines
1. Random Search.
2. Budget-Matched Greedy Local Directed Evolution.
3. Fixed Exploitation.
4. Fixed Uncertainty/UCB.
5. Fixed Mixture Control.

## Primary fairness constraint
Adaptive and Fixed Mixture must share:

- initial data,
- surrogate model,
- sequence encoding,
- candidate primitives,
- assay budget,
- seed pairing.

## Output
`research/baseline_protocol.md`

---

# 8. `initialize-run`

## Goal
Create one fair paired run.

## Procedure
1. Set seed.
2. Create run ID.
3. Generate common initial 24 candidates using the preregistered rule.
4. Send through virtual lab.
5. Store results once.
6. Fork the same observed initial dataset to every strategy in the pair/set.
7. Initialize per-strategy ledgers.

## Output
`runs/<strategy>/seed_<n>/round_01/*`

---

# 9. `fit-surrogate`

## Goal
Fit a reproducible sequence-to-fitness model using observed assays only.

## Primary model
`ExtraTreesRegressor` unless preregistration says otherwise.

## Primary encoding
80-dimensional one-hot encoding of 4 positions × 20 amino acids.

## Procedure
1. Load only observed assay pairs.
2. Encode sequences.
3. Fit model with fixed seed.
4. Compute diagnostics on observed data using small-data-aware cross-validation where possible.
5. Save model and diagnostics.
6. Produce predictions for theoretical unseen candidates without using hidden fitness.
7. Derive uncertainty proxy from tree-ensemble variance if used.

## Outputs
- model artifact,
- `surrogate_report.json`,
- candidate score table.

## Prohibition
Do not evaluate surrogate against the entire hidden landscape during an active run.

---

# 10. `generate-exploitation-pool`

## Goal
Create candidates likely to have high fitness according to the current surrogate.

## Procedure
1. exclude measured sequences,
2. score theoretical candidates,
3. rank by predicted fitness,
4. optionally apply a fixed minimum-distance filter to avoid redundant near-duplicates,
5. return a pool larger than requested assay allocation.

## Output schema
```yaml
pool_name: exploit_model
method: predicted_mean
n_candidates: ...
seed: ...
path: ...
```

---

# 11. `generate-uncertainty-pool`

## Goal
Create candidates expected to reduce model uncertainty.

## Procedure
1. compute uncertainty proxy,
2. remove measured sequences,
3. rank by uncertainty,
4. optionally remove extreme duplicates,
5. return candidate pool.

## Caution
High uncertainty is not automatically useful. The Critic must evaluate whether the pool provided information or simply sampled poor sequences.

---

# 12. `generate-diversity-pool`

## Goal
Explore under-sampled sequence regions.

## Possible methods
- maximum Hamming distance from observed set,
- farthest-point traversal,
- underrepresented residue combinations,
- diversity in one-hot feature space.

## Rule
Freeze the method for confirmatory runs.

---

# 13. `generate-local-pool`

## Goal
Generate directed-evolution candidates near the current best measured variants.

## Procedure
1. identify current best sequence(s),
2. enumerate unseen Hamming-1 neighbors,
3. optionally include Hamming-2 only if protocol allows,
4. return a candidate pool with distance metadata,
5. never use hidden fitness for ranking.

---

# 14. `generate-random-pool`

## Goal
Create a seeded random candidate pool for random search or planner diversification.

## Rule
Random selection must be reproducible and exclude measured sequences.

---

# 15. `scientific-hypothesis-update`

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

# 16. `allocate-assay-budget`

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

# 17. `deduplicate-candidate-pools`

## Goal
Resolve overlap between exploitation, uncertainty, diversity, and local candidate pools before assays are spent.

## Procedure
1. merge selected candidates,
2. preserve source-priority and source attribution,
3. remove already measured sequences,
4. resolve duplicate nominations deterministically,
5. refill from the same source first unless planner specifies otherwise,
6. produce exactly 24 candidate proposals before virtual-lab availability rejections.

---

# 18. `run-assay-round`

## Goal
Execute one 24-assay round through the hidden virtual lab.

## Procedure
1. validate run and round IDs,
2. submit selected candidates,
3. handle unavailable variants,
4. refill rejected slots using planner-approved fallback rules,
5. stop when 24 new valid measurements are obtained,
6. write assay ledger,
7. return only measured values and rejection metadata.

## Output
`measurements.csv`

---

# 19. `critic-round-review`

## Goal
Evaluate whether the previous strategy worked and whether the next strategy should change.

## Required checks
- best-fitness improvement,
- yield by candidate source,
- surrogate error on newly revealed points,
- uncertainty usefulness,
- redundancy,
- local-search stagnation,
- leakage,
- budget compliance,
- fairness relative to baselines,
- whether policy change is justified.

## Output
`critic_report.yaml`

## Blocking rule
Leakage failure blocks continuation.

---

# 20. `update-evidence-ledger`

## Goal
Maintain cumulative scientific evidence without overstating single-run observations.

## Entry fields
```text
evidence_id
scope
run_id
round
observation
supports
weakens
confidence
limitations
artifact_paths
```

## Rule
Label single-run evidence as preliminary.

---

# 21. `run-fixed-baseline`

## Goal
Execute one baseline with the exact same accounting rules.

## Requirements
- same common initialization,
- same assay budget,
- same unavailable-candidate handling,
- same seed pairing,
- same surrogate and encoding for model-based baselines.

## Output
Identical run schema to adaptive strategy for easy comparison.

---

# 22. `run-repeated-benchmark`

## Goal
Run paired adaptive and baseline experiments over many seeds.

## Procedure
1. load frozen confirmatory config,
2. loop over confirmatory seeds,
3. create common initialization per seed,
4. run all strategies,
5. store all raw results,
6. never change hyperparameters based on partial confirmatory outcomes.

## Target
30–100 paired seeds depending on time.

---

# 23. `analyze-sample-efficiency`

## Goal
Quantify how quickly each method discovers strong variants.

## Metrics
- best fitness after 24/48/72/96 assays,
- area under best-so-far curve,
- assay count to threshold,
- top-1% and top-0.1% hit rates,
- normalized regret computed offline after runs finish.

## Outputs
- aggregate CSV,
- plot-ready tables,
- analysis memo.

---

# 24. `analyze-agent-value`

## Goal
Test the core hypothesis that adaptivity adds value beyond the surrogate model.

## Primary contrast
```text
Adaptive planner
vs
Fixed mixture
```

## Must hold constant
- surrogate,
- features,
- initialization,
- candidate primitives,
- total budget.

## Additional analyses
- compare with and without critic,
- compare allocation changes to next-round outcomes,
- measure which strategy changes were beneficial.

---

# 25. `statistical-review`

## Goal
Produce defensible repeated-run statistics.

## Procedure
1. verify paired seeds,
2. summarize mean, median, IQR/SD,
3. compute 95% confidence intervals,
4. compute paired differences,
5. perform paired bootstrap,
6. optionally run Wilcoxon signed-rank sensitivity analysis,
7. inspect outlier seeds,
8. report both wins and losses.

## Rule
Do not declare superiority from a single run or only from a p-value.

---

# 26. `preregister-confirmatory-run`

## Goal
Freeze the final experiment before confirmatory execution.

## Must freeze
- primary endpoint,
- primary contrast,
- confirmatory seed list,
- baseline definitions,
- surrogate,
- encoding,
- fixed-mixture allocation,
- initialization rule,
- adaptive action space,
- round count and budget,
- statistics plan.

## Output
`research/preregistration.md`

---

# 27. `leakage-audit`

## Goal
Prove that unmeasured fitness did not influence selection.

## Checks
- agent filesystem access,
- tool interfaces,
- logs for accidental full-dataset reads,
- candidate tables for hidden labels,
- offline evaluator isolation,
- global optimum not present in planner context,
- no post-hoc availability list exposed.

## Failure action
Mark run invalid and rerun from clean state.

---

# 28. `reproducibility-audit`

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

# 29. `m5-compute-plan`

## Goal
Keep the project fast and reliable on Apple M5.

## Rules
- avoid CUDA-only dependencies,
- use sklearn primary models,
- precompute 160k sequence encodings once,
- vectorize scoring,
- cache candidate metadata,
- parallelize seed-level runs only after deterministic single-run validation,
- prefer CPU-friendly uncertainty proxies,
- avoid deep protein model fine-tuning.

## Escalation
If local runtime becomes a bottleneck, move execution to Databricks Sandbox without changing the Omnigent agent protocol.

---

# 30. `failure-recovery`

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

# 31. `visualize-discovery`

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

# 32. `build-demo`

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

# 33. `final-claim-writing`

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

# 34. `final-project-gate`

## Goal
Prevent an incomplete but visually polished project from being presented as finished.

## Pass conditions
- literature survey complete,
- hidden oracle audited,
- baselines fair,
- adaptive-vs-fixed ablation complete,
- repeated confirmatory runs complete,
- statistics complete,
- reproducibility audit complete,
- Omnigent orchestration visible,
- demo assets generated,
- final claim reviewed by Critic.

If any primary gate fails, state the limitation explicitly in the final presentation.

---

# Recommended skill invocation order

```text
bootstrap-project
        ↓
omnigent-orchestration
        ↓
literature-survey
        ↓
dataset-audit
        ↓
virtual-lab-audit
        ↓
baseline-protocol
        ↓
initialize-run
        ↓
fit-surrogate
        ↓
(generate exploitation / uncertainty / diversity / local pools in parallel)
        ↓
scientific-hypothesis-update
        ↓
allocate-assay-budget
        ↓
deduplicate-candidate-pools
        ↓
run-assay-round
        ↓
critic-round-review
        ↓
update-evidence-ledger
        ↓
repeat rounds
        ↓
preregister-confirmatory-run
        ↓
run-repeated-benchmark
        ↓
analyze-sample-efficiency
        ↓
analyze-agent-value
        ↓
statistical-review
        ↓
leakage-audit
        ↓
reproducibility-audit
        ↓
visualize-discovery
        ↓
build-demo
        ↓
final-claim-writing
        ↓
final-project-gate
```

