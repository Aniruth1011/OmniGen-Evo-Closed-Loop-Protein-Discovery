# Two-Minute Demo Video Script

Target duration: **1:55–2:05**. Record at 1080p with the HTML deck full-screen. Keep the cursor still unless demonstrating the Omnigent trace.

## 0:00–0:12 — Hook

**Screen:** Slide 1.

**Narration:**

> Protein optimization usually fixes one search strategy in advance. OmniEvo asks a different question: can a scientific agent learn which search strategy to use while experiments are happening—with only 96 measurements?

## 0:12–0:28 — System and constraint

**Screen:** Slide 2, orchestration diagram.

**Narration:**

> We use the four-site GB1 fitness landscape as a hidden virtual laboratory. The full table never enters the agent context. Databricks Omnigent coordinates hypothesis scientists, a critic, and an experiment planner. Only the lab tool can reveal a new fitness, and every run is locked to four rounds of 24 assays.

## 0:28–0:43 — Discovery trajectory

**Screen:** Slide 3.

**Narration:**

> The first random round found CNGA at 0.60. Guided search then found INGA at 2.83. Round three confirmed a strong local ridge but did not improve the best. That plateau became evidence for changing the final plan.

## 0:43–1:04 — Show Omnigent adapting

**Screen:** Slide 4, then `artifacts/presentation/omnigent_demo_trace.html`.

**Narration:**

> After Round two, exploitation was productive while uncertainty and diversity returned no record hits. The critic recommended moving budget toward exploitation and local testing. After the Round three plateau, Omnigent went further: 15 local slots, seven model-exploitation slots, and targeted double mutants. Here is the critic-to-planner handoff, the changed allocation, and the lab call it triggered.

**On-screen trace order:**

1. `round_03/critic_report.json`
2. `omnigent_handoffs.jsonl`
3. `round_04/planner_decision.json`
4. Round 4 trace item containing `execute_planner_round`
5. `round_04/measurements.csv`

## 1:04–1:22 — Breakthrough

**Screen:** Slide 5, then Slide 6.

**Narration:**

> That decision found IYGV at 4.388—55 percent above the entering best. The biology was surprising: the winning double showed strong positive epistasis, while related F and W combinations were antagonistic. The value came from testing interactions, not just following single-mutation effects.

## 1:22–1:38 — Model versus experiment

**Screen:** Slide 7.

**Narration:**

> The surrogate did matter: it ranked IYGV fourth, so it entered the batch. But it predicted only 1.846. Experiment returned 4.388. The model supplied a useful ranking; Omnigent decided how to spend scarce assays around the model's limitations.

## 1:38–1:53 — Integrity

**Screen:** Slide 8 or briefly show the lab status.

**Narration:**

> The run completed exactly 96 successful assays, with an immutable ledger, no oracle leakage, and a visible Omnigent trace from specialist result to planner decision to returned measurement.

## 1:53–2:03 — Honest conclusion

**Screen:** Slide 9.

**Narration:**

> This proves the adaptive loop works and produced a compelling discovery run. It does not yet prove superiority. Our next experiment is the preregistered paired comparison against a fixed mixture using the same surrogate, candidates, initialization, seeds, and budget.

## Recording commands

Serve the deck locally:

```bash
# Run from the repository root.
python3 -m http.server 8000 -d artifacts/presentation
```

Open `http://127.0.0.1:8000/omnievo_deck.html`, enter full-screen mode, and use left/right arrows.

## Editing checklist

- Use 1920×1080 output.
- Keep cuts under two seconds.
- Add captions for all narration.
- Put “Development run, seed 0” on all result scenes.
- Never call the result statistically superior.
- End on the paired-baseline experiment, not merely the high score.
