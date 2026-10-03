---
name: databricks-omnigent-runbook
description: "Run the project correctly on Databricks Omnigent. Use this skill when executing the databricks omnigent runbook stage of the OmniEvo project under Databricks Omnigent."
---

# databricks-omnigent-runbook

## Goal
Run the project correctly on Databricks Omnigent.

## Managed path
1. Open `<workspace-url>/omnigent`.
2. Start a new session.
3. Prefer Databricks Sandbox when available.
4. Load/register the OmniEvo agent image.
5. Confirm model access is routed through the workspace-managed path.
6. Confirm project files are mounted or checked out.
7. Confirm hidden GB1 oracle is exposed only through the lab tool/service.
8. Run a smoke-test assay with a known allowed test fixture, not the real hidden dataset if that would leak.

## Local M5 path
1. Run the Omnigent host on the Mac.
2. Use the same agent image.
3. Keep raw oracle data outside the agent-readable working tree.
4. Connect to the managed Omnigent server if using the Databricks-managed control plane.

## Warning
Do not assume custom Python policies are available on managed Databricks Omnigent. Prefer built-ins or supported CEL policies.

---

## Omnigent execution rule

- Treat Databricks Omnigent as the orchestration layer; do not bypass the root Scientific Director for cross-stage decisions.
- Write outputs to the exact project artifact paths defined above.
- Preserve the 96-assay budget and hidden-oracle boundary.
- Return concise evidence, artifact paths, and next-step recommendations; do not expose private chain-of-thought.
