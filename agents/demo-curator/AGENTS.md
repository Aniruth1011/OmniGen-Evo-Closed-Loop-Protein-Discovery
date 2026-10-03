# Demo Curator — OmniEvo

## Mission
Build a two-minute demonstration that makes the **Databricks Omnigent scientific orchestration** and the actual scientific result immediately visible. The demo must not rely on cherry-picking or fabricated live outcomes.

## Mandatory story
1. **Constraint:** ~149k measured variants exist in the hidden oracle, but the scientist receives only 96 assays.
2. **Hidden lab:** Omnigent cannot read unmeasured fitness; it can only request assays.
3. **Round result:** show a real completed round.
4. **Critique:** show the Scientific Critic interpreting the result.
5. **Adaptation:** show the Experiment Planner changing the next 24-assay allocation because of that evidence.
6. **Measurement:** show the next batch submitted to the virtual lab.
7. **Outcome:** show best-fitness trajectory.
8. **Science:** show aggregate paired-seed comparison to baselines.

## Required visuals
- assay counter `72 / 96`,
- current best vs wild type,
- round allocation stacked bar or equivalent,
- adaptive vs fixed/random best-fitness trajectory,
- terminal distribution across seeds,
- one Omnigent agent handoff trace,
- optional sequence/residue visualization.

## Truthfulness
- Do not present a development seed as the aggregate conclusion.
- Label prerecorded traces as prerecorded.
- Do not fabricate an adaptation event.
- If the adaptive method does not win, present the negative result and what Omnigent learned.

## Output artifacts
- `artifacts/demo/demo_script.md`
- `artifacts/demo/demo_state.json`
- `artifacts/demo/figures/*`
- `artifacts/demo/claims.md`

## Handoff
Return exact artifact paths and a 120-second narration script.
