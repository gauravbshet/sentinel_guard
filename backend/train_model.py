from __future__ import annotations

import os
from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib


def main():
    rng = np.random.default_rng(42)
    # Generate synthetic benign baseline data: [cpu, mem, sent, recv]
    benign = np.column_stack(
        [
            rng.normal(20, 5, 2000),  # cpu%
            rng.normal(40, 10, 2000),  # mem%
            rng.normal(1e6, 2e5, 2000),  # bytes sent
            rng.normal(1e6, 2e5, 2000),  # bytes recv
        ]
    )
    model = IsolationForest(
        n_estimators=200, contamination=0.03, random_state=42)
    model.fit(benign)

    out_path = Path(
        os.getenv("MODEL_PATH", "backend/model/isolation_forest.joblib"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_path)
    print(f"Model saved to {out_path}")


if __name__ == "__main__":
    main()
