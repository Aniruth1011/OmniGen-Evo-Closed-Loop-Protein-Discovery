# Logging and Research Memory Protocol

## Objective

Make every scientific decision reconstructable without storing private chain-of-thought.

## Required directories

```text
research/
  project_state.yaml
  plan.md
  literature_matrix.csv
  novelty_memo.md
  hypotheses.yaml
  evidence_ledger.jsonl
  decision_log.md
  preregistration.md
  statistical_review.md
  final_research_summary.md

runs/
  <strategy>/
    seed_<N>/
      run_manifest.json
      round_01/
      round_02/
      round_03/
      round_04/

logs/
  agent_events.jsonl
  handoffs.jsonl
  errors.jsonl
  human_approvals.md

artifacts/
  plots/
  demo/
```

## Per-assay ledger

Every successful assay record must contain:

```yaml
run_id: ...
strategy: ...
seed: ...
round: 2
assay_index_global: 37
sequence: XXXX
fitness: ...
source_action: EXPLORE_UNCERTAIN
proposal_agent: exploration-specialist
planner_batch_id: ...
measured_at: ...
```

Never edit previous assay records. Append corrections as separate provenance events.

## Agent event log

Each important agent action should contain:

```yaml
event_id: EVT-...
timestamp: ...
agent: experiment-planner
action: allocate_assay_budget
inputs:
  - research/evidence_ledger.jsonl
  - runs/.../round_02/critic.yaml
outputs:
  - runs/.../round_03/plan.yaml
rationale_summary: "Exploitation yield plateaued; uncertainty pool produced stronger hits in round 2."
evidence_ids: [E-014, E-019]
status: success
```

`rationale_summary` must be concise and evidence-based. Do not store hidden chain-of-thought.

## Handoff log

```yaml
handoff_id: HO-...
from_agent: scientific-critic
to_agent: experiment-planner
run_id: ...
round: 3
request: "Reconsider exploration/exploitation allocation."
evidence_ids: [E-019]
constraints:
  remaining_budget: 48
  next_round_slots: 24
artifacts:
  - runs/.../round_02/critic.yaml
```

## Decision log

Every strategy change must answer:

1. What changed?
2. What measured evidence motivated it?
3. What alternative action was considered?
4. Why was the chosen action preferred?
5. What result would make the agent reverse this decision?

## Error logging

Record:
- failed tool call,
- invalid planner schema,
- unavailable sequence rejection,
- duplicate proposal,
- oracle timeout,
- model fit failure,
- reproducibility mismatch.

Scientific runs with unrecoverable logging gaps must be marked invalid.
