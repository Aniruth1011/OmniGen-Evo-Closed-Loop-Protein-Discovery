# Structured Output Schemas

## Hypothesis record

```yaml
id: H-001
status: PROPOSED
observation: ...
statement: ...
prediction: ...
falsifier: ...
alternatives:
  - ...
evidence_for: []
evidence_against: []
strategy_implication: ...
last_updated_round: 1
```

## Candidate record

```yaml
sequence: XXXX
source_action: EXPLOIT_MODEL|EXPLORE_UNCERTAIN|EXPLORE_DIVERSE|LOCAL_MUTATE|RANDOM_SAMPLE
source_agent: ...
score: ...
score_definition: ...
parent: null
rank: ...
metadata: {}
```

## Planner output

```yaml
run_id: ...
round: 3
budget: 24
allocation:
  EXPLOIT_MODEL: 8
  EXPLORE_UNCERTAIN: 8
  EXPLORE_DIVERSE: 4
  LOCAL_MUTATE: 4
selected_sequences:
  - sequence: XXXX
    source_action: EXPLOIT_MODEL
fallback_sequences:
  - sequence: YYYY
    source_action: EXPLORE_DIVERSE
rationale:
  - evidence_id: E-014
    implication: ...
validation:
  unique: true
  unmeasured: true
  count: 24
```

## Critic output

```yaml
run_id: ...
round: 2
status: PASS|WARN|BLOCK
findings:
  - severity: low|medium|high|blocking
    statement: ...
    evidence_ids: [...]
prior_plan_assessment: ...
policy_change_recommended: true|false
recommended_change: ...
repairs_required: []
```

## Surrogate report

```yaml
run_id: ...
round: ...
model_family: ...
encoding: ...
train_n: ...
seed: ...
hyperparameters: {}
uncertainty_method: ...
diagnostics: {}
artifacts:
  candidate_scores: ...
warnings: []
```

## Round result

```yaml
run_id: ...
strategy: ...
round: ...
assays_requested: 24
assays_successful: 24
unavailable_rejections: 0
best_before: ...
best_after: ...
round_best: ...
action_yield: {}
artifact_paths: []
```
