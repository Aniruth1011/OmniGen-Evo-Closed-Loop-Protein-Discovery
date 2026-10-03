# Databricks Omnigent Runbook for OmniEvo

## Purpose

This runbook defines how the GB1 directed-evolution project should use **Databricks Omnigent** as the live orchestration layer. If project notes refer to "OmniAgent," interpret that as the Databricks product **Omnigent**.

## Non-negotiable architecture

```text
Databricks Omnigent root Scientific Director
        |
        +--> literature / hypothesis / model / exploration / exploitation agents
        |
        +--> Experiment Planner
        |       |
        |       +--> deterministic candidate-generation/model tools
        |
        +--> Virtual Lab tool
                |
                +--> PRIVATE GB1 fitness oracle
```

The agent system must never be given direct read access to the private oracle table.

## Managed Databricks path

1. Confirm the workspace has the Omnigent preview enabled.
2. Open `<workspace-url>/omnigent`.
3. Start a new session.
4. Prefer Databricks Sandbox for reproducible hosted execution when available.
5. Load the OmniEvo agent image / repository.
6. Verify that project files are visible while the raw GB1 oracle is not.
7. Verify that the virtual-lab tool is callable and budget-limited.
8. Start the root agent using the startup prompt in `AGENTS.md`.
9. Keep the Omnigent session trace for the final demo.

## Local M5 host path

1. Install the Omnigent CLI requirements required by the current Databricks quickstart.
2. Register the Mac as a host.
3. Keep the exact same agent image, skills, and sub-agents used in managed execution.
4. Keep the raw GB1 table outside the agent-readable repository.
5. Expose only a narrow measurement service/tool to the agent.
6. Record the host hardware, OS, Python version, and package lockfile.

## Why Omnigent must remain central

Python code should implement deterministic operations such as:
- sequence encoding,
- surrogate fitting,
- candidate scoring,
- Hamming-distance calculation,
- statistical analysis,
- virtual-lab lookup,
- plotting.

Omnigent should coordinate scientific decisions such as:
- which specialist to call,
- what hypothesis changed,
- which candidate-generation modes to request,
- how to allocate the next 24 assays,
- whether critic feedback requires a strategy change,
- what experiment should run next.

Do not hide all adaptive logic inside a single optimizer and call it from Omnigent once.

## Required visible Omnigent evidence for the demo

Capture at least one real sequence of:

```text
Round result
  -> Hypothesis Scientist
  -> Scientific Critic
  -> Experiment Planner
  -> changed allocation
  -> Virtual Lab call
  -> returned assays
```

The final demo should show that the next scientific decision changed because of measured evidence.

## Policies and permissions

- Use least privilege.
- The root agent may call approved sub-agents and scientific tools.
- Sub-agents should not inherit hidden-oracle access.
- The virtual-lab tool alone may access the private dataset.
- Use supported Databricks/Omnigent contextual or CEL policies where useful.
- Do not assume arbitrary Python policies are supported in the managed Databricks environment.

## Portability rule

The scientific protocol must remain stable if execution moves from the local M5 host to Databricks Sandbox. Only the execution backend may change; the research question, assay budget, baselines, agent roles, logging, and confirmatory protocol may not silently change.
