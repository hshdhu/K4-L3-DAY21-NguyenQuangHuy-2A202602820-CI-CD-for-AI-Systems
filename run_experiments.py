"""Run the three required local MLflow experiments and retain the best model."""
import json
import os
from pathlib import Path
import mlflow
import yaml
from src.train import train

if __name__ == "__main__":
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
    mlflow.set_experiment("Default")
    configs = [
        dict(n_estimators=100, learning_rate=0.1, max_depth=3),
        dict(n_estimators=50, learning_rate=0.05, max_depth=2),
        dict(n_estimators=200, learning_rate=0.1, max_depth=5),
    ]
    results = []
    for params in configs:
        train(params)
        report = json.loads(Path("outputs/report.json").read_text())
        results.append(dict(params=params, **report))
    Path("outputs/experiments.json").write_text(json.dumps(results, indent=2))
    best = max(results, key=lambda row: row["f1_score"])
    Path("params.yaml").write_text(yaml.safe_dump(best["params"], sort_keys=False))
    if best != results[-1]:
        train(best["params"])
    print(json.dumps(results, indent=2))
