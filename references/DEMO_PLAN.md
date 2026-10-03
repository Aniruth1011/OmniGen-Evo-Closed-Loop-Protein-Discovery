# Two-Minute Demo Plan

## Demo objective

Show a real scientific adaptation event orchestrated by Databricks Omnigent, not merely a dashboard of final metrics.

## 0:00–0:20 — Problem

Show:
- GB1 four-site space,
- ~149k measured variants hidden behind the virtual lab,
- only 96 assay reveals allowed.

Narration:
> "The challenge is not to predict every protein. It is to decide which protein to test next when experiments are expensive."

## 0:20–0:45 — Omnigent laboratory

Show the live Omnigent session with:
- Scientific Director,
- Hypothesis Scientist,
- Surrogate Modeler,
- Exploration and Exploitation specialists,
- Experiment Planner,
- Critic.

Make the tool boundary visible: agents cannot inspect the raw GB1 oracle.

## 0:45–1:15 — Adaptation event

Show one completed round and the real Critic output. Then show the Planner changing the next 24-slot allocation because of the result.

Example visual:

```text
Round 2: Exploit 14 | Uncertain 4 | Diverse 2 | Local 4
                         |
                         v
Critic: exploitation plateaued; uncertain pool had higher yield
                         |
                         v
Round 3: Exploit 8 | Uncertain 8 | Diverse 4 | Local 4
```

Use actual project values in the final demo.

## 1:15–1:40 — Search trajectory

Animate best-observed fitness against assay count. Overlay adaptive Omnigent and at least the fixed-mixture and random baselines.

## 1:40–2:00 — Research result

Show aggregate repeated-seed results and the primary adaptive-vs-fixed comparison. End with the measured conclusion and one limitation.

## Required visual artifacts

1. assay counter,
2. strategy-allocation chart by round,
3. best-fitness trajectory,
4. terminal distribution across seeds,
5. Omnigent handoff/trace screenshot or UI state,
6. optional sequence/residue summary.
