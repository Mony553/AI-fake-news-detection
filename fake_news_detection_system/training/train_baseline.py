from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_fake_news.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "baseline" / "logistic_regression_model.pkl"
REPORTS_DIR = PROJECT_ROOT / "reports"


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Cleaned dataset not found. Run python training/prepare_data.py first.")

    df = pd.read_csv(DATA_PATH)
    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=50000, ngram_range=(1, 2), min_df=2)),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    pipeline.fit(train_df["combined_text"], train_df["label"])
    predictions = pipeline.predict(test_df["combined_text"])

    metrics = {
        "accuracy": accuracy_score(test_df["label"], predictions),
        "precision": precision_score(test_df["label"], predictions),
        "recall": recall_score(test_df["label"], predictions),
        "f1": f1_score(test_df["label"], predictions),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    baseline_metrics_path = REPORTS_DIR / "baseline_metrics.json"
    baseline_metrics_path.write_text(json.dumps({"baseline_test": metrics}, indent=2))
    print(f"Saved baseline model to {MODEL_PATH}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
