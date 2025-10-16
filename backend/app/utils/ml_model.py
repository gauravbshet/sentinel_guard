from __future__ import annotations

import joblib
import os
from pathlib import Path
from typing import Dict, Any

import numpy as np
from sklearn.ensemble import IsolationForest


MODEL_PATH = Path(
    os.getenv("MODEL_PATH", "backend/model/isolation_forest.joblib"))

_model: IsolationForest | None = None


def _features_from_metrics(metrics: Dict[str, Any]) -> np.ndarray:
    return np.array([
        metrics.get("cpu_percent", 0.0),
        metrics.get("memory_percent", 0.0),
        metrics.get("net_bytes_sent", 0.0),
        metrics.get("net_bytes_recv", 0.0),
    ], dtype=float).reshape(1, -1)


def get_model() -> IsolationForest:
    global _model
    if _model is not None:
        return _model
    if MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    else:
        # Fallback: initialize a default model
        _model = IsolationForest(
            n_estimators=100, contamination=0.05, random_state=42)
        # Train on some benign baseline if no model file (zeros)
        baseline = np.zeros((100, 4))
        _model.fit(baseline)
    return _model


def predict_anomaly(metrics: Dict[str, Any]) -> Dict[str, Any]:
    model = get_model()
    X = _features_from_metrics(metrics)
    score = -model.decision_function(X)[0]
    label = "anomaly" if model.predict(X)[0] == -1 else "normal"
    return {"score": float(score), "label": label}
