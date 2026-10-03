# Baseline Protocol — Development Draft

Status: **implemented for development; not approved/frozen for confirmation**.

All strategies receive the same seeded theoretical-sequence order for Round 1 within each paired seed. Each strategy independently queries that identical order through the lab until 24 valid measurements are returned. Wild-type fitness is public prior knowledge and does not consume budget.

Every run uses four rounds of 24 successful measurements. Unavailable variants do not count and are refilled from the same acquisition source. Candidate generators know the 160,000 theoretical sequences but never receive valid-set membership.

The controls are:

- `random`: 24 seeded uniform unseen candidates per post-initialization round.
- `greedy_local`: 24 deterministic unseen Hamming-1 neighbors of the best observed parents, expanding to the next-best observed parent when needed.
- `fixed_exploit`: ExtraTrees predicted-mean rank, 24 slots each post-initialization round.
- `fixed_ucb`: fixed `predicted_mean + 1.0 * ensemble_std`, 24 slots each post-initialization round.
- `fixed_mixture`: 8 predicted-mean, 6 uncertainty, 6 sequence-diversity, and 4 local-mutation slots each post-initialization round.

The adaptive and fixed-mixture methods share ExtraTrees settings, 80-dimensional one-hot encoding, candidate-pool implementations, source-preserving refill, common initialization, and paired seeds. Only the adaptive method may change the allocation after structured Omnigent scientist/critic/planner handoffs.

Human approval is required before this draft and its fixed allocation are used for confirmatory seeds.

