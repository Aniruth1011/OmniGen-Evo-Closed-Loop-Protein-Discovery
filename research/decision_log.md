# Decision Log

No scientific experiment decisions have been made. Engineering design decisions are documented in `implementation_plan.md`; toy-fixture tests are not scientific evidence.


## Run adaptive_omnigent_seed_000 — Round 4 (final, 24/24 assays, run COMPLETE)

Evidence entering round:
- best fitness = 2.8315 (INGA, Round 2, single unreplicated measurement)
- Round 3 flat: no improvement; INGV 2.2863 best of round; noise floor ~ +-0.55
- Surrogate n=72 CV RMSE 0.551, Spearman 0.573; EXPLOIT top IKGV/IVGV (~1.9), LOCAL = INGA Hamming-1 (128)
- Critic verdict: modify (leakage/fairness PASS); replicate anchors impossible (pools exclude measured); merge EXPLOIT+LOCAL reasoning; cut UNCERTAIN 4->1, DIVERSE 2->1; beat-candidate block; pre-commit gap>0.7 rule

Decision:
- exploit = 7, uncertain = 1, diverse = 1, local = 15, random = 0 (sum 24)
- Selected: pos54 aromatics (INGY/INGW/INGF/INGI/INGM), Hamming-2 doubles (IKGV/IVGV/IYGV/INLV/FNGV/WNGV), pos39 W/F/Y (FNGA/YNGA), pos41 I/M/K probes, 1 diversity guard (PYFV)

Why this changed (vs Round 3 8/4/2/10):
- Round 3 showed Hamming-1 single sweeps around INGA had diminishing returns and zero measured double mutants was the largest blind spot; all potential winners were ING*-family doubles/aromatics, so LOCAL (parent-prioritized) + EXPLOIT (model-ranked doubles) carried the budget while uncertainty/diversity were cut to monitoring (1 each)

Alternative considered:
- Replicate-first block of INGA/INGV/IKGA (rejected: pools exclude measured sequences, no replicate mechanism in frozen tool contract)
- 10 exploit / 10 local / 2 uncertain / 2 diverse (rejected: fewer beat-candidates than 15 local + 7 exploit)

What result would reverse this decision next round:
- Any IYGV replicate < 3.0 (positive-epistasis claim collapses); FNGV replicate > 2.7 (pos39 transfer rescues); new best from non-ING* candidate (narrow-landscape hypothesis false)

Result:
- IYGV 4.3877 (NEW BEST, EXPLOIT_MODEL rank 4, predicted 1.846; +1.556 gap, clears pre-committed >0.7)
- FNGA 3.2615 (best single, LOCAL_MUTATE), YNGA 2.6513, IYGA 2.4352, INGF 1.8449
- Uncertainty (INKV 0.0044) and diversity (PYFV 0.0032) ~0; 0 unavailable rejections
- Final lab status: COMPLETE, 96 successful assays, 0 remaining, 24 per round
- Best observed fitness: 4.3877 (IYGV, single-replicate; U-01: Y at pos40 per planner convention vs pos39 in prose — positive-epistasis magnitude robust to parse, partner position not)
