# Final Research Summary

Status: **one complete real-data development run; confirmatory comparison pending**.

Databricks Omnigent completed `adaptive_omnigent_seed_000` with exactly 96 successful hidden-lab assays across four rounds. The controller made three evidence-linked allocation changes and discovered `IYGV` with fitness **4.38774529032** in Round 4, improving on the entering best `INGA` (2.83147206953) by approximately 55%.

The required Omnigent transition is preserved: specialist interpretation → Scientific Critic → critic-to-planner handoff → changed Round 4 allocation → `execute_planner_round` → returned measurements. The full oracle remained outside agent context.

This run demonstrates that the adaptive orchestration loop functions and generated an interesting sign-variable epistasis hypothesis. It does **not** establish that adaptive control outperforms fixed strategies. H1 and H4 remain unresolved until matched fixed-mixture baselines and repeated paired seeds are complete. The highest-fitness observations are single, unreplicated measurements.

See `reports/final_report.md` for the complete result and `artifacts/presentation/` for the presentation package.
