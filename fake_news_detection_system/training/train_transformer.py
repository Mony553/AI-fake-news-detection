from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DATA_PATH = DATA_DIR / "cleaned_fake_news.csv"
MODEL_DIR = PROJECT_ROOT / "models" / "transformer_fake_news"
REPORTS_DIR = PROJECT_ROOT / "reports"


def detect_device_name() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def compute_metrics(eval_pred) -> dict:
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall": recall_score(labels, predictions, zero_division=0),
        "f1": f1_score(labels, predictions, zero_division=0),
    }


def tokenize_dataset(dataset: Dataset, tokenizer, max_length: int) -> Dataset:
    def tokenize(batch):
        return tokenizer(batch["combined_text"], truncation=True, max_length=max_length)

    return dataset.map(tokenize, batched=True, remove_columns=["title", "text", "combined_text"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune BERT/RoBERTa for fake news detection.")
    parser.add_argument("--model-name", default="bert-base-uncased", help="bert-base-uncased or roberta-base")
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    args = parser.parse_args()

    if not DATA_PATH.exists():
        raise FileNotFoundError("Cleaned dataset not found. Run python training/prepare_data.py first.")

    device_name = detect_device_name()
    print(f"Detected training device: {device_name}")

    df = pd.read_csv(DATA_PATH)
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df["label"], random_state=42)
    train_df.to_csv(DATA_DIR / "train_data.csv", index=False)
    val_df.to_csv(DATA_DIR / "validation_data.csv", index=False)
    test_df.to_csv(DATA_DIR / "test_data.csv", index=False)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=2,
        id2label={0: "REAL", 1: "FAKE"},
        label2id={"REAL": 0, "FAKE": 1},
    )

    train_dataset = tokenize_dataset(Dataset.from_pandas(train_df), tokenizer, args.max_length)
    val_dataset = tokenize_dataset(Dataset.from_pandas(val_df), tokenizer, args.max_length)
    test_dataset = tokenize_dataset(Dataset.from_pandas(test_df), tokenizer, args.max_length)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    training_args = TrainingArguments(
        output_dir=str(PROJECT_ROOT / "models" / "training_checkpoints"),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=args.weight_decay,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=50,
        report_to="none",
        seed=42,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    test_metrics = trainer.evaluate(test_dataset, metric_key_prefix="test")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    trainer.save_model(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    (MODEL_DIR / "label_mapping.json").write_text(json.dumps({"REAL": 0, "FAKE": 1}, indent=2))

    metrics = {
        "model_name": args.model_name,
        "max_length": args.max_length,
        "batch_size": args.batch_size,
        "epochs": args.epochs,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "device": device_name,
        "training_data_size": len(train_df),
        "validation_data_size": len(val_df),
        "test_data_size": len(test_df),
        "transformer_test": {
            "accuracy": test_metrics.get("test_accuracy"),
            "precision": test_metrics.get("test_precision"),
            "recall": test_metrics.get("test_recall"),
            "f1": test_metrics.get("test_f1"),
        },
    }
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Saved transformer model to {MODEL_DIR}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
