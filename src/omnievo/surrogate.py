"""Observed-data-only ExtraTrees surrogate and uncertainty proxy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .constants import AMINO_ACIDS, SEQUENCE_LENGTH
from .errors import ProtocolError
from .space import theoretical_sequences, validate_sequence


def _imports():
    try:
        import joblib
        import numpy as np
        from sklearn.ensemble import ExtraTreesRegressor
        from sklearn.model_selection import KFold, cross_val_predict
    except ImportError as exc:
        raise RuntimeError("surrogate tools require the dependencies declared in pyproject.toml") from exc
    return joblib, np, ExtraTreesRegressor, KFold, cross_val_predict


def encode_sequences(sequences: Iterable[str]):
    _, np, _, _, _ = _imports()
    items = [validate_sequence(item) for item in sequences]
    encoded = np.zeros((len(items), SEQUENCE_LENGTH * len(AMINO_ACIDS)), dtype=np.uint8)
    residue_index = {residue: index for index, residue in enumerate(AMINO_ACIDS)}
    for row, sequence in enumerate(items):
        for position, residue in enumerate(sequence):
            encoded[row, position * len(AMINO_ACIDS) + residue_index[residue]] = 1
    return encoded


def _rank_correlation(observed, predicted) -> float | None:
    _, np, _, _, _ = _imports()
    if len(observed) < 3 or float(np.std(observed)) == 0 or float(np.std(predicted)) == 0:
        return None
    observed_rank = np.argsort(np.argsort(observed, kind="stable"), kind="stable").astype(float)
    predicted_rank = np.argsort(np.argsort(predicted, kind="stable"), kind="stable").astype(float)
    return float(np.corrcoef(observed_rank, predicted_rank)[0, 1])


def fit_and_score(
    observations: list[dict[str, Any]],
    output_dir: str | Path,
    run_id: str,
    round_number: int,
    seed: int,
    n_estimators: int = 128,
    min_samples_leaf: int = 1,
) -> dict[str, Any]:
    if len(observations) < 2:
        raise ProtocolError("at least two observed assays are required to fit the surrogate")
    joblib, np, ExtraTreesRegressor, KFold, cross_val_predict = _imports()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    sequences = [validate_sequence(item["sequence"]) for item in observations]
    if len(sequences) != len(set(sequences)):
        raise ProtocolError("surrogate training observations contain duplicate sequences")
    targets = np.asarray([float(item["fitness"]) for item in observations], dtype=float)
    features = encode_sequences(sequences)
    hyperparameters = {
        "n_estimators": int(n_estimators),
        "min_samples_leaf": int(min_samples_leaf),
        "max_features": "sqrt",
        "n_jobs": -1,
        "random_state": int(seed),
    }
    model = ExtraTreesRegressor(**hyperparameters)
    splits = min(5, len(observations))
    predictions = cross_val_predict(
        ExtraTreesRegressor(**hyperparameters),
        features,
        targets,
        cv=KFold(n_splits=splits, shuffle=True, random_state=seed),
        n_jobs=1,
    )
    rmse = float(np.sqrt(np.mean((predictions - targets) ** 2)))
    spearman_proxy = _rank_correlation(targets, predictions)
    model.fit(features, targets)

    universe = theoretical_sequences()
    universe_features = encode_sequences(universe)
    per_tree = np.vstack([tree.predict(universe_features) for tree in model.estimators_])
    predicted_mean = per_tree.mean(axis=0).astype(np.float32)
    predicted_std = per_tree.std(axis=0).astype(np.float32)
    score_path = output / "candidate_scores.npz"
    np.savez_compressed(
        score_path,
        sequences=np.asarray(universe, dtype="U4"),
        predicted_fitness=predicted_mean,
        uncertainty=predicted_std,
    )
    model_path = output / "surrogate.joblib"
    joblib.dump(model, model_path)
    report = {
        "run_id": run_id,
        "round": round_number,
        "model_family": "ExtraTreesRegressor",
        "encoding": "4x20 one-hot (80 features)",
        "train_n": len(observations),
        "seed": seed,
        "hyperparameters": hyperparameters,
        "uncertainty_method": "standard deviation across ExtraTrees estimators",
        "diagnostics": {
            "observed_cv_rmse": rmse,
            "observed_cv_spearman_rank_proxy": spearman_proxy,
            "cv_folds": splits,
            "caveat": "Diagnostics use observed assays only; ensemble spread is not calibrated posterior uncertainty.",
        },
        "artifacts": {"candidate_scores": str(score_path), "model": str(model_path)},
        "warnings": [],
    }
    (output / "surrogate_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def load_score_records(path: str | Path) -> list[dict[str, Any]]:
    _, np, _, _, _ = _imports()
    with np.load(Path(path), allow_pickle=False) as payload:
        sequences = payload["sequences"]
        means = payload["predicted_fitness"]
        uncertainties = payload["uncertainty"]
        return [
            {
                "sequence": str(sequence),
                "predicted_fitness": float(mean),
                "uncertainty": float(uncertainty),
            }
            for sequence, mean, uncertainty in zip(sequences, means, uncertainties)
        ]
