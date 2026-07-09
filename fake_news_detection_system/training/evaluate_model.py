from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "test_data.csv"
MODEL_DIR = PROJECT_ROOT / "models" / "transformer_fake_news"
REPORTS_DIR = PROJECT_ROOT / "reports"


def detect_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def predict_batch(texts, tokenizer, model, device, max_length: int = 256, batch_size: int = 16):
    predictions = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        encoded = tokenizer(batch, truncation=True, padding=True, max_length=max_length, return_tensors="pt")
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.no_grad():
            logits = model(**encoded).logits
        predictions.extend(torch.argmax(logits, dim=-1).cpu().tolist())
    return predictions


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Test split not found. Run python training/train_transformer.py first.")
    if not (MODEL_DIR / "config.json").exists():
        raise FileNotFoundError("Trained transformer model not found. Run python training/train_transformer.py first.")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)
    device = detect_device()
    model.to(device)
    model.eval()

    y_true = df["label"].astype(int).tolist()
    y_pred = predict_batch(df["combined_text"].astype(str).tolist(), tokenizer, model, device)

    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }
    report = classification_report(y_true, y_pred, target_names=["REAL", "FAKE"], zero_division=0)
    (REPORTS_DIR / "classification_report.txt").write_text(report)

    matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=["REAL", "FAKE"], yticklabels=["REAL", "FAKE"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "confusion_matrix.png", dpi=160)
    plt.close()

    metrics_path = REPORTS_DIR / "metrics.json"
    existing = {}
    if metrics_path.exists():
        try:
            existing = json.loads(metrics_path.read_text())
        except json.JSONDecodeError:
            existing = {}
    existing["transformer_test"] = metrics
    metrics_path.write_text(json.dumps(existing, indent=2))

    print(report)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
