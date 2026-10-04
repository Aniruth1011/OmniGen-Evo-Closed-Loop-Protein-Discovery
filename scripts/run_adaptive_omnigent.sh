#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

RUN_ID="${1:-adaptive_seed_000}"
SEED="${2:-0}"
RUN_DIR="${3:-runs/adaptive/seed_$(printf '%03d' "$SEED")}"

: "${OMNIEVO_LAB_URL:=http://127.0.0.1:8765}"
if [[ -z "${OMNIEVO_LAB_TOKEN:-}" ]]; then
  LAB_TOKEN_FILE="${OMNIEVO_LAB_TOKEN_FILE:-$PWD/../gb1_omnigent_private/lab_token}"
  [[ -f "$LAB_TOKEN_FILE" ]] || {
    echo "Set OMNIEVO_LAB_TOKEN or OMNIEVO_LAB_TOKEN_FILE." >&2
    exit 1
  }
  OMNIEVO_LAB_TOKEN="$(tr -d '\n' < "$LAB_TOKEN_FILE")"
fi

if [[ -z "${OMNIEVO_DATABRICKS_TOKEN:-}" || -z "${OMNIEVO_DATABRICKS_BASE_URL:-}" ]]; then
  OMNIEVO_DATABRICKS_TOKEN="$(databricks auth token omnievo -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"
  DATABRICKS_WORKSPACE_HOST="$(databricks auth describe --profile omnievo -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["details"]["host"])')"
  OMNIEVO_DATABRICKS_BASE_URL="${DATABRICKS_WORKSPACE_HOST%/}/serving-endpoints"
fi

export OMNIEVO_LAB_URL OMNIEVO_LAB_TOKEN OMNIEVO_DATABRICKS_TOKEN OMNIEVO_DATABRICKS_BASE_URL
# Omnigent intentionally strips arbitrary caller variables from its background
# runner. Explicitly forward only the narrow lab client endpoint and credential.
export OMNIGENT_LAB_URL="$OMNIEVO_LAB_URL"
export OMNIGENT_LAB_TOKEN="$OMNIEVO_LAB_TOKEN"
export OMNIGENT_DATABRICKS_TOKEN="$OMNIEVO_DATABRICKS_TOKEN"
export OMNIGENT_DATABRICKS_BASE_URL="$OMNIEVO_DATABRICKS_BASE_URL"
# Child openai-agents workers use the harness's supported ambient credentials;
# nested Omnigent specs do not expand auth placeholders in 0.16.0.
export OPENAI_API_KEY="$OMNIEVO_DATABRICKS_TOKEN"
export OPENAI_BASE_URL="$OMNIEVO_DATABRICKS_BASE_URL"
export OMNIGENT_RUNNER_ENV_PASSTHROUGH="OMNIGENT_LAB_URL,OMNIGENT_LAB_TOKEN,OMNIGENT_DATABRICKS_TOKEN,OMNIGENT_DATABRICKS_BASE_URL"
unset OMNIEVO_PRIVATE_ORACLE_PATH OMNIEVO_PRIVATE_STATE_DIR

if ! curl --fail --silent --show-error -H "Authorization: Bearer ${OMNIEVO_LAB_TOKEN}" "${OMNIEVO_LAB_URL}/health" >/dev/null; then
  echo "Virtual lab is not reachable at ${OMNIEVO_LAB_URL}. Start it first." >&2
  exit 1
fi

BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/omnievo-final.XXXXXX")"
AGENT_BUILD="${BUILD_ROOT}/agent"
persist_artifacts() {
  if [[ -d "$AGENT_BUILD/runs" ]]; then
    mkdir -p "$PWD/runs"
    cp -R "$AGENT_BUILD/runs/." "$PWD/runs/"
  fi
  if [[ -d "$AGENT_BUILD/logs" ]]; then
    mkdir -p "$PWD/logs"
    for staged_log in "$AGENT_BUILD"/logs/*.jsonl; do
      [[ -e "$staged_log" ]] || continue
      destination="$PWD/logs/$(basename "$staged_log")"
      merged_log="$(mktemp "${TMPDIR:-/tmp}/omnievo-log.XXXXXX")"
      awk 'NF && !seen[$0]++' "$destination" "$staged_log" 2>/dev/null > "$merged_log" || \
        awk 'NF && !seen[$0]++' "$staged_log" > "$merged_log"
      mv "$merged_log" "$destination"
    done
  fi
  rm -rf "$BUILD_ROOT"
}
trap persist_artifacts EXIT
python3 scripts/build_agent_bundle.py --directory "$AGENT_BUILD"
python3 scripts/materialize_runtime_auth.py "$AGENT_BUILD"
if [[ -d "$PWD/runs" ]]; then
  mkdir -p "$AGENT_BUILD/runs"
  cp -R "$PWD/runs/." "$AGENT_BUILD/runs/"
fi

omnigent stop >/dev/null 2>&1 || true
if [[ "${OMNIEVO_SKIP_SPECIALIST_PREFLIGHT:-0}" != "1" ]]; then
  ROUTING_OUTPUT="$(omnigent run "$AGENT_BUILD" -p 'Zero-assay routing gate. Do not call laboratory or filesystem tools. Dispatch hypothesis-scientist exactly once with: reply exactly SPECIALIST_OK. Wait for the actual child response. Reply ROUTING_PREFLIGHT_PASS only if that child response was received; otherwise reply ROUTING_PREFLIGHT_FAIL and include the real error.' 2>&1)"
  printf '%s\n' "$ROUTING_OUTPUT"
  if [[ "$ROUTING_OUTPUT" != *"ROUTING_PREFLIGHT_PASS"* ]] || [[ "$ROUTING_OUTPUT" == *"ROUTING_PREFLIGHT_FAIL"* ]] || [[ "$ROUTING_OUTPUT" == *"PERMISSION_DENIED"* ]] || [[ "$ROUTING_OUTPUT" == *"Connection error"* ]]; then
    echo "Specialist routing preflight failed; refusing to spend assays." >&2
    exit 1
  fi
  omnigent stop >/dev/null 2>&1 || true
fi
omnigent run "$AGENT_BUILD" -p "Execute the complete adaptive GB1 discovery run.

Run ID: ${RUN_ID}
Seed: ${SEED}
Run directory: ${RUN_DIR}

Use native Omnigent tool calls only; never print or narrate tool-call syntax.
Complete exactly four rounds of 24 successful assays. Round 1 must use the common seeded initialization via initialize_adaptive_run. After each round—including Round 4—coordinate the Hypothesis Scientist, Surrogate Modeler, acquisition specialists, and Scientific Critic through Omnigent and save their required structured artifacts. Before Rounds 2–4, record the critic-to-planner handoff, have the Experiment Planner select exactly 24 sequences from the observed-data-only candidate pools, and execute the round through execute_planner_round. Base every adaptation only on returned measurements and observed-data diagnostics. Never access, request, or infer the private oracle path or unseen fitness.

The value COMPLETE for a single tool or round is never sufficient. Stop only when the nested lab status has status COMPLETE, successful_assays 96, remaining_budget 0, and round_counts 1 through 4 all equal 24. Treat any claimed measurement not returned by a successful native lab tool as fabricated and invalid.

Do not stop after setup, file inspection, skill loading, one round, or narration. Continue until lab_status confirms the full terminal condition. Then report the best observed fitness, per-round allocations, allocation changes, artifact paths, and final lab status. If any native tool fails, report the actual error and retry safely without inventing a result or bypassing budget, critic, or leakage controls."
