# Confirmatory Preregistration — Draft, Not Frozen

**Do not run or inspect confirmatory seeds until a human approves this document.**

- Primary endpoint: best observed fitness after exactly 96 successful assays.
- Primary contrast: adaptive Omnigent allocation minus fixed-mixture allocation, paired by seed.
- Candidate confirmatory seeds: 100–149.
- Common initialization: seeded uniform order over theoretical variants, with unavailable refill.
- Primary surrogate: `ExtraTreesRegressor`, 4×20 one-hot encoding, 128 trees, `max_features=sqrt`, `min_samples_leaf=1`.
- Fixed mixture: exploit 8, uncertainty 6, diversity 6, local mutation 4.
- Adaptive action space: predicted-mean exploitation, ensemble-variance uncertainty, Hamming diversity, Hamming-1 local mutation, and optional random slots; exactly 24 total.
- Rounds and budget: 4×24 = 96 successful measurements.
- Primary analysis: paired mean/median difference and paired bootstrap 95% confidence interval. Wilcoxon signed-rank is a sensitivity analysis.
- Secondary analyses: round trajectories, AUC of best-so-far, source yield, allocation changes, top-tail hits computed only by the offline evaluator, and predefined ablations.

Approval: **PENDING**

