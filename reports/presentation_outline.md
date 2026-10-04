# OmniEvo Presentation Outline

Use the generated browser deck at `artifacts/presentation/omnievo_deck.html`. It contains nine 16:9 slides and is optimized for full-screen recording.

## Slide 1 — Adaptive Agentic Directed Evolution

**Headline:** 96 assays. Four rounds. One hidden GB1 landscape.

**Say:** We built OmniEvo to test whether an adaptive scientific agent can decide what kind of experiment to run next—not merely rank sequences with a fixed model.

**Visual:** Title metric: `IYGV = 4.388`.

## Slide 2 — The scientific question

**Headline:** Does strategy switching add value beyond the surrogate?

**Show:** `06_omnigent_orchestration.png`

**Key points:**

- Full GB1 fitness table remains behind the lab boundary.
- Omnigent owns hypothesis, critique, allocation, and tool invocation.
- Deterministic tools own modeling, validation, and assay accounting.

## Slide 3 — The discovery run

**Headline:** The best observed fitness rose from 0.597 to 4.388.

**Show:** `01_discovery_trajectory.png`

**Callouts:** `CNGA → INGA → IYGV`; Round 3 plateau; Round 4 jump.

## Slide 4 — The agent changed its mind

**Headline:** Every new evidence batch changed the next 24-assay allocation.

**Show:** `02_adaptive_allocation.png`

**Key points:**

- Round 2 explored broadly.
- Low-yield uncertainty/diversity slots were reduced.
- Final round prioritized local and pairwise interaction tests.

## Slide 5 — Evidence → strategy change → result

**Headline:** This is the core Omnigent contribution.

**Show:** `07_adaptation_story.png`

**Demo insert:** Briefly switch to the saved Round 4 Omnigent session trace and show:

1. Round 3 critic report;
2. critic-to-planner handoff;
3. Round 4 allocation;
4. `execute_planner_round` tool call;
5. returned `IYGV` measurement.

## Slide 6 — The biological surprise

**Headline:** The winning double showed strong positive epistasis.

**Show:** `04_epistasis.png`

**Say:** V54 was not universally beneficial. Its effect changed sign with the partner residue, which is exactly why interaction-aware experimental design matters.

## Slide 7 — Why both model and agent mattered

**Headline:** The model ranked the winner; the experiment revealed its magnitude.

**Show:** `05_model_diagnostics.png`

**Say:** `IYGV` was ranked fourth but predicted at only 1.846. Observed fitness was 4.388. The model was a useful generator, not an oracle.

## Slide 8 — Where the assays paid off

**Headline:** Exploitation found the terminal best; local search found the best single.

**Show:** `03_source_performance.png`

**Key point:** Diversity and uncertainty were useful monitoring arms but had very low observed fitness yield in this run.

## Slide 9 — The honest conclusion

**Headline:** Complete adaptive demonstration; causal superiority remains to be tested.

**Show:** `08_evidence_status.png`

**Close with:**

> We demonstrated the full autonomous loop. The next step is the paired adaptive-versus-fixed experiment that isolates agentic value.

## Backup slides

- Full round allocation table.
- Exact 96-row assay ledger.
- Final critic limitations.
- Hidden-oracle architecture and audit.
- Reproducibility commands and tests.
