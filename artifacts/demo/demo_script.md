# OmniEvo Two-Minute Demo Script

Status: **template — populate only after aggregate results and a representative Omnigent trace exist**.

## 0:00–0:20 — Constraint

“The GB1 library has roughly 149,000 available measured variants behind our virtual lab, but the scientist may reveal only 96: four batches of 24. Unmeasured fitness and even variant availability are hidden.”

Show the lab boundary and assay counter. Do not show the raw table.

## 0:20–0:45 — Omnigent control plane

“Databricks Omnigent coordinates the modeler, exploration and exploitation specialists, hypothesis scientist, experiment planner, and critic. Deterministic tools calculate scores; Omnigent owns the scientific handoffs and next-round allocation.”

Show the actual Omnigent session tree and structured specialist outputs.

## 0:45–1:15 — Real adaptation transition

Show, without editing:

1. one completed round’s `critic_input.json` and returned measurements;
2. the Scientific Critic’s diagnosis;
3. the critic-to-planner handoff event;
4. Round N and Round N+1 allocation bars;
5. the evidence-linked planner rationale;
6. `execute_planner_round` calling the virtual lab and returning 24 measurements.

Narration placeholder: “After Round [N], [source] produced [measured outcome], while [source] [plateaued/added information]. The planner therefore changed [allocation] to [allocation].”

## 1:15–1:40 — Discovery trajectory

Show the representative run’s best-so-far curve, clearly labeled representative, with fixed-mixture and random paired controls. State whether the policy change helped, harmed, or had no clear effect in the next round.

## 1:40–2:00 — Aggregate result

Show every confirmatory seed through a paired-difference plot and the terminal distribution. Use the final statistical wording exactly; include the paired effect and 95% interval. End with one limitation: retrospective virtual lab on a single four-site landscape.

If adaptivity loses, say so directly and show which policy changes failed. Never substitute the engineering fixture or a hand-picked development seed.

