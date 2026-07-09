from pathlib import Path
from typing import Optional, Tuple

import joblib
import streamlit as st

from utils.paths import PROJECT_ROOT, project_path


MODEL_DIR = project_path("models", "transformer_fake_news")
BASELINE_MODEL_PATH = project_path("models", "baseline", "logistic_regression_model.pkl")
QWEN_LORA_DIR = PROJECT_ROOT.parent / "fake-news-detection" / "models" / "qwen_lora_fake_news"
QWEN_BASE_MODEL_NAME = "Qwen/Qwen2.5-1.5B"

QWEN_LABEL_ID_TO_NAME = {
    0: "Real News",
    1: "Fake News",
}
QWEN_LABEL_NAME_TO_ID = {
    "Real News": 0,
    "Fake News": 1,
}


def detect_device():
    import torch

    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def build_qwen_instruction_text(title: str, text: str) -> str:
    return (
        "Classify the following news article as Fake News or Real News.\n\n"
        f"Title: {title}\n\n"
        f"Article: {text}\n\n"
        "Answer:"
    )


@st.cache_resource(show_spinner=False)
def load_qwen_model(
    adapter_dir: str = str(QWEN_LORA_DIR),
    model_name: str = QWEN_BASE_MODEL_NAME,
) -> Tuple[Optional[object], Optional[object], Optional[object], str]:
    path = Path(adapter_dir)
    if not (path / "adapter_config.json").exists():
        return None, None, None, "Qwen LoRA adapter not found."

    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        from peft import PeftModel
    except ModuleNotFoundError as exc:
        return None, None, None, f"Qwen dependency missing: {exc}. Install transformer dependencies first."

    try:
        device = detect_device()
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True, local_files_only=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        dtype = torch.float16 if device.type == "cuda" else torch.float32
        base_model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,
            id2label=QWEN_LABEL_ID_TO_NAME,
            label2id=QWEN_LABEL_NAME_TO_ID,
            torch_dtype=dtype,
            trust_remote_code=True,
        )
        model = PeftModel.from_pretrained(base_model, path, local_files_only=True)
        model.config.pad_token_id = tokenizer.pad_token_id
        model.to(device)
        model.eval()
        return tokenizer, model, device, ""
    except Exception as exc:
        return None, None, None, f"Could not load Qwen model: {exc}"


@st.cache_resource(show_spinner=False)
def load_transformer_model(model_dir: str = str(MODEL_DIR)) -> Tuple[Optional[object], Optional[object], str]:
    path = Path(model_dir)
    if not (path / "config.json").exists():
        return None, None, "Local transformer model not found. Train the model first."

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True)
        device = detect_device()
        model.to(device)
        model.eval()
        return tokenizer, model, ""
    except Exception as exc:
        return None, None, f"Could not load local model: {exc}"


@st.cache_resource(show_spinner=False)
def load_baseline_model(model_path: str = str(BASELINE_MODEL_PATH)) -> Tuple[Optional[object], str]:
    path = Path(model_path)
    if not path.exists():
        return None, "No trained model found. Train the transformer or baseline model first."

    try:
        return joblib.load(path), ""
    except Exception as exc:
        return None, f"Could not load baseline model: {exc}"
