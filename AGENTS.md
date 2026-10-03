# AGENTS.md — OmniEvo: Adaptive Agentic Directed Evolution on GB1

## 0. Purpose of this file

## Naming and platform note

The required platform is **Databricks Omnigent**. If project discussion informally says "OmniAgent," treat that as a reference to Databricks Omnigent. The final implementation and demo must use Omnigent as the visible orchestration/control plane.

**Submission-level requirement:** at least one complete discovery transition in the final demo must be traceable through Omnigent itself: specialist result -> critic/planner handoff -> changed experiment allocation -> virtual-lab tool call -> returned measurements. A Python script may implement deterministic tools, but it must not replace this orchestration loop.


This file is the operating contract for the scientific agent system that executes the project:

> **Adaptive Agentic Directed Evolution on the GB1 Protein Fitness Landscape Under a 96-Assay Budget**

The central research question is:

> **Under a fixed budget of 96 experimental measurements, can an adaptive autonomous experiment-planning agent identify extreme high-fitness GB1 variants more efficiently than random screening, budget-matched greedy directed evolution, and fixed machine-learning acquisition strategies?**

The more important mechanistic question is:

> **Does adaptive strategy selection itself add value beyond the underlying surrogate model?**

The project must be run as a scientific discovery loop, not as a one-shot optimizer and not as a scripted demo. The system must observe evidence, form or revise hypotheses, choose experiments under a budget, execute those experiments through a hidden virtual laboratory, analyze the results, and change the next experimental plan when warranted.

---

# 1. Non-negotiable platform requirement: Databricks Omnigent

## 1.1 Omnigent is the orchestrator, not a decorative wrapper

The live scientific workflow MUST be orchestrated through **Databricks Omnigent** (managed on Databricks or the open-source Omnigent stack connected to Databricks). Do not implement the core adaptive loop as a monolithic Python script and then place Omnigent only in front of it.

Omnigent must visibly own the orchestration decisions:

1. delegate specialist tasks to sub-agents,
2. collect structured outputs,
3. maintain the shared research state,
4. invoke experiment tools,
5. enforce the hidden-oracle boundary,
6. choose or approve the next round strategy,
7. trigger critique after each round,
8. update the experiment plan when evidence changes,
9. preserve a trace that can be shown in the final demo.

The demo should make it obvious that the same research workflow would be harder to coordinate manually.

## 1.2 Use Omnigent-native structure

Prefer a native agent image:

```text
omnievo/
├── config.yaml
├── AGENTS.md
├── SKILLS.md
├── skills/
│   └── <skill>/SKILL.md
├── agents/
│   └── <specialist>/
│       ├── config.yaml
│       └── AGENTS.md
├── tools/
│   └── ...
└── references/
```

Omnigent should be configured with:

- a root scientific director agent,
- specialist sub-agents,
- reusable skills,
- explicit tool boundaries,
- contextual policies where useful,
- a sandbox or host that does NOT expose the hidden GB1 oracle directly to the agent.

## 1.3 Databricks-specific usage

When using managed Omnigent on Databricks:

- use the Databricks workspace Omnigent session as the primary visible control plane,
- use Databricks Sandbox when available for reproducible execution,
- route model access through the Databricks-managed model path / Unity Gateway when running in Databricks Sandbox,
- keep project artifacts, logs, and experiment outputs inside the project workspace or mounted project directory,
- prefer built-in contextual policies or CEL policies supported by the managed environment,
- do not rely on custom Python policies if running on managed Databricks Omnigent where they are unsupported.

If running the Omnigent host on the local M5 Mac, retain the exact same agent image and skills so the orchestration layer remains portable.

---

# 2. Scientific system definition

## 2.1 Biological system

The system studies the GB1 protein fitness landscape at four interacting positions:

- position 39,
- position 40,
- position 41,
- position 54.

Each position can take one of 20 amino acids, producing a theoretical sequence space of:

```text
20^4 = 160,000 variants
```

The experimentally characterized landscape contains fitness measurements for approximately 149,361 variants. Missing variants are **unavailable experiments**, not zero-fitness examples.

The wild-type genotype and wild-type fitness are allowed initial knowledge.

## 2.2 Experimental budget

Each run has a strict budget of:

```text
96 assays total
```

Use:

```text
4 rounds × 24 assays = 96 measurements
```

After every round, the system receives the 24 returned measurements and may revise the next strategy.

No unused budget may be silently reclaimed after the run ends. If fewer than 24 valid variants are measured in a round because some proposed variants are unavailable, the planner may refill within the same round until 24 valid measurements are obtained, subject to tool rules.

## 2.3 Hidden virtual laboratory

The complete GB1 table is a hidden experimental oracle.

The scientific agents MUST NOT have direct read access to:

- the complete sequence-fitness table,
- the fitness of any untested sequence,
- the global optimum sequence,
- the ranking of variants,
- the complete distribution of fitness,
- precomputed labels such as top-1% membership for candidates.

The only sanctioned path to a new fitness value is the virtual laboratory interface, conceptually:

```python
lab.measure(sequence)
```

or a budget-controlled batch form such as:

```python
lab.measure_batch(run_id, round_id, sequences)
```

The laboratory may internally look up the hidden dataset. The agent may not.

## 2.4 Initial knowledge

All methods may begin with the same information:

- mutable positions,
- amino-acid alphabet,
- wild-type genotype,
- wild-type fitness,
- 96-assay total budget,
- 24-assay round size,
- sequence length of four residues at the mutable sites,
- general published biological context if supplied equally to all compared methods.

The wild-type reference value is prior knowledge and does not consume one of the 96 simulated assays unless the final experiment protocol explicitly chooses otherwise. Freeze this convention before experiments begin.

---

# 3. Primary scientific claim to test

The project must NOT merely demonstrate that machine learning can guide directed evolution. That is already established in prior GB1 work.

The project must test:

> **Whether an adaptive experiment-planning agent that changes the mixture of exploration, exploitation, diversity search, uncertainty search, and local mutation after observing experimental evidence improves search efficiency under the same 96-assay budget.**

The cleanest causal comparison is:

```text
Adaptive Omnigent strategy controller
vs.
Fixed strategy controller
```

while holding constant as much as possible:

- surrogate model family,
- feature representation,
- initial observations,
- candidate universe,
- round size,
- total assay budget,
- random seed pairing,
- access to prior biological knowledge.

If the adaptive controller uses a stronger model, larger initialization, privileged information, or more assays than the fixed baselines, the experiment does NOT isolate the agentic contribution.

---

# 4. Primary hypotheses

Maintain hypotheses in `research/hypotheses.yaml` with status values:

```text
PROPOSED
SUPPORTED
WEAKENED
REJECTED
UNRESOLVED
```

## H1 — adaptive policy advantage

> An adaptive controller that changes search strategy after each round achieves higher best-observed fitness after 96 assays than a fixed strategy using the same surrogate model and candidate primitives.

### Prediction
Across paired randomized runs, adaptive search has a higher distribution of terminal best fitness than the fixed-mixture control.

### Falsifier
No reliable paired improvement is observed, or the apparent advantage disappears when surrogate model, initialization, and random seeds are controlled.

---

## H2 — adaptive value is state-dependent

> No single acquisition primitive is optimal across all rounds; useful search behavior changes as evidence accumulates.

### Prediction
Successful adaptive runs alter allocation among exploration, exploitation, uncertainty, and local search in response to observed outcomes.

### Falsifier
The learned policy converges immediately to one static allocation and that static allocation performs equivalently across seeds.

---

## H3 — epistasis penalizes naive local greed

> A budget-matched single-mutation local walk is more likely to stall at suboptimal local regions than a strategy that occasionally explores distant sequence regions.

### Prediction
Adaptive or diversity-aware search has a higher probability of escaping low-fitness local basins and discovering extreme variants.

### Falsifier
Local greedy search matches or exceeds adaptive strategies under the same assay budget across repeated trials.

---

## H4 — agentic adaptation adds value beyond surrogate prediction quality

> Improvement is caused by changing how assays are allocated, not simply by using a better predictive model.

### Prediction
When the same fitted surrogate and candidate scores are supplied to both adaptive and fixed policies, the adaptive allocation yields better terminal fitness or sample-efficiency metrics.

### Falsifier
Performance differences vanish under same-surrogate controls.

---

# 5. Research-quality baselines

The source problem statement is truncated during Baseline 2. Complete the benchmark suite using the following fairness-first definitions unless a literature survey provides a better canonical protocol.

## Baseline A — Random Search

- Uniformly sample unseen candidate variants.
- Same 96-assay budget.
- Same availability handling for missing variants.
- Repeat across the same paired seeds used for other methods.

Purpose: fundamental no-model reference.

## Baseline B — Budget-Matched Greedy Local Directed Evolution

- Start from the same common initialization used by all strategies.
- Maintain the best measured sequence.
- Generate unseen Hamming-distance-1 neighbors around the current best sequence.
- Select up to 24 candidates using a fixed, preregistered rule that does not inspect hidden fitness.
- After measurements, move the center to the best observed sequence if improvement occurs.
- If the neighborhood is exhausted, expand to neighbors of the next-best measured sequence using a fixed rule.

Purpose: classical local hill-climbing behavior under the same assay budget.

## Baseline C — Fixed Exploitation

- Fit the same primary surrogate used by the adaptive method.
- Rank unseen candidates by predicted mean fitness.
- Measure the top 24 every round.
- Do not alter the acquisition policy after poor results.

Purpose: isolate exploitation-only behavior.

## Baseline D — Fixed Uncertainty / UCB

- Fit the same primary surrogate.
- Use a fixed preregistered uncertainty-aware acquisition rule for all adaptive rounds.
- Example: fixed UCB coefficient, ensemble upper-confidence score, or expected improvement if the model supports calibrated uncertainty.

Purpose: compare adaptive policy selection against a conventional fixed acquisition rule.

## Baseline E — Fixed Mixture Control

This is the MOST IMPORTANT baseline for the agentic claim.

Use the same candidate primitives as the adaptive system but freeze the allocation before the run, for example:

```text
8 exploit-model
6 explore-uncertain
6 explore-diverse
4 local-mutate
= 24 assays per round
```

The exact fixed allocation must be chosen before final confirmatory experiments and must not be tuned on the final evaluation seeds.

Purpose: isolate the value of **changing strategy allocation from evidence**.

## Optional upper bound — oracle reference

The global maximum and complete landscape may be used only by an offline evaluator after a run is finished to compute regret or percentile metrics.

Do not expose oracle information to any agent during search.

---

# 6. Primary experimental protocol

## 6.1 Common initialization

For the primary fairness comparison, use a COMMON first-round initialization across all strategies within a paired seed.

Recommended:

```text
Round 1: 24 common initialization assays
Rounds 2–4: policy-controlled assays
```

A common initialization prevents one strategy from winning simply because it received a better initial sample.

Choose one initialization rule before confirmatory experiments:

- seeded uniform random, or
- seeded diversity-maximizing design over the sequence alphabet.

Use the SAME initial 24 measurements for every compared strategy for that seed.

Secondary ablation: allow the Omnigent agent to control Round 1 and report this separately.

## 6.2 Primary surrogate model

Use one simple, reproducible model as the primary surrogate.

Recommended default:

```text
ExtraTreesRegressor
```

Reasons:

- handles small nonlinear tabular datasets,
- trains quickly on an M5 Mac,
- tolerates sparse early observations,
- ensemble variance can provide a rough uncertainty proxy,
- easy to reproduce.

Alternative models may be evaluated as secondary analyses:

- Random Forest,
- Gaussian Process on appropriate encoding,
- gradient boosting,
- small MLP.

Do not change surrogate families mid-study solely because one gives a more favorable result. Any `CHANGE_SURROGATE` action must be logged, justified, and treated as a separate ablation unless the protocol explicitly allows it.

## 6.3 Sequence encoding

Use a fixed encoding shared by all model-based methods.

Primary recommended encoding:

```text
4 positions × 20 one-hot amino-acid indicators = 80 features
```

Optional secondary encodings:

- physicochemical amino-acid descriptors,
- learned protein embeddings if computationally justified.

Do not give only the adaptive method a richer representation.

## 6.4 Candidate universe

The 160,000 theoretical variants may be enumerated because the sequence space itself is allowed knowledge.

The model may score unmeasured theoretical sequences, but it must not know which sequences are absent from the measured dataset before submitting them to the virtual lab.

The virtual lab rejects unavailable candidates without assigning fitness zero.

## 6.5 Four-round loop

For each run:

### Round 1

1. generate common initialization batch,
2. measure 24 valid variants,
3. record observations,
4. fit first surrogate,
5. run critique.

### Round 2

1. Scientist analyzes Round 1,
2. modeler updates surrogate,
3. exploration/exploitation/local specialists propose candidates,
4. planner allocates exactly 24 assay slots,
5. critic checks leakage and budget,
6. virtual lab reveals 24 measurements,
7. evidence ledger is updated.

### Round 3

Repeat, but the planner MUST explicitly consider whether Round 2 evidence justifies changing allocation.

### Round 4

Repeat and spend the remaining assay budget. No post-hoc fifth round.

After Round 4, freeze the run and invoke offline evaluation.

---

# 7. Agent architecture

The system should use purposeful specialist agents rather than artificially splitting trivial steps.

## 7.1 Root agent — Scientific Director

### Owns

- scientific objective,
- research-state integrity,
- experiment ordering,
- delegation,
- approval of next-round plans,
- evidence ledger,
- final synthesis,
- demo narrative.

### Must do

1. read this file before acting,
2. inspect current project state,
3. call the literature agent before novelty claims,
4. ensure the virtual-lab boundary is active,
5. maintain the 96-assay budget,
6. delegate model fitting and candidate proposals,
7. require planner output in the defined schema,
8. call the critic after every round,
9. update hypothesis status from evidence,
10. continue to the next round unless a human approval gate or unrecoverable failure occurs.

### Must not do

- directly read the hidden GB1 table,
- fabricate measurements,
- silently alter baselines,
- optimize on final evaluation seeds,
- claim success before repeated-run statistics.

---

## 7.2 Literature Scientist

### Owns

- literature survey,
- novelty risk assessment,
- baseline identification,
- extraction of canonical GB1 experimental facts.

### Required literature clusters

Search primary sources for:

1. Wu et al. 2016 GB1 landscape,
2. Wu et al. / Biswas et al. ML-assisted directed evolution work using the GB1 landscape,
3. active learning / Bayesian optimization for protein engineering,
4. sequence-based surrogate modeling under low data,
5. autonomous laboratories / agentic experimental design,
6. adaptive acquisition policies,
7. recent 2024–2026 work that could overlap with the proposed contribution.

### Deliverable

`research/literature_matrix.csv` with columns:

```text
citation
paper_year
question
system_or_dataset
method
experimental_budget
acquisition_strategy
adaptive_or_fixed
primary_metric
main_result
limitations
relation_to_our_claim
```

and:

`research/novelty_memo.md`

### Rule

Never claim novelty merely because the exact phrase "agentic directed evolution" was not found. Compare mechanisms and experimental design.

---

## 7.3 Scientist / Hypothesis Agent

### Owns

- interpretation of observed assay results,
- hypotheses about residue preferences and epistasis,
- proposing strategy changes,
- distinguishing observation from speculation.

### Inputs

Only:

- observed sequence-fitness pairs,
- current best variants,
- surrogate summaries,
- candidate-pool summaries,
- prior public literature allowed by protocol,
- experiment history.

### Output schema

```yaml
observations:
  - ...
hypotheses:
  - id: Hx
    statement: ...
    evidence_for: ...
    evidence_against: ...
    prediction: ...
    falsifier: ...
strategy_implications:
  - ...
uncertainties:
  - ...
recommended_tests:
  - ...
```

Do not emit private chain-of-thought. Log concise scientific rationale only.

---

## 7.4 Surrogate Modeler

### Owns

- fitting the preregistered surrogate,
- cross-validated diagnostics on OBSERVED data only,
- prediction and uncertainty summaries for unseen theoretical variants,
- reproducible model artifacts.

### Must return

```yaml
model_family: ...
training_n: ...
feature_encoding: ...
seed: ...
observed_cv:
  rmse: ...
  spearman: ...
  caveat: ...
candidate_scores_path: ...
uncertainty_definition: ...
```

### Important

Any model diagnostic using the full hidden landscape is OFFLINE EVALUATION and may not be returned to the planner before the run completes.

---

## 7.5 Exploration Specialist

### Owns

Two candidate pools:

1. **uncertainty exploration** — candidates where model uncertainty is high,
2. **diversity exploration** — candidates distant from observed sequences or covering under-sampled residue combinations.

### Must return more candidates than needed

Example:

```yaml
pool_name: explore_uncertain
n_candidates: 100
candidate_file: ...
method: ensemble_std
seed: ...
```

The planner chooses how many slots to allocate; the specialist does not spend assays.

---

## 7.6 Exploitation Specialist

### Owns

- high predicted-fitness candidate pool,
- optional exploitation-with-diversity filtering to avoid near-duplicates.

### Must avoid

- hidden fitness,
- final test statistics,
- using previously measured sequences.

---

## 7.7 Local Search Specialist

### Owns

- Hamming-distance-1 and optional Hamming-distance-2 variants around the best observed sequences,
- candidate generation only,
- no direct assay execution.

### Purpose

Provide an explicit directed-evolution primitive that can be expanded or reduced by the planner.

---

## 7.8 Experiment Planner

This is the core adaptive decision agent and the most important Omnigent-visible role.

### Owns

- allocation of exactly 24 assay slots per round,
- selection among candidate primitives,
- justification of exploration versus exploitation,
- expected-value-of-information reasoning,
- budget compliance.

### Allowed action types

```text
EXPLORE_DIVERSE
EXPLORE_UNCERTAIN
EXPLOIT_MODEL
LOCAL_MUTATE
RANDOM_SAMPLE
CHANGE_SURROGATE
CHANGE_ACQUISITION
ALLOCATE_BUDGET
```

### Planning schema

```yaml
round: 3
remaining_total_budget_before_round: 48
round_budget: 24
current_best_fitness: ...
primary_observations:
  - ...
policy_change_from_previous_round: true
policy_change_reason: ...
allocation:
  EXPLOIT_MODEL: 10
  EXPLORE_UNCERTAIN: 6
  EXPLORE_DIVERSE: 4
  LOCAL_MUTATE: 4
selection_parameters:
  exploit_rank_by: predicted_mean
  uncertainty_rank_by: ensemble_std
  diversity_metric: hamming_or_feature_distance
  local_search_radius: 1
candidate_overlap_resolution: ...
expected_learning:
  - ...
risks:
  - ...
stop_conditions:
  - ...
```

Allocations must sum to 24.

### Thinking discipline

Use a compact decision table:

```text
Action | expected fitness gain | expected information gain | redundancy risk | cost | rationale
```

Do not choose a strategy because it "sounds balanced." Tie every allocation change to observed evidence.

---

## 7.9 Critic / Scientific Reviewer

### Owns

- challenge assumptions after every round,
- leakage checks,
- fairness checks,
- detection of post-hoc tuning,
- assessment of whether a strategy actually worked,
- recommendation to retain, change, or reject current hypotheses.

### Required questions after each round

1. Did the round improve best fitness?
2. Which acquisition source produced the improvements?
3. Which source wasted assay slots?
4. Did surrogate ranking quality improve or deteriorate on newly measured points?
5. Did uncertainty-selected candidates provide information or merely low fitness?
6. Are candidate pools collapsing to near-duplicates?
7. Is local search stuck near one basin?
8. Is the planner reacting to noise rather than repeated evidence?
9. Did any component receive information unavailable to baselines?
10. Should next-round allocation change?

### Output schema

```yaml
round: ...
verdict: retain|modify|major_revision
successful_components:
  - ...
failed_components:
  - ...
leakage_check: pass|fail
fairness_check: pass|fail
hypothesis_updates:
  - id: ...
    new_status: ...
recommended_policy_change:
  - ...
```

A failed leakage check blocks the next round until corrected.

---

## 7.10 Statistical Reviewer

Use primarily after repeated runs, not every candidate selection.

### Owns

- paired-run statistics,
- confidence intervals,
- effect sizes,
- robustness summaries,
- checking whether the claimed advantage is driven by a few lucky runs.

### Must distinguish

- exploratory runs,
- hyperparameter-selection runs,
- final confirmatory runs.

---

## 7.11 Demo Curator

### Owns

- selecting one representative run AFTER aggregate statistics are fixed,
- visualizing the four-round strategy changes,
- showing Omnigent sub-agent handoffs,
- showing measured sequence-fitness improvements,
- making clear that the oracle was hidden,
- avoiding cherry-picked claims.

The representative run must be labeled as a demo run, while aggregate conclusions come from all confirmatory seeds.

---

# 8. Scientific reasoning protocol

## 8.1 Use evidence-first reasoning

For each decision:

```text
OBSERVATION
↓
HYPOTHESIS
↓
COMPETING EXPLANATION
↓
DISCRIMINATING TEST
↓
RESULT
↓
BELIEF UPDATE
↓
NEXT DECISION
```

Do not skip directly from observation to intervention.

## 8.2 Falsification-first method

Every hypothesis must include:

```yaml
statement:
prediction:
falsifier:
alternative_explanations:
minimum_test:
status:
```

If a hypothesis survives only because the agent repeatedly changes definitions, mark it as weakened or rejected.

## 8.3 Value-of-information reasoning

When two actions compete for limited assays, consider:

- expected fitness gain,
- expected uncertainty reduction,
- coverage of unexplored sequence space,
- chance of escaping a local optimum,
- redundancy with already observed data,
- number of assays consumed,
- whether the result will change a later decision.

Prefer experiments that are both decision-relevant and budget-efficient.

## 8.4 Separate model uncertainty from agent uncertainty

Model uncertainty is a numeric property of the surrogate or ensemble.

Agent uncertainty is uncertainty in the scientific interpretation or strategy choice.

Do not conflate the two.

## 8.5 No hidden chain-of-thought logging

Research logs should contain concise, auditable reasons such as:

```text
Round 2 exploitation produced no improvement in 10 assays, while uncertainty sampling found two >2× WT variants; increase uncertainty allocation from 4 to 8 next round.
```

Do not store private free-form chain-of-thought.

---

# 9. Fairness rules for the agentic comparison

The main claim is invalid unless these controls hold.

## 9.1 Same assay budget

Every strategy gets exactly 96 successful measurements.

## 9.2 Same initialization

Within a paired seed, every method receives the same initial observations.

## 9.3 Same surrogate for the primary agent-value comparison

Adaptive and fixed-policy methods must share the same model family and encoding.

## 9.4 Same candidate space

No method gets privileged knowledge of missing variants or high-fitness regions.

## 9.5 Same random seeds where applicable

Use paired seeds to reduce variance.

## 9.6 No tuning on confirmatory seeds

Hyperparameters and fixed allocations are frozen before final evaluation.

## 9.7 Separate development and confirmation

Recommended protocol:

```text
Development seeds: 0–19
Confirmatory seeds: 100–149
```

Adjust counts for compute, but freeze the final confirmatory set before analyzing it.

---

# 10. Evaluation metrics

## 10.1 Primary endpoint

**Best observed fitness after 96 assays.**

Primary comparison:

```text
Adaptive Omnigent planner vs Fixed Mixture Control
```

## 10.2 Secondary endpoints

Measure:

- best fitness after 24, 48, 72, and 96 assays,
- area under the best-so-far curve,
- normalized regret to the known global maximum, computed offline only,
- probability of discovering a top-1% variant,
- probability of discovering a top-0.1% variant,
- assays needed to first exceed predefined fitness thresholds,
- number of unique high-fitness basins or residue combinations explored,
- fraction of assays by acquisition source,
- contribution of each acquisition source to improvements,
- surrogate ranking quality on newly revealed measurements.

## 10.3 Agent-specific metrics

Track:

- number of rounds where policy allocation changed,
- magnitude of allocation change,
- whether changes followed critic recommendations,
- whether changed policies improved the next round,
- proportion of assay budget assigned to each primitive,
- number of rejected / unavailable candidate proposals,
- number of planner decisions later reversed.

These demonstrate actual adaptive behavior rather than merely final performance.

---

# 11. Statistical analysis

Because the virtual experiment is cheap, repeated runs are mandatory.

## 11.1 Target number of runs

Recommended:

- minimum: 30 paired confirmatory seeds,
- preferred: 50 paired confirmatory seeds,
- stretch: 100 paired confirmatory seeds.

Use the highest count that comfortably fits the hackathon compute window.

## 11.2 Report distributions

For each strategy report:

- mean,
- median,
- standard deviation or IQR,
- 95% confidence interval,
- full seed-level results.

## 11.3 Paired comparisons

Because strategies share the same seed and initialization, use paired analyses.

Recommended:

- paired bootstrap confidence interval for terminal best-fitness difference,
- Wilcoxon signed-rank as a nonparametric sensitivity analysis,
- paired difference plots.

Do not rely only on a p-value.

## 11.4 Multiple metrics

Predeclare one primary endpoint and one primary contrast. Treat other metrics as secondary to avoid accidental cherry-picking.

---

# 12. Required ablations

## Ablation 1 — adaptivity vs fixed allocation

Same surrogate + same primitives + same initial data.

Only difference:

```text
adaptive round-by-round allocation
vs
frozen allocation
```

This is essential.

## Ablation 2 — remove critic

Run adaptive planner with and without the critic feedback step.

Purpose: test whether structured post-round reflection adds measurable value.

## Ablation 3 — remove uncertainty exploration

Test whether the adaptive method needs uncertainty sampling or primarily benefits from diversity/local search.

## Ablation 4 — local-search-only

Quantify how much epistasis harms pure local optimization under the strict budget.

## Optional Ablation 5 — agent chooses sequence identities directly

Compare:

- agent chooses only strategy allocation while deterministic tools rank sequences,
- agent manually nominates individual sequences.

Primary project SHOULD favor the first design because it is more reproducible and isolates orchestration quality.

---

# 13. Literature survey gate

No implementation claim such as "novel" or "first" may be used before literature review.

## Required sequence

1. retrieve Wu et al. 2016 landscape paper,
2. retrieve ML-assisted directed evolution paper using the same landscape,
3. search active learning / Bayesian optimization protein engineering,
4. search adaptive acquisition in protein sequence optimization,
5. search LLM/agent scientific experiment planning,
6. search 2024–2026 publications and preprints,
7. create literature matrix,
8. write novelty-risk memo,
9. refine the final claim.

## Novelty wording

Prefer:

> "We evaluate whether evidence-driven agentic strategy switching adds value under an extreme fixed assay budget on GB1."

Avoid:

> "This is the first autonomous directed-evolution system."

unless supported by a thorough literature review.

---

# 14. Experiment selection protocol

The planner must not improvise an unbounded search strategy.

At each adaptive round:

1. obtain candidate pools from the specialist components,
2. obtain a surrogate report,
3. obtain the scientist's hypotheses,
4. obtain the critic's previous-round assessment,
5. compare allowed actions,
6. allocate exactly 24 slots,
7. deduplicate candidates across pools,
8. record source attribution for every selected sequence,
9. send the final batch to the virtual lab,
10. log returned measurements.

## Candidate-source attribution

Every assayed sequence must carry:

```yaml
sequence: WAGF
source_action: EXPLOIT_MODEL
source_rank: 3
model_score: ...
model_uncertainty: ...
distance_to_best: ...
planner_round: 3
```

This enables post-hoc attribution of which actions actually helped.

---

# 15. Virtual-lab integrity

## 15.1 Hard separation

Store the hidden GB1 dataset outside normal agent-readable project paths.

Preferred designs:

### Managed Databricks / Sandbox

Expose the oracle through a narrow tool or service. Do not mount the raw data into the agent-readable working directory.

### Local M5 host

Run the oracle as a separate process or tool with a private data path. The Omnigent root agent receives only the function interface, not raw file access.

## 15.2 Assay ledger

Every successful measurement writes an immutable ledger entry:

```json
{
  "run_id": "adaptive_seed_104",
  "round": 2,
  "assay_index": 37,
  "sequence": "WAGF",
  "fitness": 2.31,
  "source_action": "EXPLOIT_MODEL",
  "timestamp": "..."
}
```

## 15.3 Missing variants

If a proposed sequence is absent from the experimentally measured table:

- return `UNAVAILABLE`,
- do not assign fitness zero,
- do not count it as a successful assay,
- log the rejection,
- allow the planner to refill the remaining slot,
- do not reveal any further global dataset information.

## 15.4 No oracle peeking

Any direct read of hidden fitness values before assay selection invalidates the run.

The Critic must mark:

```text
RUN_INVALID_LEAKAGE
```

and rerun from a clean seed/state.

---

# 16. Logging and research memory

Create the following structure:

```text
research/
├── project_state.yaml
├── literature_matrix.csv
├── novelty_memo.md
├── hypotheses.yaml
├── evidence_ledger.jsonl
├── decision_log.md
├── baseline_protocol.md
├── preregistration.md
└── final_research_summary.md

runs/
├── adaptive/
│   └── seed_###/
│       ├── run_manifest.yaml
│       ├── assay_ledger.jsonl
│       ├── round_01/
│       │   ├── observations.csv
│       │   ├── surrogate_report.json
│       │   ├── candidate_pools.json
│       │   ├── planner_decision.yaml
│       │   ├── measurements.csv
│       │   └── critic_report.yaml
│       ├── round_02/
│       ├── round_03/
│       └── round_04/
├── random/
├── greedy_local/
├── fixed_exploit/
├── fixed_ucb/
└── fixed_mixture/

logs/
├── omnigent_handoffs.jsonl
├── tool_calls.jsonl
├── errors.jsonl
├── approvals.md
└── run_index.csv

artifacts/
├── figures/
├── tables/
├── demo/
└── final/
```

## 16.1 Decision log format

Every round decision appends:

```markdown
## Run adaptive_seed_104 — Round 3

Evidence entering round:
- best fitness = ...
- exploit success rate = ...
- uncertainty pool yielded ...

Decision:
- exploit = 8
- uncertain = 8
- diverse = 4
- local = 4

Why this changed:
- ...

Alternative considered:
- ...

What result would reverse this decision next round:
- ...
```

## 16.2 Evidence ledger

Use structured entries:

```json
{
  "evidence_id": "E-0021",
  "run_scope": "development",
  "source": "adaptive_seed_104_round_2",
  "observation": "uncertainty pool produced 2 of 3 new >2xWT variants",
  "supports": ["H1", "H2"],
  "weakens": [],
  "confidence": "moderate",
  "limitations": "single run"
}
```

Evidence from one seed should not upgrade a project-level hypothesis to "supported" without aggregate replication.

---

# 17. Reproducibility requirements

Every run must capture:

```text
run_id
strategy
random_seed
git_commit
python_version
package_versions
dataset_checksum_or_version
hidden_oracle_checksum
initialization_sequence_ids
surrogate_model
surrogate_hyperparameters
sequence_encoding
acquisition_parameters
round allocations
all proposed candidates
all rejected unavailable candidates
all measured candidates
fitness returned by the lab
wall-clock time
model/tool errors
```

## Determinism

Where possible:

- set Python, NumPy, and sklearn seeds,
- persist candidate ordering,
- sort ties deterministically using a seeded rule,
- save exact config files,
- avoid depending on unordered set/dict behavior.

## Agent nondeterminism

Because the LLM planner may vary:

- save the complete structured planner output,
- use a strict JSON/YAML schema,
- restrict action space,
- compare multiple agent runs,
- if possible set stable model settings for confirmatory experiments.

---

# 18. M5 Mac compute strategy

This project is intentionally lightweight enough for an Apple M5 machine.

Use:

- CPU or Apple Silicon compatible Python stack,
- no CUDA dependency,
- simple sklearn surrogates,
- precomputed 160k sequence encodings,
- vectorized candidate scoring,
- cached features and candidate metadata,
- multiprocessing only when it improves throughput without reducing reproducibility.

Avoid:

- large protein language-model fine-tuning,
- large GPU-only Bayesian optimization stacks,
- unnecessarily expensive deep ensembles.

The main cost should be repeated small-model fitting and candidate ranking, which should be tractable locally.

---

# 19. Human approval gates

Human approval is required before:

1. finalizing the confirmatory baseline protocol,
2. unblinding confirmatory results,
3. changing the primary endpoint after seeing results,
4. changing the hidden-oracle implementation in a way that could leak data,
5. publishing or presenting a novelty claim stronger than the literature evidence supports.

The agent may continue routine development experiments without approval if they remain inside the predeclared development budget.

---

# 20. Failure recovery

## If the surrogate performs poorly

Do not immediately replace it with a more complex model.

First check:

1. encoding correctness,
2. training-data size,
3. duplicate sequences,
4. target scaling,
5. extreme zero/near-zero fitness distribution,
6. whether ranking, rather than RMSE, is the more relevant diagnostic.

Then run a preregistered surrogate sensitivity analysis.

## If adaptive search loses to fixed search

Do NOT hide the result.

Investigate:

- did the planner overreact to one round?
- was the action space too large?
- did fixed UCB already capture most useful adaptivity?
- did the critic improve or worsen decisions?
- was the initial sample too informative?
- is four rounds insufficient for policy adaptation?

A negative result can still be scientifically valuable if the workflow identifies why adaptivity failed.

## If random search occasionally wins

That is expected on a rugged finite landscape. Use repeated-run distributions rather than anecdotal runs.

## If the agent repeatedly proposes unavailable variants

- verify candidate generation,
- record the rejection rate,
- do not reveal the valid-set membership globally,
- allow refill while preserving budget.

---

# 21. Demo-first requirements

The end goal is a rigorous project AND a strong visual demonstration.

The demo should make five things visible:

1. **The budget constraint** — only 96 assays out of ~149k measured variants.
2. **The hidden lab** — the agent cannot see unmeasured fitness.
3. **Omnigent orchestration** — multiple specialist handoffs and a planner decision.
4. **Adaptation** — the Round 3 allocation visibly differs from Round 2 because of evidence.
5. **Scientific result** — aggregate comparison against baselines.

## 21.1 Recommended main visualization

A live or precomputed search dashboard:

```text
┌────────────────────────────────────────────────────────────────┐
│ OmniEvo — GB1 Directed Evolution                              │
├───────────────────┬────────────────────────────────────────────┤
│ Assays used       │ 72 / 96                                   │
│ Current best      │ fitness = X.XX                             │
│ Wild type         │ 1.00                                      │
├───────────────────┼────────────────────────────────────────────┤
│ Round allocation  │ Exploit 8 | Uncertain 8 | Diverse 4 | Local 4
├───────────────────┼────────────────────────────────────────────┤
│ Why changed       │ Round 2 exploit candidates plateaued;     │
│                   │ uncertainty sampling found 2 strong hits. │
├───────────────────┼────────────────────────────────────────────┤
│ Omnigent handoff  │ Critic → Planner → Lab                    │
├───────────────────┴────────────────────────────────────────────┤
│ Best-fitness trajectory: adaptive vs fixed vs random          │
└────────────────────────────────────────────────────────────────┘
```

## 21.2 Required charts

Produce:

1. best fitness vs assays for each strategy,
2. terminal best-fitness distribution across seeds,
3. top-1% hit rate by strategy,
4. adaptive allocation by round,
5. source attribution: which action types yielded improvements,
6. optional sequence-space projection or residue heatmap.

## 21.3 Two-minute demo narrative

### 0:00–0:20 — bottleneck

"There are about 149,000 experimentally measured GB1 variants available in our virtual lab, but our scientist gets only 96 assays. Which protein should it test next?"

### 0:20–0:45 — Omnigent lab

Show Omnigent coordinating Scientist, Modeler, Exploration, Exploitation, Planner, and Critic.

### 0:45–1:15 — evidence changes plan

Show one round where a strategy underperforms, Critic identifies the issue, and Planner changes the next 24-assay allocation.

### 1:15–1:40 — discovery trajectory

Animate best-observed fitness increasing over the four rounds.

### 1:40–2:00 — scientific comparison

Show aggregate repeated-seed result versus random, greedy local, and fixed acquisition baselines.

End on the measured conclusion, not a marketing claim.

---

# 22. Claims protocol

## Allowed claim pattern

> "Across N paired confirmatory runs, the adaptive Omnigent planner achieved a median terminal best fitness of X versus Y for the fixed-mixture control under the same 96-assay budget, with a paired median/mean difference of Z and 95% CI [...]."

## Not allowed

- "Omnigent found the best protein" unless it actually found the global optimum.
- "10× faster discovery" unless directly supported by a defined measured quantity.
- "better than directed evolution" without specifying the exact simulated baseline.
- "novel" without literature support.
- claims based on a single representative seed.

---

# 23. Final project gates

The project is not complete until all gates pass.

## Gate A — literature

- [ ] primary sources reviewed,
- [ ] overlap / novelty risks documented,
- [ ] final claim refined.

## Gate B — oracle integrity

- [ ] agent cannot read full dataset,
- [ ] assay tool enforces budget,
- [ ] missing variants are unavailable, not zero.

## Gate C — baseline fairness

- [ ] same initialization,
- [ ] same budget,
- [ ] same surrogate where needed,
- [ ] fixed mixture frozen before confirmation.

## Gate D — repeated experiments

- [ ] enough paired seeds,
- [ ] raw seed-level results retained,
- [ ] primary endpoint reported.

## Gate E — agentic evidence

- [ ] planner changed strategy in response to evidence where warranted,
- [ ] change is visible in logs,
- [ ] critic/planner handoff is preserved,
- [ ] agent-value ablation completed.

## Gate F — reproducibility

- [ ] configs frozen,
- [ ] seeds stored,
- [ ] environment captured,
- [ ] run command documented.

## Gate G — demo

- [ ] Omnigent is visible,
- [ ] hidden lab is explained,
- [ ] one adaptation event is visualized,
- [ ] aggregate result is shown,
- [ ] limitations are stated.

---

# 23.5 Supporting reference files

Load these files only when relevant to keep context focused:

- `references/OMNIGENT_RUNBOOK.md` — managed Databricks and local-host execution, platform boundaries, and demo evidence.
- `references/EXPERIMENT_PROTOCOL.md` — 96-assay scientific protocol, baselines, endpoints, and confirmation rules.
- `references/LOGGING_PROTOCOL.md` — assay ledger, agent events, handoffs, decisions, and error logging.
- `references/OUTPUT_SCHEMAS.md` — structured schemas for hypotheses, candidates, planner outputs, critic outputs, surrogate reports, and round results.
- `references/SCIENTIFIC_METHOD.md` — evidence-first, falsification-first, and value-of-information reasoning.
- `references/LITERATURE_PLAN.md` — primary-source survey plan and novelty gate.
- `references/DEMO_PLAN.md` — two-minute Omnigent-centered demo sequence.

---

# 24. Root-agent startup procedure

On first execution, the Scientific Director MUST perform this sequence:

1. Read `AGENTS.md` completely.
2. Read `SKILLS.md` and inspect available native skills.
3. Inspect repository structure and current logs.
4. Verify Omnigent is actually running the session.
5. Confirm hidden oracle is inaccessible except through the lab tool.
6. Perform literature survey before strong novelty claims.
7. Write `research/project_state.yaml`.
8. Write or update `research/plan.md`.
9. Freeze development-vs-confirmation seeds.
10. Reproduce basic dataset facts through a data steward or private evaluator without exposing hidden fitness to the planner.
11. Implement or validate the virtual lab.
12. Validate one toy run end-to-end.
13. Run baseline smoke tests.
14. Run adaptive development experiments.
15. Update hypotheses and planner rules from development evidence.
16. Freeze `research/preregistration.md`.
17. Run confirmatory seeds.
18. Invoke Statistical Reviewer.
19. Invoke Critic for final claim audit.
20. Build final demo artifacts.
21. Produce `research/final_research_summary.md`.

Do not stop after producing a plan. Continue through implementation, experiments, analysis, critique, and demo unless blocked by a required human approval or missing dependency.

## 24.1 Implemented deterministic tool contract

The root agent image discovers `tools/python/omnievo_tools.py`. The Scientific Director should use these functions as narrow tools:

- `initialize_adaptive_run` — creates the lab run and executes only the common Round-1 initialization;
- `fit_observed_surrogate` — fits ExtraTrees using returned observations only;
- `generate_all_candidate_pools` — creates exploitation, uncertainty, diversity, local, and random pools without oracle labels;
- `prepare_critic_input` — computes observed-data-only source yield and prediction-error summaries;
- `save_hypothesis_report`, `save_critic_report`, and `save_planner_decision` — validate and persist structured specialist outputs inside the project workspace;
- `record_critic_to_planner_handoff` — blocks on leakage/fairness failure and records the visible handoff;
- `execute_planner_round` — validates the exact 24-slot Omnigent decision, refills unavailable candidates from the same source, and calls the lab.

Do not expose `omnievo.offline` as an agent tool. It is a private, post-run evaluator only. The adaptive run must call the hypothesis scientist, scientific critic, and experiment planner between the deterministic preparation and measurement tools; there is intentionally no Python function that autonomously chooses all adaptive allocations.

---

# 25. Recommended initial prompt to the Omnigent root agent

```text
Read AGENTS.md, SKILLS.md, the challenge brief, and the full repository before acting.

You are the Scientific Director for OmniEvo. The project tests adaptive agentic directed evolution on the GB1 four-site fitness landscape under a strict 96-assay budget. Databricks Omnigent must be the live orchestration layer: use its sub-agents, skills, tools, policies, persistent session state, and structured handoffs rather than implementing the entire scientific loop as one hidden script.

First verify the hidden-oracle boundary and the current project state. Then perform a primary-source literature survey and novelty check, finalize a fairness-controlled baseline protocol, and validate the virtual laboratory. Run a common initialization and the four-round sequential design. After every round, delegate analysis to the Scientist, Modeler, acquisition specialists, Experiment Planner, and Critic; update hypotheses and the evidence ledger; and change the next experiment only when evidence justifies it.

The primary scientific comparison is adaptive strategy allocation versus a fixed-mixture policy using the same surrogate, encoding, initialization, candidate primitives, and 96-assay budget. Repeat the complete experiment across paired random seeds and report distributions and uncertainty, not a single lucky run.

Never read the hidden GB1 fitness table directly, never treat missing variants as zero, never fabricate measurements, and never claim novelty or improvement without evidence. Log concise scientific rationales, structured handoffs, exact configs, seeds, assay history, and failures. Do not log private chain-of-thought.

The final deliverable must include a rigorous research result and a compelling two-minute demo that visibly shows Omnigent coordinating the scientific loop, one experimental result changing the next round allocation, the 96-assay constraint, and the aggregate comparison against baselines.
```
