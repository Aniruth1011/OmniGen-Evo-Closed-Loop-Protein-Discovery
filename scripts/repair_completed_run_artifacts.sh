#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

RUN_DIR="${1:-runs/adaptive/omnigent_seed_000}"
RUN_ID="${2:-adaptive_omnigent_seed_000}"

for required in \
  "$RUN_DIR/assay_ledger.jsonl" \
  "$RUN_DIR/round_03/assay_ledger.jsonl" \
  "$RUN_DIR/round_04/assay_ledger.jsonl"; do
  [[ -s "$required" ]] || {
    echo "Missing observed-measurement artifact: $required" >&2
    exit 1
  }
done

ledger_tmp="$(mktemp "${TMPDIR:-/tmp}/omnievo-ledger.XXXXXX")"
jq -cs 'sort_by(.assay_index_global) | unique_by(.assay_index_global) | .[]' \
  "$RUN_DIR/assay_ledger.jsonl" \
  "$RUN_DIR/round_03/assay_ledger.jsonl" \
  "$RUN_DIR/round_04/assay_ledger.jsonl" > "$ledger_tmp"

jq -e -s --arg run_id "$RUN_ID" '
  length == 96 and
  all(.[]; .run_id == $run_id) and
  ([.[].assay_index_global] == [range(1; 97)]) and
  ([group_by(.round)[] | length] == [24, 24, 24, 24])
' "$ledger_tmp" >/dev/null
mv "$ledger_tmp" "$RUN_DIR/assay_ledger.jsonl"

for round in 03 04; do
  nested="$RUN_DIR/round_${round}/round_${round}"
  [[ -d "$nested" ]] || continue
  for artifact in measurements.csv observations.csv round_result.json planner_decision.yaml; do
    if [[ -f "$nested/$artifact" ]]; then
      cp "$nested/$artifact" "$RUN_DIR/round_${round}/$artifact"
    fi
  done
done

mkdir -p logs
touch logs/omnigent_handoffs.jsonl
for planner_round in 03 04; do
  if [[ "$planner_round" == "03" ]]; then
    critic_round="02"
    session_id="9dc40220070748f187431ca7dfd21a3c"
  else
    critic_round="03"
    session_id="a1fb05050c6d45058f5b7b3d960ee4d1"
  fi
  handoff_id="HO-${RUN_ID}-r${planner_round}"
  if ! grep -Fq "\"handoff_id\":\"${handoff_id}\"" logs/omnigent_handoffs.jsonl && \
     ! grep -Fq "\"handoff_id\": \"${handoff_id}\"" logs/omnigent_handoffs.jsonl; then
    jq -nc \
      --arg handoff_id "$handoff_id" \
      --arg timestamp "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
      --arg run_id "$RUN_ID" \
      --argjson round "$((10#$planner_round))" \
      --arg critic "$RUN_DIR/round_${critic_round}/critic_report.json" \
      --arg planner "$RUN_DIR/round_${planner_round}/planner_decision.json" \
      --arg session_id "$session_id" \
      '{handoff_id:$handoff_id,timestamp:$timestamp,from_agent:"scientific-critic",to_agent:"experiment-planner",run_id:$run_id,round:$round,request:"Allocate the next 24 assays using the critic evidence and frozen action space.",artifacts:[$critic,$planner],status:"ready",omnigent_session_id:$session_id,provenance:"recovered from validated artifacts after staging-log overwrite; native session trace preserved"}' \
      >> logs/omnigent_handoffs.jsonl
  fi
done
cp logs/omnigent_handoffs.jsonl "$RUN_DIR/omnigent_handoffs.jsonl"

echo "REPAIR_COMPLETE: canonical ledger has 96 observed measurements"
