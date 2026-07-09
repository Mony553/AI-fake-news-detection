from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "cleaned_fake_news.csv"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]
    return df


def _map_label(value) -> Optional[int]:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"fake", "false", "1", "label_1"}:
            return 1
        if normalized in {"real", "true", "0", "label_0"}:
            return 0
    try:
        numeric = int(value)
        if numeric in {0, 1}:
            return numeric
    except (TypeError, ValueError):
        return None
    return None


def load_kaggle_fake_true(fake_path: Path, true_path: Path) -> pd.DataFrame:
    fake = _normalize_columns(pd.read_csv(fake_path))
    true = _normalize_columns(pd.read_csv(true_path))
    fake["label"] = 1
    true["label"] = 0
    return pd.concat([fake, true], ignore_index=True)


def load_welfake(path: Path, welfake_real_label: int) -> pd.DataFrame:
    df = _normalize_columns(pd.read_csv(path))
    if "title" not in df.columns or "text" not in df.columns or "label" not in df.columns:
        raise ValueError("WELFake dataset must contain title, text, and label columns.")
    if welfake_real_label in {0, 1}:
        fake_label = 1 - welfake_real_label
        df["label"] = df["label"].map({welfake_real_label: 0, fake_label: 1})
    return df


def discover_dataset() -> tuple[str, Path | tuple[Path, Path]]:
    fake_path = RAW_DIR / "Fake.csv"
    true_path = RAW_DIR / "True.csv"
    if fake_path.exists() and true_path.exists():
        return "kaggle", (fake_path, true_path)

    candidates = [
        RAW_DIR / "WELFake_Dataset.csv",
        PROJECT_ROOT.parent / "WELFake_Dataset.csv",
        PROJECT_ROOT / "WELFake_Dataset.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return "welfake", candidate

    raise FileNotFoundError(
        "No dataset found. Place Fake.csv and True.csv in data/raw, or WELFake_Dataset.csv in data/raw."
    )


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_columns(df)
    required = {"title", "text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(sorted(missing))}")

    work = df[["title", "text", "label"]].copy()
    work["title"] = work["title"].fillna("").astype(str).str.strip()
    work["text"] = work["text"].fillna("").astype(str).str.strip()
    work["label"] = work["label"].apply(_map_label)
    work = work.dropna(subset=["label"])
    work["label"] = work["label"].astype(int)
    work = work[(work["title"] != "") | (work["text"] != "")]
    work = work.drop_duplicates(subset=["title", "text"]).reset_index(drop=True)
    work["combined_text"] = (work["title"] + ". " + work["text"]).str.strip()
    return work[["title", "text", "combined_text", "label"]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare fake news dataset.")
    parser.add_argument(
        "--welfake-real-label",
        type=int,
        default=0,
        choices=[0, 1],
        help="Original WELFake label value that means real news. Default assumes WELFake uses 0 for real.",
    )
    args = parser.parse_args()

    dataset_type, paths = discover_dataset()
    if dataset_type == "kaggle":
        fake_path, true_path = paths  # type: ignore[misc]
        raw = load_kaggle_fake_true(fake_path, true_path)
    else:
        raw = load_welfake(paths, args.welfake_real_label)  # type: ignore[arg-type]

    cleaned = clean_dataset(raw)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(cleaned):,} cleaned rows to {OUTPUT_PATH}")
    print(cleaned["label"].value_counts().rename(index={0: "REAL", 1: "FAKE"}))


if __name__ == "__main__":
    main()
