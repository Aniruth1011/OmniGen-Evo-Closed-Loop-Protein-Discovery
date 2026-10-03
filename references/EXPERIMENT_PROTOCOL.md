# Experimental Protocol — GB1 96-Assay Search

## Core budget

Use exactly:

```text
4 rounds x 24 successful assays = 96 assays
```

The virtual laboratory is retrospective: the hidden GB1 table acts as an oracle for experiments that would otherwise require laboratory measurement.

## Initial knowledge

All compared strategies receive the same:
- mutable sites: 39, 40, 41, 54,
- amino-acid alphabet,
- wild-type genotype,
- wild-type fitness,
- total budget,
- round size,
- allowed public prior knowledge.

They do not receive unmeasured fitness values, the global optimum, high-fitness clusters, or the full fitness distribution.

## Missing sequences

Unmeasured variants in the source landscape are **unavailable**, not zero fitness. If proposed, the lab returns `UNAVAILABLE` and the planner fills the slot using a preregistered fallback rule.

## Primary causal comparison

The key comparison is:

```text
Adaptive Omnigent strategy controller
vs
Fixed-mixture controller
```

Hold constant:
- surrogate family,
- encoding,
- initialization,
- candidate primitives,
- assay budget,
- round count,
- paired seeds.

This comparison isolates the value of adaptive strategy allocation better than comparing against random search alone.

## Required baselines

1. Random search.
2. Budget-matched greedy single-mutation/local walk.
3. Fixed exploitation.
4. Fixed uncertainty/UCB-style acquisition.
5. Fixed mixture of exploitation, uncertainty, diversity, and local search.

## Primary endpoint

Terminal best observed fitness after 96 successful assays.

## Secondary endpoints

- best observed fitness vs assay count,
- best observed fitness after each round,
- proportion of runs reaching a preregistered high-fitness threshold,
- hit rate for a preregistered top-tail definition if allowed only in offline evaluation,
- action-source yield,
- diversity of sampled variants,
- robustness across paired seeds.

## Development vs confirmation

During development:
- choose surrogate,
- debug candidate generation,
- tune planner prompt/rules,
- test logging,
- select fixed-mixture baseline allocation.

Before confirmation freeze:
- primary endpoint,
- seed list,
- surrogate,
- encoding,
- initialization,
- action space,
- fixed-mixture allocation,
- adaptive planner constraints,
- statistics plan.

Do not tune on confirmatory seeds.
