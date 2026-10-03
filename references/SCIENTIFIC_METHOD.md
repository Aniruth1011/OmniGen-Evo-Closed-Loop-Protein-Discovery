# Scientific Reasoning Method for OmniEvo

## Evidence-first loop

Use:

```text
Observation
  -> Mechanistic hypothesis
  -> Competing explanation
  -> Falsifiable prediction
  -> Cheapest discriminating experiment
  -> Measurement
  -> Update
```

## Falsification rule

A hypothesis is useful only if the team can state what result would weaken or reject it.

## Value-of-information rule

The Experiment Planner should not ask only "which variant looks best?" It should ask:

> Which allocation of the next 24 assays gives the best combination of expected high-fitness discovery and information needed to improve later rounds?

## Separate three uncertainties

1. **Predictive uncertainty** — model uncertainty about sequence fitness.
2. **Scientific uncertainty** — uncertainty about hypotheses such as epistasis/locality.
3. **Policy uncertainty** — uncertainty about whether exploitation, exploration, or local search should receive more budget.

Do not collapse these into one number without justification.

## Negative-results rule

If adaptive search fails to beat a well-controlled fixed strategy, preserve the result. Investigate whether:
- four rounds are too few,
- the planner overreacts,
- UCB already captures enough adaptivity,
- the landscape rewards a stable acquisition policy,
- the critic introduces noise.

A negative result can still directly answer the project’s core research question.

## Anti-cherry-picking rule

Never select a final seed because it looks visually impressive. Demo a representative trace only after aggregate results are complete and label it as representative.
