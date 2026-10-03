# OmniEvo on Databricks Omnigent

## What this bundle is

This folder is an Omnigent-oriented scientific agent image for:

**Adaptive Agentic Directed Evolution on the GB1 Protein Fitness Landscape Under a 96-Assay Budget.**

The root Scientific Director delegates literature review, hypothesis generation, surrogate-model reporting, exploration, exploitation, local search, experiment planning, critique, statistics, and demo preparation to specialist sub-agents.

## Why Omnigent must stay central

The project is specifically designed so Omnigent owns the live discovery loop:

```text
Observed assays
  -> specialist analysis
  -> competing proposals
  -> experiment planner
  -> hidden virtual lab
  -> critic
  -> updated next-round plan
```

Do not replace this with one Python optimizer that decides all four rounds internally. Python should provide deterministic scientific tools; Omnigent should coordinate the scientific decisions.

## Managed Databricks path

Current Databricks documentation describes managed Omnigent as a Databricks-operated server integrated with workspace identity, Foundation Model APIs / Unity Gateway, and Databricks Sandbox. In a supported workspace:

1. Open `<workspace-url>/omnigent`.
2. Start a new session.
3. Select Databricks Sandbox when available, or register the local Mac as a host.
4. Register/load this custom agent image.
5. Confirm the agent can see the project files but cannot read the raw hidden GB1 oracle.
6. Start with the root prompt at the end of `AGENTS.md`.

## Local M5 path

Use the same agent image with an Omnigent host running on the Mac. Keep the hidden GB1 CSV outside the agent-readable repo and expose only a narrow virtual-lab tool or local service.

## Hidden-oracle requirement

The most important architecture rule is:

```text
Omnigent agents -> lab.measure_batch(...) -> private GB1 oracle
```

NOT:

```text
Omnigent agents -> read gb1.csv
```

If the agent can inspect the complete landscape, the research question is invalid.

## Suggested repo layout around this agent

```text
project/
├── omnigent/
│   └── omnievo/               # this bundle
├── src/
│   ├── lab/
│   ├── models/
│   ├── acquisition/
│   ├── baselines/
│   ├── analysis/
│   └── demo/
├── research/
├── runs/
├── logs/
├── artifacts/
└── tests/
```

Keep the raw oracle outside `project/` or behind a service boundary.

## Current Omnigent notes

- Custom agents are YAML-defined and can point instructions to `AGENTS.md`.
- Omnigent supports sub-agents, local tools, skills, policies, and sandboxing.
- Managed Databricks Omnigent routes model access through Databricks-managed infrastructure when using Databricks Sandbox.
- Managed Databricks supports built-in contextual policies and custom CEL policies; do not assume arbitrary Python policies are supported there.

Because Omnigent is evolving quickly, validate `config.yaml` against the version enabled in your Databricks workspace before the event. The scientific instructions and native skill files are independent of harness choice.

## What is now included

This bundle contains:

- root `AGENTS.md` scientific operating contract,
- master `SKILLS.md` catalog,
- **34 native Omnigent skills** under `skills/<name>/SKILL.md`,
- 10 specialist sub-agent instruction files,
- reusable reference docs for logging, experiment protocol, literature, schemas, scientific reasoning, and demo design.

The intended workflow is Databricks Omnigent-first. The platform should visibly coordinate the experiment loop; deterministic Python components are scientific tools, not a substitute for agent orchestration.

## Implemented tool boundary

The root image now auto-discovers `tools/python/omnievo_tools.py`. These functions can initialize a run, fit the observed-data-only surrogate, generate shared candidate pools, prepare a leakage-safe critic packet, record the critic-to-planner handoff, validate a 24-slot planner decision, and invoke the virtual lab. They accept only a lab URL/token; the private dataset path belongs exclusively to the separate `omnievo serve-lab` process.

Install the local package in the Omnigent host before loading the image:

```bash
python -m pip install -e '.[analysis]'
omnigent run .
```

See `README.md` for the complete local/private-service setup. Validate `config.yaml` with the exact Omnigent version enabled in the target Databricks workspace before recording the demo.
