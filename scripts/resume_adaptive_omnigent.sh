#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

RUN_ID="${1:-adaptive_omnigent_seed_000}"
SEED="${2:-0}"
RUN_DIR="${3:-runs/adaptive/omnigent_seed_000}"
COOLDOWN_SECONDS="${OMNIEVO_RATE_LIMIT_COOLDOWN_SECONDS:-60}"

if [[ ! "$RUN_ID" =~ ^[A-Za-z0-9_.-]+$ ]]; then
  echo "RUN_ID may contain only letters, digits, dot, underscore, and hyphen." >&2
  exit 2
fi
if [[ ! "$SEED" =~ ^[0-9]+$ ]]; then
  echo "SEED must be a non-negative integer." >&2
  exit 2
fi
if [[ ! "$COOLDOWN_SECONDS" =~ ^[0-9]+$ ]] || (( COOLDOWN_SECONDS > 60 )); then
  echo "OMNIEVO_RATE_LIMIT_COOLDOWN_SECONDS must be an integer from 0 to 60." >&2
  exit 2
fi

: "${OMNIEVO_LAB_URL:=http://127.0.0.1:8765}"
if [[ -z "${OMNIEVO_LAB_TOKEN:-}" ]]; then
  LAB_TOKEN_FILE="${OMNIEVO_LAB_TOKEN_FILE:-$PWD/../gb1_omnigent_private/lab_token}"
  [[ -f "$LAB_TOKEN_FILE" ]] || {
    echo "Set OMNIEVO_LAB_TOKEN or OMNIEVO_LAB_TOKEN_FILE." >&2
    exit 1
  }
  OMNIEVO_LAB_TOKEN="$(tr -d '\n' < "$LAB_TOKEN_FILE")"
fi

refresh_databricks_auth() {
  OMNIEVO_DATABRICKS_TOKEN="$(databricks auth token omnievo -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"
  DATABRICKS_WORKSPACE_HOST="$(databricks auth describe --profile omnievo -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["details"]["host"])')"
  OMNIEVO_DATABRICKS_BASE_URL="${DATABRICKS_WORKSPACE_HOST%/}/serving-endpoints"
  export OMNIEVO_DATABRICKS_TOKEN OMNIEVO_DATABRICKS_BASE_URL
  export OMNIGENT_DATABRICKS_TOKEN="$OMNIEVO_DATABRICKS_TOKEN"
  export OMNIGENT_DATABRICKS_BASE_URL="$OMNIEVO_DATABRICKS_BASE_URL"
  export OPENAI_API_KEY="$OMNIEVO_DATABRICKS_TOKEN"
  export OPENAI_BASE_URL="$OMNIEVO_DATABRICKS_BASE_URL"
}

export OMNIEVO_LAB_URL OMNIEVO_LAB_TOKEN
export OMNIGENT_LAB_URL="$OMNIEVO_LAB_URL"
export OMNIGENT_LAB_TOKEN="$OMNIEVO_LAB_TOKEN"
export OMNIGENT_RUNNER_ENV_PASSTHROUGH="OMNIGENT_LAB_URL,OMNIGENT_LAB_TOKEN,OMNIGENT_DATABRICKS_TOKEN,OMNIGENT_DATABRICKS_BASE_URL"
unset OMNIEVO_PRIVATE_ORACLE_PATH OMNIEVO_PRIVATE_STATE_DIR

status_json() {
  curl --fail --silent --show-error \
    -H "Authorization: Bearer ${OMNIEVO_LAB_TOKEN}" \
    "${OMNIEVO_LAB_URL}/v1/runs/${RUN_ID}/status"
}

status_field() {
  local field="$1"
  status_json | python3 -c 'import json,sys; print(json.load(sys.stdin)[sys.argv[1]])' "$field"
}

if ! curl --fail --silent --show-error \
  -H "Authorization: Bearer ${OMNIEVO_LAB_TOKEN}" \
  "${OMNIEVO_LAB_URL}/health" >/dev/null; then
  echo "Virtual lab is not reachable at ${OMNIEVO_LAB_URL}. Start it first." >&2
  exit 1
fi

INITIAL_STATUS="$(status_json)"
python3 -c '
import json, sys
s = json.loads(sys.argv[1])
count = s["successful_assays"]
rounds = {int(k): v for k, v in s["round_counts"].items()}
if count not in (48, 72, 96):
    raise SystemExit(f"Refusing unsafe resume: expected 48, 72, or 96 assays, found {count}")
expected = {1: 24, 2: 24, 3: 24 if count >= 72 else 0, 4: 24 if count >= 96 else 0}
if rounds != expected:
    raise SystemExit(f"Refusing unsafe resume: unexpected round counts {rounds}; expected {expected}")
print(f"Safe resume state: {count}/96 assays; round counts {rounds}")
' "$INITIAL_STATUS"

if [[ "${OMNIEVO_RESUME_CHECK_ONLY:-0}" == "1" ]]; then
  echo "RESUME_CHECK_PASS (no assays or model calls were made)"
  exit 0
fi

if (( COOLDOWN_SECONDS > 0 )); then
  echo "Cooling down ${COOLDOWN_SECONDS}s before refreshing Databricks auth..."
  sleep "$COOLDOWN_SECONDS"
fi
# Always replace inherited credentials. Databricks OAuth access tokens are
# short-lived, and embedding a stale exported token causes an immediate 403.
refresh_databricks_auth

MODEL_PROBE_BODY='{"model":"databricks-deepseek-v4-flash-0731","messages":[{"role":"user","content":"Reply OK"}],"max_tokens":4}'
MODEL_PROBE_FILE="$(mktemp "${TMPDIR:-/tmp}/omnievo-model-probe.XXXXXX")"
MODEL_PROBE_STATUS="$(curl --silent --show-error --output "$MODEL_PROBE_FILE" --write-out '%{http_code}' \
  -H "Authorization: Bearer ${OMNIEVO_DATABRICKS_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "$MODEL_PROBE_BODY" \
  "${OMNIEVO_DATABRICKS_BASE_URL}/chat/completions")"
if [[ "$MODEL_PROBE_STATUS" != "200" ]]; then
  echo "Databricks model preflight failed with HTTP ${MODEL_PROBE_STATUS}." >&2
  python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("error_code", d.get("error", "unknown error")))' "$MODEL_PROBE_FILE" >&2 || true
  rm -f "$MODEL_PROBE_FILE"
  exit 1
fi
rm -f "$MODEL_PROBE_FILE"
echo "DATABRICKS_MODEL_PREFLIGHT_PASS"

BUILD_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/omnievo-resume.XXXXXX")"
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

run_phase() {
  local round="$1"
  local expected_before="$2"
  local expected_after="$3"
  local final_clause
  if (( round == 4 )); then
    final_clause="After measurement, complete observed-data-only Round 4 hypothesis, surrogate, acquisition, and critic artifacts. Stop only after lab_status reports COMPLETE, 96 successful assays, zero remaining, and 24 assays in every round."
  else
    final_clause="After measurement, verify lab_status reports ACTIVE with exactly 72 successful assays and Round 3 equal to 24. Leave Round 3 post-processing for the next fresh phase, then stop."
  fi

  local before
  before="$(status_field successful_assays)"
  if (( before >= expected_after )); then
    echo "Round ${round} is already complete; skipping it."
    return 0
  fi
  if (( before != expected_before )); then
    echo "Refusing Round ${round}: expected ${expected_before} assays before phase, found ${before}." >&2
    return 1
  fi

  if (( PHASES_STARTED > 0 && COOLDOWN_SECONDS > 0 )); then
    echo "Cooling down ${COOLDOWN_SECONDS}s before Round ${round} to clear the Databricks rolling token limit..."
    sleep "$COOLDOWN_SECONDS"
  fi
  PHASES_STARTED=$((PHASES_STARTED + 1))
  omnigent stop >/dev/null 2>&1 || true

  set +e
  omnigent run "$AGENT_BUILD" -p "Resume one existing adaptive GB1 run and execute only the next scientific phase.

Run ID: ${RUN_ID}
Seed: ${SEED}
Run directory: ${RUN_DIR}
Target measurement round: ${round}
Expected lab count before this phase: ${expected_before}
Expected lab count after this phase: ${expected_after}

This is a RESUME. First call lab_status. Never call initialize_adaptive_run. Never repeat, replace, or modify completed measurements. Treat the lab status and assay ledger as authoritative.

Before planning Round ${round}, finish any missing post-processing artifacts for Round $((round - 1)) from observed measurements only: fit the preregistered surrogate, generate candidate pools, obtain the hypothesis report, obtain the scientific critic report, and record the critic-to-planner handoff. Coordinate the required specialist agents through actual Omnigent child sessions. To avoid the Databricks token-rate failure, dispatch exactly one specialist at a time and wait for its actual result before dispatching the next; never launch specialists concurrently. Keep child prompts and returned rationales concise and scientific.

Then obtain the Experiment Planner decision through an actual child session, validate and save an exactly-24 allocation, and invoke execute_planner_round once for Round ${round}. Use only observed evidence and theoretical sequences; never access or request the private oracle path or unseen fitness. Do not fabricate child responses, tool results, or measurements. If an artifact already exists and validates, reuse it instead of regenerating it.

${final_clause}

Report the authoritative lab status, best observed fitness, allocation, and saved handoff/artifact paths. If infrastructure fails, report the real error and exit without reinitializing or bypassing any gate."
  local omnigent_rc=$?
  set -e

  local after
  after="$(status_field successful_assays)"
  echo "Authoritative lab count after Round ${round} phase: ${after}/96"
  if (( after == expected_after )); then
    if (( omnigent_rc != 0 )); then
      echo "Omnigent CLI returned ${omnigent_rc}, but the lab atomically reached the expected checkpoint; continuing safely." >&2
    fi
    return 0
  fi
  echo "Round ${round} did not reach its checkpoint (CLI=${omnigent_rc}, assays=${after})." >&2
  echo "Artifacts will be preserved. Re-run this same command after the rate-limit window clears." >&2
  return 1
}

PHASES_STARTED=0
CURRENT_COUNT="$(status_field successful_assays)"
if (( CURRENT_COUNT == 48 )); then
  run_phase 3 48 72
fi
CURRENT_COUNT="$(status_field successful_assays)"
if (( CURRENT_COUNT == 72 )); then
  run_phase 4 72 96
fi

FINAL_STATUS="$(status_json)"
python3 -c '
import json, sys
s = json.loads(sys.argv[1])
ok = (
    s["status"] == "COMPLETE"
    and s["successful_assays"] == 96
    and s["remaining_budget"] == 0
    and all(int(s["round_counts"].get(str(r), s["round_counts"].get(r, -1))) == 24 for r in range(1, 5))
)
if not ok:
    raise SystemExit(f"Run is not complete: {s}")
print("RESUME_COMPLETE")
print(json.dumps(s, indent=2, sort_keys=True))
' "$FINAL_STATUS"
