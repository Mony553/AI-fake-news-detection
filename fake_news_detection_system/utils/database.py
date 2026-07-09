from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

import pandas as pd

from utils.paths import project_path


HISTORY_PATH = project_path("data", "history", "prediction_history.csv")
HISTORY_COLUMNS = [
    "datetime",
    "title",
    "source",
    "url",
    "prediction",
    "fake_probability",
    "real_probability",
    "credibility_score",
    "risk_level",
    "explanation_summary",
]


def ensure_history_file() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        pd.DataFrame(columns=HISTORY_COLUMNS).to_csv(HISTORY_PATH, index=False)


def load_history() -> pd.DataFrame:
    ensure_history_file()
    try:
        return pd.read_csv(HISTORY_PATH)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=HISTORY_COLUMNS)


def save_prediction(record: Dict[str, object]) -> None:
    ensure_history_file()
    row = {column: record.get(column, "") for column in HISTORY_COLUMNS}
    if not row["datetime"]:
        row["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history = load_history()
    history = pd.concat([history, pd.DataFrame([row])], ignore_index=True)
    history.to_csv(HISTORY_PATH, index=False)


def save_batch(records: Iterable[Dict[str, object]]) -> None:
    records = list(records)
    if not records:
        return
    ensure_history_file()
    rows: List[Dict[str, object]] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for record in records:
        row = {column: record.get(column, "") for column in HISTORY_COLUMNS}
        row["datetime"] = record.get("datetime") or now
        rows.append(row)
    history = load_history()
    history = pd.concat([history, pd.DataFrame(rows)], ignore_index=True)
    history.to_csv(HISTORY_PATH, index=False)


def clear_history() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=HISTORY_COLUMNS).to_csv(HISTORY_PATH, index=False)
