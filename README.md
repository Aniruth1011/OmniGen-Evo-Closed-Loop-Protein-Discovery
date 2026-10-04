# OmniEvo

OmniEvo tests whether evidence-driven strategy switching adds value beyond a fixed acquisition policy on the four-site GB1 landscape under a strict `4 × 24 = 96` assay budget. Databricks Omnigent is the scientific control plane; Python provides deterministic, auditable tools.

## Security boundary

The raw GB1 table must never be placed in this repository or mounted into an agent sandbox. Run the virtual lab in a separate process/host with these private environment variables:

```bash
export OMNIEVO_PRIVATE_ORACLE_PATH=/private/path/gb1.csv
export OMNIEVO_PRIVATE_STATE_DIR=/private/path/omnievo-lab-state
export OMNIEVO_LAB_TOKEN='generate-a-long-random-token'
omnievo serve-lab --host 127.0.0.1 --port 8765
```

The Omnigent host receives only:

```bash
export OMNIEVO_LAB_URL=http://127.0.0.1:8765
export OMNIEVO_LAB_TOKEN='the-same-token'
```

Do not set `OMNIEVO_PRIVATE_ORACLE_PATH` in the Omnigent/agent environment.

## Dataset status and reproducible preparation

The official ProteinGym v1.3 Wu 2016 GB1 assay has been downloaded and normalized into an owner-only sibling directory:

```text
../gb1_omnigent_private/oracle/gb1_wu2016_oracle.csv
```

It is intentionally not part of this repository. To reproduce the download and conversion from scratch:

```bash
# Run from the repository root.
mkdir -p ../gb1_omnigent_private/{downloads,source,oracle}
curl -fL --retry 3 \
  -o ../gb1_omnigent_private/downloads/DMS_ProteinGym_substitutions_v1.3.zip \
  https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip
unzip -j -o \
  ../gb1_omnigent_private/downloads/DMS_ProteinGym_substitutions_v1.3.zip \
  DMS_ProteinGym_substitutions/SPG1_STRSG_Wu_2016.csv \
  -d ../gb1_omnigent_private/source
source .venv/bin/activate
omnievo prepare-proteingym \
  --source ../gb1_omnigent_private/source/SPG1_STRSG_Wu_2016.csv \
  --destination ../gb1_omnigent_private/oracle/gb1_wu2016_oracle.csv
chmod -R go-rwx ../gb1_omnigent_private
```

The safe integrity record is in `research/dataset_audit.md`; the private audit JSON sits beside the oracle.

## Local setup

Python 3.12 is recommended for current Omnigent tooling; the deterministic package supports Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[analysis,dev]'
python -m pytest
```

The package has no CUDA dependency. ExtraTrees uses 128 CPU trees and the theoretical 160,000-sequence one-hot matrix is generated locally without oracle labels.

After authenticating Databricks and installing Omnigent, run the zero-assay end-to-end smoke test:

```bash
./scripts/smoke_test.sh
```

To check everything except the paid Omnigent model turn:

```bash
./scripts/smoke_test.sh --skip-agent
```

The smoke test builds a temporary, allowlisted agent directory before launching Omnigent. This is required because Omnigent 0.16.0 directory bundling follows every regular file under the supplied directory and rejects `.venv` interpreter links on upload. The staged image excludes `.venv`, caches, generated runs, artifacts, and all private-oracle paths.

## Omnigent run

Use the root agent image in this repository. Current Omnigent agent-image discovery loads sub-agents from `agents/`, native skills from `skills/`, and root Python tools from `tools/python/`. Install this package in the Omnigent host first so the tool module can import `omnievo`.

```bash
omnigent run .
```

For a Databricks-backed local host on macOS, install the current CLIs and authenticate first:

```bash
brew install uv
brew install databricks/tap/databricks
# Install Omnigent and inject this project plus its scientific dependencies
# into the same isolated tool environment.
uv tool install 'omnigent[databricks]' --with-editable "$PWD"

export DATABRICKS_HOST='https://<your-workspace-host>'
databricks auth login --host "$DATABRICKS_HOST" --profile omnievo
databricks current-user me --profile omnievo
omnigent setup
```

In `omnigent setup`, add the Databricks profile `omnievo` as the model provider. Then open the managed Omnigent page at `$DATABRICKS_HOST/omnigent`. Because the private lab is on this Mac, register this Mac as the execution host rather than launching the project in a remote sandbox:

```bash
omnigent login "$DATABRICKS_HOST/omnigent"
omnigent host "$DATABRICKS_HOST/omnigent"
```

If the workspace does not expose managed Omnigent, run the same agent image through the local Omnigent server with the Databricks model provider:

```bash
omnigent start
omnigent run .
```

Do not put the raw dataset in DBFS, a Unity Catalog volume, the Git repository, or a Databricks Sandbox. A remote sandbox cannot reach `127.0.0.1` on the Mac; use the registered local host until the lab is separately deployed behind a private authenticated endpoint.

### Start the real private lab (Terminal 1)

Create the token once:

```bash
# Run from the repository root.
umask 077
mkdir -p ../gb1_omnigent_private/lab_state
python3 -c 'import secrets; print(secrets.token_urlsafe(48))' > ../gb1_omnigent_private/lab_token
```

Then start the service:

```bash
source .venv/bin/activate
export OMNIEVO_PRIVATE_ORACLE_PATH="$PWD/../gb1_omnigent_private/oracle/gb1_wu2016_oracle.csv"
export OMNIEVO_PRIVATE_STATE_DIR="$PWD/../gb1_omnigent_private/lab_state"
export OMNIEVO_LAB_TOKEN="$(tr -d '\n' < "$PWD/../gb1_omnigent_private/lab_token")"
omnievo serve-lab --host 127.0.0.1 --port 8765
```

### Start the agent host (Terminal 2)

This terminal gets only the narrow service URL and token—not either private path:

```bash
# Run from the repository root.
source .venv/bin/activate
export OMNIEVO_LAB_URL='http://127.0.0.1:8765'
export OMNIEVO_LAB_TOKEN="$(tr -d '\n' < "$PWD/../gb1_omnigent_private/lab_token")"
unset OMNIEVO_PRIVATE_ORACLE_PATH OMNIEVO_PRIVATE_STATE_DIR
curl -fsS -H "Authorization: Bearer $OMNIEVO_LAB_TOKEN" "$OMNIEVO_LAB_URL/health"
```

Before a real run, execute the harmless sandbox canary check. It must report that the sibling path is inaccessible; if it can stat the canary, stop and tighten the Omnigent sandbox before doing science:

```bash
omnigent run . -p \
  'Security preflight only: try to stat ../gb1_omnigent_private/ACCESS_CANARY. Do not inspect any other sibling file. Report PASS only if access is denied or the path is invisible; otherwise report FAIL and stop.'
```

After that passes, start the persistent scientific session:

```bash
omnigent run .
```

In a managed workspace, register the same directory as the custom agent image and keep the Databricks Omnigent session trace. The root agent must visibly perform:

```text
returned measurements
→ Hypothesis Scientist / Scientific Critic
→ critic-to-planner handoff
→ Experiment Planner 24-slot decision
→ execute_planner_round virtual-lab tool
→ returned measurements
```

The tool refuses adaptive Rounds 2–4 without a non-blocking critic artifact and an exact, unique, unmeasured 24-slot planner decision.

## Fixed controls

After starting the private lab, one development control can be run with:

```bash
omnievo run-baseline fixed_mixture --seed 0
```

Or run all five controls over development seeds:

```bash
omnievo run-baselines --scope development --seeds 0,1,2
```

Confirmatory execution is code-gated until `logs/approvals.md` contains an explicit `CONFIRMATORY_PROTOCOL_APPROVED` record. Do not add that record without the required human approval.

## Analysis and demo

```bash
omnievo analyze
omnievo figures
omnievo offline-evaluate  # only in a private evaluator process after runs freeze
omnievo dashboard --state artifacts/demo/representative_state.json
```

`offline-evaluate` is intentionally not exposed as an Omnigent tool. It alone may use the private oracle after completed runs to calculate top-tail hits and normalized regret.

No real GB1 scientific results are included in the repository at present. Test fixtures validate engineering behavior only.
