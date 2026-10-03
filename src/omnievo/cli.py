"""Command-line entry points for the private lab and deterministic controls."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .baselines import run_baseline
from .dataset import prepare_proteingym_gb1
from .demo import build_dashboard
from .evaluation import write_analysis
from .lab.client import LabClient
from .lab.oracle import PrivateOracle
from .lab.server import create_server
from .lab.state import LabState
from .offline import evaluate_completed_runs
from .repeated import run_repeated_baselines
from .visualize import build_figures


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"required environment variable is not set: {name}")
    return value


def _assert_private_path(path: Path) -> None:
    candidates = [Path.cwd().resolve()]
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / "config.yaml").exists():
            candidates.append(parent)
    for agent_root in candidates:
        try:
            path.relative_to(agent_root)
        except ValueError:
            continue
        raise SystemExit(f"private oracle/state path must be outside the agent-readable repository: {path}")


def serve_lab(args: argparse.Namespace) -> int:
    # The private dataset path is deliberately accepted only through the lab process environment.
    oracle_path = Path(_required_env("OMNIEVO_PRIVATE_ORACLE_PATH")).expanduser().resolve(strict=True)
    state_dir = Path(_required_env("OMNIEVO_PRIVATE_STATE_DIR")).expanduser().resolve()
    _assert_private_path(oracle_path)
    _assert_private_path(state_dir)
    oracle = PrivateOracle.from_csv(
        oracle_path,
        sequence_column=args.sequence_column,
        fitness_column=args.fitness_column,
    )
    state = LabState(state_dir / "lab.sqlite3", state_dir / "assay_ledger.jsonl")
    server = create_server(args.host, args.port, oracle, state, _required_env("OMNIEVO_LAB_TOKEN"))
    print(f"OmniEvo virtual lab listening on http://{args.host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOmniEvo virtual lab stopped.", flush=True)
    finally:
        server.server_close()
    return 0


def prepare_dataset(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve(strict=True)
    destination = Path(args.destination).expanduser().resolve()
    _assert_private_path(source)
    _assert_private_path(destination)
    print(prepare_proteingym_gb1(source, destination))
    return 0


def baseline(args: argparse.Namespace) -> int:
    client = LabClient(_required_env("OMNIEVO_LAB_URL"), _required_env("OMNIEVO_LAB_TOKEN"))
    result = run_baseline(client, args.strategy, args.seed, args.runs_root)
    print(result)
    return 0


def repeated_baselines(args: argparse.Namespace) -> int:
    client = LabClient(_required_env("OMNIEVO_LAB_URL"), _required_env("OMNIEVO_LAB_TOKEN"))
    seeds = [int(item) for item in args.seeds.split(",") if item.strip()]
    results = run_repeated_baselines(client, seeds, args.runs_root, scope=args.scope)
    print({"completed": len(results), "scope": args.scope})
    return 0


def analyze(args: argparse.Namespace) -> int:
    print(write_analysis(args.runs_root, args.output_dir))
    return 0


def figures(args: argparse.Namespace) -> int:
    print({"artifacts": build_figures(args.runs_root, args.output_dir)})
    return 0


def dashboard(args: argparse.Namespace) -> int:
    import json

    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    print({"artifacts": build_dashboard(state, args.output_dir)})
    return 0


def offline_evaluate(args: argparse.Namespace) -> int:
    print(
        evaluate_completed_runs(
            _required_env("OMNIEVO_PRIVATE_ORACLE_PATH"),
            args.runs_root,
            args.output_dir,
            args.sequence_column,
            args.fitness_column,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="omnievo")
    subparsers = parser.add_subparsers(dest="command", required=True)
    lab_parser = subparsers.add_parser("serve-lab", help="start the private budgeted GB1 oracle service")
    lab_parser.add_argument("--host", default="127.0.0.1")
    lab_parser.add_argument("--port", type=int, default=8765)
    lab_parser.add_argument("--sequence-column", default="sequence")
    lab_parser.add_argument("--fitness-column", default="fitness")
    lab_parser.set_defaults(function=serve_lab)

    dataset_parser = subparsers.add_parser(
        "prepare-proteingym", help="privately normalize and audit the official Wu 2016 GB1 assay"
    )
    dataset_parser.add_argument("--source", required=True)
    dataset_parser.add_argument("--destination", required=True)
    dataset_parser.set_defaults(function=prepare_dataset)

    baseline_parser = subparsers.add_parser("run-baseline", help="run one fixed-policy control")
    baseline_parser.add_argument("strategy")
    baseline_parser.add_argument("--seed", type=int, required=True)
    baseline_parser.add_argument("--runs-root", default="runs")
    baseline_parser.set_defaults(function=baseline)

    repeated_parser = subparsers.add_parser("run-baselines", help="run paired fixed controls over seeds")
    repeated_parser.add_argument("--seeds", required=True, help="comma-separated integer seeds")
    repeated_parser.add_argument("--scope", choices=["development", "confirmatory"], default="development")
    repeated_parser.add_argument("--runs-root", default="runs")
    repeated_parser.set_defaults(function=repeated_baselines)

    analysis_parser = subparsers.add_parser("analyze", help="aggregate completed observed run artifacts")
    analysis_parser.add_argument("--runs-root", default="runs")
    analysis_parser.add_argument("--output-dir", default="artifacts/tables")
    analysis_parser.set_defaults(function=analyze)

    figure_parser = subparsers.add_parser("figures", help="build aggregate figures")
    figure_parser.add_argument("--runs-root", default="runs")
    figure_parser.add_argument("--output-dir", default="artifacts/figures")
    figure_parser.set_defaults(function=figures)

    dashboard_parser = subparsers.add_parser("dashboard", help="build the static demo dashboard")
    dashboard_parser.add_argument("--state", required=True, help="JSON state derived from a completed run")
    dashboard_parser.add_argument("--output-dir", default="artifacts/demo")
    dashboard_parser.set_defaults(function=dashboard)

    offline_parser = subparsers.add_parser("offline-evaluate", help="post-run private oracle metrics")
    offline_parser.add_argument("--runs-root", default="runs")
    offline_parser.add_argument("--output-dir", default="artifacts/tables")
    offline_parser.add_argument("--sequence-column", default="sequence")
    offline_parser.add_argument("--fitness-column", default="fitness")
    offline_parser.set_defaults(function=offline_evaluate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.function(args))


if __name__ == "__main__":
    raise SystemExit(main())
