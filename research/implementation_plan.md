# OmniEvo Implementation Plan

## Current state and constraints

- The repository currently contains an Omnigent agent image, specialist instructions, skills, schemas, and research protocols, but no executable scientific code, tests, dataset, run logs, or Git metadata.
- The raw GB1 table must remain outside this repository and outside every scientific-agent filesystem. A separate authenticated virtual-lab service will be the only component allowed to receive its path.
- Real runs require a private GB1 dataset and a Databricks Omnigent workspace or local Omnigent host. Until those are available, tests will use temporary toy fixtures and will not be reported as scientific results.

## Architecture

1. **Private virtual laboratory:** build a standalone service that loads the oracle, validates four-residue sequences, returns only requested measurements, rejects unavailable/duplicate variants, and stores durable SQLite budget state plus append-only JSONL audit records.
2. **Strict accounting and state:** enforce 24 successful assays per round and 96 per run transactionally, support refill after `UNAVAILABLE`, isolate run IDs, and persist manifests, observations, proposals, handoffs, decisions, critic reports, and errors.
3. **Deterministic scientific tools:** implement the 160,000-sequence universe, 80-feature one-hot encoding, ExtraTrees fitting and tree-variance uncertainty, seeded candidate generators, deterministic deduplication/refill, and all five required baselines.
4. **Omnigent control plane:** expose narrow Python tools to the root agent for run initialization, surrogate fitting, candidate-pool generation, batch validation, lab measurement, and round summaries. Specialist agents will provide structured scientific interpretation and allocation decisions; the root will visibly coordinate result -> hypothesis/critic -> planner -> changed allocation -> lab call.
5. **Fair evaluation:** share Round 1 observations within each paired seed, hold the surrogate/encoding/primitives/budget constant for adaptive versus fixed mixture, separate development from confirmatory seeds, and keep offline oracle metrics unavailable until a run is frozen.
6. **Analysis and demo:** produce paired bootstrap summaries, sensitivity statistics when dependencies permit, trajectory/allocation/source-yield figures, a representative non-cherry-picked trace, and a two-minute dashboard/script centered on the Omnigent handoff.

## Implementation sequence

1. Create package/config scaffolding, research state, and tests.
2. Implement and audit the private lab, budget state machine, and append-only logging.
3. Implement common initialization and random, greedy-local, fixed-exploit, fixed-uncertainty, and fixed-mixture policies.
4. Implement surrogate and acquisition/candidate utilities with deterministic tie-breaking.
5. Add root Omnigent tools and tighten agent configs/tool permissions so no sub-agent can access the oracle.
6. Add schemas and validators for planner, critic, hypotheses, handoffs, and exact 24-slot batches.
7. Implement paired multi-seed runner for fixed policies and an Omnigent round protocol for adaptive runs; do not hide adaptive decisions inside the runner.
8. Add offline evaluation, statistics, plots, dashboard/demo assets, leakage audit, and reproducibility checks.
9. Run unit and integration tests with a temporary oracle; then perform one real smoke run only after the private dataset and Omnigent credentials are available.

## Verification gates

- Restart-safe budget tests, concurrency/duplicate tests, unavailable-refill tests, and cross-run isolation tests pass.
- Candidate artifacts contain predictions and uncertainty but no true unseen fitness or availability labels.
- Every model-based strategy uses the same encoding and model settings in the primary comparison.
- Adaptive execution requires a recorded Omnigent planner decision and critic handoff before each post-initialization lab call.
- No confirmatory run starts before human approval of the frozen preregistration, as required by `AGENTS.md`.
