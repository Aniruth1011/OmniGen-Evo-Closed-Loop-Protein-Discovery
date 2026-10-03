# Literature Survey Plan

## Goal

Determine what is established, what baselines are scientifically defensible, and whether the claim "adaptive strategy selection itself adds value" is genuinely distinct from previous GB1 ML-guided directed-evolution work.

## Search clusters

1. Wu et al. 2016 GB1 fitness landscape.
2. ML-assisted directed evolution using GB1.
3. Low-N protein engineering / sequence-function learning.
4. Bayesian optimization for protein sequence design.
5. Active learning and adaptive acquisition in protein engineering.
6. Bandit and sequential experimental design methods.
7. Autonomous / agentic scientific experiment planning.
8. Recent work (especially 2024–2026) that switches acquisition policies dynamically.

## Extraction columns

```text
citation
year
protein/dataset
sequence space
initialization size
assay budget
surrogate
acquisition rule
adaptive or fixed
number of rounds
primary metric
best result
key limitation
overlap with OmniEvo
```

## Novelty gate

Before saying the contribution is novel, answer:

> Has prior work already used a sequential controller that changes among exploration, exploitation, diversity sampling, and local search based on intermediate GB1 assay outcomes under a strict small budget?

If yes, narrow the contribution to a more specific controlled comparison or reproducibility result.
