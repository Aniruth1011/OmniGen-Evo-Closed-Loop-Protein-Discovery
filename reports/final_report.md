# OmniEvo Final Development-Run Report

## Adaptive Agentic Directed Evolution on the GB1 Protein Fitness Landscape Under a 96-Assay Budget

**Run:** `adaptive_omnigent_seed_000`  
**Platform:** Databricks Omnigent with a local hidden virtual laboratory  
**Protocol:** four rounds × 24 successful assays  
**Status:** complete, 96/96 assays  
**Best observed variant:** `IYGV`  
**Best observed fitness:** **4.38774529032**

## Executive summary

OmniEvo is a scientific-agent workflow that asks whether evidence-driven strategy selection can improve directed evolution under a severe experimental budget. The agent did not receive the full GB1 landscape. It could enumerate theoretical four-residue sequences, fit models to measured variants, and obtain new fitness values only through a budget-controlled virtual laboratory.

In the completed development run, Databricks Omnigent coordinated hypothesis analysis, scientific criticism, experiment planning, and virtual-lab execution. The strategy allocation changed after every evidence update:

| Round | Random | Exploit | Uncertainty | Diversity | Local | Outcome |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 24 | 0 | 0 | 0 | 0 | Common seeded initialization; best `CNGA` = 0.5971 |
| 2 | 0 | 4 | 8 | 6 | 6 | `INGA` = 2.8315 became the new best |
| 3 | 0 | 8 | 4 | 2 | 10 | High-fitness ridge mapped; no new global best |
| 4 | 0 | 7 | 1 | 1 | 15 | Interaction-focused search found `IYGV` = 4.3877 |

The final-round hit improved over the entering best by **1.5563**, or approximately **55%**. The surrogate ranked `IYGV` fourth among the exploitation candidates, making it assay-worthy, but predicted only 1.846. Its +2.54 residual shows that the model was useful for ranking while unreliable for extrapolating extreme epistatic fitness.

This is a strong demonstration of the complete agentic loop. It is not yet evidence that adaptive Omnigent search outperforms a matched fixed strategy. That causal claim requires paired fixed-mixture baselines and repeated confirmatory seeds.

## Research question and hypotheses

The primary research question is:

> Under 96 measurements, can an adaptive scientific agent identify strong GB1 variants more effectively than fixed search policies?

The mechanistic question is stricter:

> Does changing the allocation between identical candidate-generation primitives add value beyond the surrogate model itself?

The completed run demonstrates that the controller genuinely changed policy in response to evidence. It does not resolve the primary adaptive-versus-fixed comparison:

- **H1 — adaptive policy advantage:** unresolved pending paired fixed-mixture runs.
- **H2 — state-dependent acquisition value:** preliminary within-run support; allocation changed three times for evidence-linked reasons.
- **H3 — local greed stalls under epistasis:** suggestive only; a matched local-only baseline is still required.
- **H4 — value beyond the surrogate:** unresolved; this is the primary missing causal comparison.

## Experimental system

The GB1 landscape varies four interacting residues corresponding to positions 39, 40, 41, and 54. The theoretical space contains 160,000 variants. Approximately 149,000 experimentally characterized variants are available to the hidden oracle; unavailable sequences are rejected rather than assigned zero fitness.

All model-based decisions used:

- 80-dimensional one-hot sequence encoding;
- `ExtraTreesRegressor` with 128 trees;
- predicted mean for exploitation;
- tree-ensemble spread as an uncertainty proxy;
- Hamming-space diversity;
- Hamming-1 and selected Hamming-2 local candidates.

The full table, global optimum, unseen fitness values, and global landscape statistics were never supplied to the agents.

## Omnigent orchestration

Omnigent was the control plane rather than a wrapper around a monolithic optimizer. The visible loop was:

```text
returned measurements
→ Hypothesis Scientist
→ observed-data surrogate and candidate pools
→ Scientific Critic
→ critic-to-planner handoff
→ Experiment Planner allocation
→ validated 24-sequence plan
→ hidden virtual-lab call
→ returned measurements
```

Rounds 3 and 4 are preserved as native Omnigent session traces. They contain the child-agent dispatches, structured results, planner decisions, tool calls, and returned measurements required for the demo.

## Round-by-round discovery

### Round 1 — common initialization

Twenty-four seeded random variants established a common low-data starting point. Most fitnesses were near zero. `CNGA` was the best initialization result at 0.5971.

### Round 2 — broad guided search

The first adaptive allocation emphasized uncertainty and diversity while retaining exploitation and local mutation. Model exploitation produced the strongest returns, including `INGA` at 2.8315. Uncertainty and diversity arms produced no record improvements.

The critic therefore recommended concentrating more assays around the newly discovered ridge while retaining a smaller monitoring allocation for exploration.

### Round 3 — confirm and diagnose

Omnigent increased exploitation from 4 to 8 slots and local mutation from 6 to 10, while reducing uncertainty plus diversity from 14 to 6. The round confirmed several strong neighbors:

- `INGV` = 2.2863
- `IKGA` = 2.0137
- `IVGA` = 1.9130
- `INGT` = 1.7185
- `INGS` = 1.7221

No variant exceeded `INGA`. The plateau and sparse coverage of pairwise mutations motivated a terminal-round shift toward local interaction tests and Hamming-2 doubles.

### Round 4 — test interactions

The final allocation used 15 local-mutation slots, 7 model-exploitation slots, and only one slot each for uncertainty and diversity. It produced:

- `IYGV` = **4.3877**, the terminal best;
- `FNGA` = 3.2615, the best observed single-step neighbor;
- `YNGA` = 2.6513;
- `IYGA` = 2.4352.

The highest-fitness variant was a Hamming-2 double that the surrogate ranked highly enough to test but badly underpredicted in magnitude.

## Biological interpretation

The measurements reveal strong, sign-variable epistasis. Using `INGA` as the background and an additive expectation of single A + single B − background:

| Double | Additive expectation | Observed | Epistasis |
|---|---:|---:|---:|
| `IYGV` | 1.89 | 4.39 | **+2.50** |
| `FNGV` | 2.72 | 1.07 | **−1.65** |
| `WNGV` | 0.43 | 0.06 | **−0.37** |

The same V54 mutation can therefore be strongly beneficial or antagonistic depending on its partner residue. This is precisely the type of interaction that can defeat naive single-step greed and simple magnitude extrapolation.

Substitutions at G41 were consistently poor in the sampled contexts, supporting the working hypothesis that this position is highly constrained. However, all key biological findings are based on single measurements and need replication.

## Surrogate behavior

Observed-data cross-validation improved in rank correlation as measurements accumulated:

| Training assays | CV RMSE | Spearman rank proxy |
|---:|---:|---:|
| 24 | 0.125 | −0.158 |
| 48 | 0.434 | 0.533 |
| 72 | 0.551 | 0.573 |
| 96 | 0.759 | 0.653 |

The rising RMSE partly reflects the increasingly broad fitness range and the discovery of an extreme outlier. The correct interpretation is **rank-useful, magnitude-unreliable for sparse Hamming-2 interactions**. Ensemble spread is only an uncertainty proxy, not a calibrated posterior.

## Integrity and reproducibility

- Exactly 96 successful assays were recorded: 24 per round.
- The final lab state is `COMPLETE` with zero remaining budget.
- The canonical ledger contains assay indices 1–96 with no duplicates.
- No unavailable experiment was counted as a zero-fitness measurement.
- The hidden oracle was accessible only through the authenticated lab interface.
- Critic leakage and fairness checks passed for planning continuation.
- Native Omnigent traces contain 115 items for Round 3 and 125 items for Round 4.
- All 13 repository tests pass.

## Limitations

1. This is one development seed, not a repeated confirmatory experiment.
2. No matched fixed-mixture result exists for this run, so adaptivity has not been causally isolated.
3. The best measurements are unreplicated.
4. The virtual laboratory is retrospective and not a prospective wet-lab experiment.
5. The system has been demonstrated on one four-site protein landscape.
6. The final surrogate underpredicted the winning interaction by 2.54 fitness units.
7. Terminal-distribution and top-tail hit-rate plots are intentionally not reported because the necessary repeated/offline evaluation is incomplete.

## Defensible conclusion

> In a complete 96-assay GB1 development run, Databricks Omnigent coordinated specialist analysis, scientific critique, evidence-linked strategy reallocation, and hidden-lab execution. The allocation changed after each round, and the final interaction-focused plan discovered `IYGV` with fitness 4.3877, 55% above the entering best. This demonstrates a functioning adaptive scientific loop and yields a biologically interesting epistasis hypothesis. Whether adaptivity outperforms an otherwise identical fixed policy remains unresolved until paired repeated baselines are completed.

## Recommended next experiment

The next scientific priority is not a more polished single run. It is the preregistered causal comparison:

1. replicate `IYGV`, `FNGA`, and `INGA`;
2. run adaptive and fixed-mixture policies on the same initialization for at least 30 paired seeds;
3. keep the surrogate, encoding, candidate pools, and 96-assay budget identical;
4. report paired terminal-fitness differences, bootstrap confidence intervals, and all seed-level outcomes;
5. add local-only and critic-ablation controls.

## Presentation assets

All presentation-ready figures and the interactive deck are in `artifacts/presentation/`. The deck uses arrow keys and can be recorded directly in a browser.
