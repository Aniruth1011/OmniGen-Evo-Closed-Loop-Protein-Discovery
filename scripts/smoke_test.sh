#!/usr/bin/env bash
# End-to-end infrastructure smoke test. It never creates a run or consumes an assay.

set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRIVATE_ROOT="${OMNIEVO_PRIVATE_ROOT:-$REPO_ROOT/../gb1_omnigent_private}"
ORACLE_PATH="${OMNIEVO_PRIVATE_ORACLE_PATH:-$PRIVATE_ROOT/oracle/gb1_wu2016_oracle.csv}"
STATE_DIR="${OMNIEVO_PRIVATE_STATE_DIR:-$PRIVATE_ROOT/smoke_state}"
TOKEN_FILE="${OMNIEVO_LAB_TOKEN_FILE:-$PRIVATE_ROOT/lab_token}"
DATABRICKS_PROFILE="${DATABRICKS_CONFIG_PROFILE:-omnievo}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
OMNIEVO_CLI="$REPO_ROOT/.venv/bin/omnievo"
RUN_AGENT=1
LAB_PID=""
LAB_LOG=""
BUNDLE_DIR=""

if [[ "${1:-}" == "--skip-agent" ]]; then
  RUN_AGENT=0
elif [[ $# -gt 0 ]]; then
  printf 'Usage: %s [--skip-agent]\n' "$0" >&2
  exit 2
fi

step() {
  printf '\n==> %s\n' "$1"
}

fail() {
  printf '\nFAIL: %s\n' "$1" >&2
  exit 1
}

cleanup() {
  if [[ -n "$LAB_PID" ]] && kill -0 "$LAB_PID" 2>/dev/null; then
    kill "$LAB_PID" 2>/dev/null || true
    wait "$LAB_PID" 2>/dev/null || true
  fi
  if [[ -n "$LAB_LOG" && -f "$LAB_LOG" ]]; then
    rm -f "$LAB_LOG"
  fi
}
trap cleanup EXIT INT TERM

cd "$REPO_ROOT"

step "Checking required files and commands"
[[ -x "$PYTHON_BIN" ]] || fail "missing .venv; run: python3 -m venv .venv && .venv/bin/pip install -e '.[analysis,dev]'"
[[ -x "$OMNIEVO_CLI" ]] || fail "OmniEvo is not installed in .venv; run: .venv/bin/pip install -e '.[analysis,dev]'"
[[ -f "$ORACLE_PATH" ]] || fail "private oracle not found at $ORACLE_PATH"
command -v curl >/dev/null || fail "curl is not installed"
command -v databricks >/dev/null || fail "Databricks CLI is not installed"
command -v jq >/dev/null || fail "jq is not installed (macOS: brew install jq)"

if command -v omnigent >/dev/null; then
  OMNIGENT_BIN="$(command -v omnigent)"
elif command -v omni >/dev/null; then
  OMNIGENT_BIN="$(command -v omni)"
else
  fail "Omnigent is not installed; run: brew install uv && uv tool install 'omnigent[databricks]' --with-editable '$REPO_ROOT'"
fi

step "Checking private oracle integrity without printing fitness data"
ORACLE_ROWS="$($PYTHON_BIN - "$ORACLE_PATH" <<'PY'
import csv
import sys

with open(sys.argv[1], encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    if reader.fieldnames != ["sequence", "fitness"]:
        raise SystemExit(f"unexpected oracle columns: {reader.fieldnames}")
    count = sum(1 for _ in reader)
print(count)
PY
)"
[[ "$ORACLE_ROWS" == "149360" ]] || fail "oracle row count is $ORACLE_ROWS, expected 149360"
printf 'Oracle: OK (%s measured mutants)\n' "$ORACLE_ROWS"

step "Checking Databricks authentication profile: $DATABRICKS_PROFILE"
if ! databricks current-user me --profile "$DATABRICKS_PROFILE" >/dev/null; then
  fail "Databricks authentication failed; run: databricks auth login --host https://<workspace-host> --profile $DATABRICKS_PROFILE"
fi
printf 'Databricks auth: OK\n'

step "Checking Omnigent CLI"
"$OMNIGENT_BIN" --version

step "Running repository tests"
"$PYTHON_BIN" -m pytest

step "Creating private smoke-test state"
umask 077
mkdir -p "$STATE_DIR"
if [[ ! -s "$TOKEN_FILE" ]]; then
  "$PYTHON_BIN" -c 'import secrets; print(secrets.token_urlsafe(48))' > "$TOKEN_FILE"
fi
LAB_TOKEN="$(tr -d '\n' < "$TOKEN_FILE")"
[[ -n "$LAB_TOKEN" ]] || fail "lab token file is empty: $TOKEN_FILE"

LAB_PORT="$($PYTHON_BIN - <<'PY'
import socket

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)"
LAB_URL="http://127.0.0.1:$LAB_PORT"
LAB_LOG="$(mktemp -t omnievo-smoke.XXXXXX)"

step "Starting the authenticated private lab on $LAB_URL"
OMNIEVO_PRIVATE_ORACLE_PATH="$ORACLE_PATH" \
OMNIEVO_PRIVATE_STATE_DIR="$STATE_DIR" \
OMNIEVO_LAB_TOKEN="$LAB_TOKEN" \
  "$OMNIEVO_CLI" serve-lab --host 127.0.0.1 --port "$LAB_PORT" >"$LAB_LOG" 2>&1 &
LAB_PID=$!

HEALTHY=0
for _ in {1..40}; do
  if curl -fsS -H "Authorization: Bearer $LAB_TOKEN" "$LAB_URL/health" >/dev/null 2>&1; then
    HEALTHY=1
    break
  fi
  if ! kill -0 "$LAB_PID" 2>/dev/null; then
    sed -n '1,80p' "$LAB_LOG" >&2
    fail "virtual lab exited during startup"
  fi
  sleep 0.25
done
[[ "$HEALTHY" == "1" ]] || fail "virtual lab did not become healthy"

UNAUTHORIZED_STATUS="$(curl -sS -o /dev/null -w '%{http_code}' "$LAB_URL/health")"
[[ "$UNAUTHORIZED_STATUS" == "401" ]] || fail "lab accepted an unauthenticated request"
printf 'Virtual lab: OK (authenticated health=200, unauthenticated health=401)\n'

if [[ "$RUN_AGENT" == "1" ]]; then
  DATABRICKS_WORKSPACE_HOST="$(
    databricks auth describe --profile "$DATABRICKS_PROFILE" -o json \
      | jq -er '.details.host'
  )" || fail "could not resolve the workspace host from Databricks profile $DATABRICKS_PROFILE"
  OMNIEVO_DATABRICKS_TOKEN="$(
    databricks auth token "$DATABRICKS_PROFILE" -o json \
      | jq -er '.access_token'
  )" || fail "could not obtain a short-lived token from Databricks profile $DATABRICKS_PROFILE"
  [[ -n "$OMNIEVO_DATABRICKS_TOKEN" ]] || fail "Databricks returned an empty access token"
  export OMNIEVO_DATABRICKS_TOKEN
  export OMNIEVO_DATABRICKS_BASE_URL="${DATABRICKS_WORKSPACE_HOST%/}/serving-endpoints"

  step "Staging a link-free allowlisted Omnigent agent image"
  BUNDLE_DIR="$(mktemp -d -t omnievo-agent.XXXXXX)"
  AGENT_IMAGE="$BUNDLE_DIR/agent"
  "$PYTHON_BIN" "$REPO_ROOT/scripts/build_agent_bundle.py" --directory "$AGENT_IMAGE"

  step "Running one no-tool Omnigent model turn"
  export OMNIEVO_LAB_URL="$LAB_URL"
  export OMNIEVO_LAB_TOKEN="$LAB_TOKEN"
  unset OMNIEVO_PRIVATE_ORACLE_PATH OMNIEVO_PRIVATE_STATE_DIR
  if [[ "${OMNIEVO_KEEP_OMNIGENT_HOST:-0}" != "1" ]]; then
    "$OMNIGENT_BIN" stop >/dev/null 2>&1 || true
  fi
  AGENT_OUTPUT="$("$OMNIGENT_BIN" run "$AGENT_IMAGE" -p 'Smoke test only. Do not call tools, create a run, or measure variants. Reply exactly OMNIGENT_OK.' 2>&1)" || {
    printf '%s\n' "$AGENT_OUTPUT" >&2
    fail "Omnigent agent launch/model call failed"
  }
  if [[ "$AGENT_OUTPUT" != *"OMNIGENT_OK"* ]]; then
    printf '%s\n' "$AGENT_OUTPUT" >&2
    fail "Omnigent completed but did not return the expected marker"
  fi
  printf 'Omnigent model turn: OK\n'
else
  printf '\nOmnigent model turn: SKIPPED (--skip-agent)\n'
fi

printf '\nPASS: OmniEvo smoke test completed. No run was created and zero assays were consumed.\n'
