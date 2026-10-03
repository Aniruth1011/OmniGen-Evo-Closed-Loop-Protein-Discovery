# Novelty-Risk Memo

## Conclusion

Novelty risk is **high** for broad claims such as “first autonomous directed-evolution system,” “first agentic protein-engineering platform,” or “first iterative active-learning method on GB1.” Those claims are contradicted by existing work.

The defensible contribution is narrower:

> We evaluate whether an Omnigent-coordinated controller that changes the *allocation among fixed acquisition primitives* after each 24-assay batch adds value beyond a frozen allocation using the same surrogate, encoding, candidate generators, initialization, seeds, and total 96-assay budget.

This is an experimental claim, not a novelty claim, until the matched repeated-seed study is complete.

## Closest overlap

[ALDE (Yang et al., 2025)](https://doi.org/10.1038/s41467-025-55987-8) is the closest methodological overlap. It already performs iterative batch active learning on GB1, retrains a surrogate after each batch, and evaluates greedy, UCB, and Thompson-sampling acquisition. Its GB1 simulations use 96 initial variants plus four further 96-variant rounds. The reported acquisition rule is selected for a campaign rather than an agent reallocating a fixed 24-slot batch among exploitation, uncertainty, diversity, and local mutation. Therefore OmniEvo must compare against fixed UCB and fixed mixture, not only random or local search.

[Wu et al. (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6500146/) and [Wittmann et al. (2021)](https://doi.org/10.1016/j.cels.2021.07.008) establish ML-assisted search on the same GB1 landscape. Wittmann et al. further show that training-set design can dominate encoding/model effects, making the common initialization and same-candidate-information controls essential.

[SAMPLE (Rapp et al., 2024)](https://doi.org/10.1038/s44286-023-00002-4) and the [generalized autonomous enzyme-engineering platform (Singh et al., 2025)](https://doi.org/10.1038/s41467-025-61209-y) establish autonomous, multi-round protein design-build-test-learn systems. [ProteinMCP (Xu et al., 2026)](https://doi.org/10.1002/pro.70547) establishes LLM/MCP orchestration for computational protein engineering. Accordingly, Omnigent coordination is the implementation mechanism, not by itself a scientific novelty.

## Claim boundaries

Safe before experiments:

- “We test evidence-driven acquisition-allocation switching under an unusually strict 96-assay GB1 budget.”
- “The primary causal comparison holds the surrogate and candidate primitives constant.”
- “The study includes a hidden-oracle boundary and source-attributed assay ledger.”

Unsafe before confirmatory results:

- “Adaptive Omnigent search is better.”
- “The agent finds extreme variants more efficiently.”
- “Critic feedback improves search.”

Unsafe regardless of result without a deeper systematic review:

- “First autonomous directed-evolution system.”
- “First agentic protein-engineering platform.”
- “First active-learning campaign on GB1.”

## Remaining literature work

The matrix covers the main GB1, low-N, Bayesian-optimization, autonomous-lab, and 2024–2026 agentic overlap. Before publication, perform citation chaining from ALDE and ProteinMCP and review any work released after 3 October 2026. Mechanistic overlap—not terminology—must determine the final wording.

