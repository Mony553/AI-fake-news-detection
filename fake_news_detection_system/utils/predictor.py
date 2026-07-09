from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from utils.explanation import build_explanation
from utils.model_loader import (
    QWEN_LABEL_NAME_TO_ID,
    build_qwen_instruction_text,
    detect_device,
    load_baseline_model,
    load_qwen_model,
    load_transformer_model,
)


TRUST_SIGNAL_PHRASES = [
    "official announcement",
    "official website",
    "ministry",
    "public school",
    "school office",
    "schedule",
    "eligibility requirements",
    "training sessions",
    "announced",
    "program",
    "registration details",
    "research team",
    "researchers",
    "scientists",
    "astronomers",
    "public images",
    "space telescope",
    "open archive",
    "universities",
    "observatories",
    "public education",
    "data will be available",
    "study and verify",
]

HIGH_RISK_PHRASES = [
    "secret",
    "free",
    "submit your id",
    "national id",
    "unofficial",
    "only three days",
    "lose the benefit",
    "share now",
    "urgent",
    "before deleted",
    "100% guaranteed",
    "click here",
    "miracle",
    "cure",
    "doctors hate",
    "overnight",
    "government deletes",
]


@dataclass
class PredictionResult:
    prediction: str
    fake_probability: float
    real_probability: float
    credibility_score: float
    risk_level: str
    recommended_action: str
    explanation: Dict[str, object]


def _word_count(title: str, text: str) -> int:
    return len(f"{title} {text}".split())


def _phrase_count(content: str, phrases: list[str]) -> int:
    lowered = content.lower()
    return sum(1 for phrase in phrases if phrase in lowered)


def _has_official_reporting_signals(title: str, text: str) -> bool:
    content = f"{title}. {text}"
    trust_signals = _phrase_count(content, TRUST_SIGNAL_PHRASES)
    risk_signals = _phrase_count(content, HIGH_RISK_PHRASES)
    return trust_signals >= 3 and risk_signals == 0


def _baseline_fake_probability(combined_text: str) -> float | None:
    baseline_model, _ = load_baseline_model()
    if baseline_model is None:
        return None

    try:
        probabilities = baseline_model.predict_proba([combined_text])[0]
    except Exception:
        return None

    class_to_probability = {
        int(label): float(probability * 100)
        for label, probability in zip(baseline_model.classes_, probabilities)
    }
    return class_to_probability.get(1)


def _calibrated_fake_probability(title: str, text: str, model_fake_probability: float) -> float:
    """Reduce overconfident fake labels when the local sanity-check model disagrees."""
    combined_text = f"{title}. {text}".strip()
    baseline_fake_probability = _baseline_fake_probability(combined_text)
    calibrated = model_fake_probability
    mixed_signal_cap = 60.0

    if baseline_fake_probability is not None:
        disagreement = abs(model_fake_probability - baseline_fake_probability)
        if model_fake_probability >= 85 and baseline_fake_probability <= 72 and _has_official_reporting_signals(title, text):
            calibrated = min(42.0, baseline_fake_probability)
        elif disagreement >= 35 and min(model_fake_probability, baseline_fake_probability) < 70:
            calibrated = min(mixed_signal_cap, (model_fake_probability + baseline_fake_probability) / 2)
        elif model_fake_probability >= 90 and baseline_fake_probability < 75:
            calibrated = min(mixed_signal_cap, model_fake_probability)
        else:
            calibrated = (model_fake_probability * 0.65) + (baseline_fake_probability * 0.35)

    if _word_count(title, text) < 20:
        calibrated = min(calibrated, mixed_signal_cap)

    return _bounded_probability(calibrated)


def _bounded_probability(probability: float) -> float:
    return max(5.0, min(95.0, float(probability)))


def classify_from_probability(fake_probability: float) -> Dict[str, str]:
    if fake_probability >= 75:
        return {
            "prediction": "High Risk",
            "risk_level": "High Risk",
            "recommended_action": "Do not share before verifying with trusted sources.",
        }
    if fake_probability >= 45:
        return {
            "prediction": "Needs Review",
            "risk_level": "Needs Review",
            "recommended_action": "Check other reliable sources before trusting this article.",
        }
    return {
        "prediction": "Low Risk",
        "risk_level": "Low Risk",
        "recommended_action": "Article appears more credible, but verification is still recommended.",
    }


def predict_news(title: str, text: str, max_length: int = 256) -> PredictionResult:
    qwen_tokenizer, qwen_model, qwen_device, qwen_error = load_qwen_model()
    tokenizer, model, error = load_transformer_model()
    combined_text = f"{title}. {text}".strip()

    if qwen_tokenizer is not None and qwen_model is not None and qwen_device is not None:
        import torch

        prompt = build_qwen_instruction_text(title or "", text or "")
        encoded = qwen_tokenizer(
            prompt,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        encoded = {key: value.to(qwen_device) for key, value in encoded.items()}

        with torch.no_grad():
            outputs = qwen_model(**encoded)
            probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu().numpy()[0]

        raw_fake_probability = float(probabilities[QWEN_LABEL_NAME_TO_ID["Fake News"]] * 100)
        fake_probability = _calibrated_fake_probability(title, text, raw_fake_probability)
        real_probability = 100 - fake_probability
        rule = classify_from_probability(fake_probability)
        credibility_score = 100 - fake_probability
        explanation = build_explanation(title, text, fake_probability)

        return PredictionResult(
            prediction=rule["prediction"],
            fake_probability=round(fake_probability, 2),
            real_probability=round(real_probability, 2),
            credibility_score=round(credibility_score, 2),
            risk_level=rule["risk_level"],
            recommended_action=rule["recommended_action"],
            explanation=explanation,
        )

    if tokenizer is None or model is None:
        baseline_model, baseline_error = load_baseline_model()
        if baseline_model is None:
            raise RuntimeError(qwen_error or baseline_error or error or "Model has not been trained yet.")

        probabilities = baseline_model.predict_proba([combined_text])[0]
        class_to_probability = {
            int(label): float(probability * 100)
            for label, probability in zip(baseline_model.classes_, probabilities)
        }
        fake_probability = _bounded_probability(class_to_probability.get(1, 0.0))
        real_probability = 100 - fake_probability
        rule = classify_from_probability(fake_probability)
        credibility_score = 100 - fake_probability
        explanation = build_explanation(title, text, fake_probability)

        return PredictionResult(
            prediction=rule["prediction"],
            fake_probability=round(fake_probability, 2),
            real_probability=round(real_probability, 2),
            credibility_score=round(credibility_score, 2),
            risk_level=rule["risk_level"],
            recommended_action=rule["recommended_action"],
            explanation=explanation,
        )

    device = detect_device()
    import torch

    encoded = tokenizer(
        combined_text,
        truncation=True,
        padding=True,
        max_length=max_length,
        return_tensors="pt",
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        outputs = model(**encoded)
        probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu().numpy()[0]

    fake_probability = _bounded_probability(float(probabilities[1] * 100))
    real_probability = 100 - fake_probability
    rule = classify_from_probability(fake_probability)
    credibility_score = 100 - fake_probability
    explanation = build_explanation(title, text, fake_probability)

    return PredictionResult(
        prediction=rule["prediction"],
        fake_probability=round(fake_probability, 2),
        real_probability=round(real_probability, 2),
        credibility_score=round(credibility_score, 2),
        risk_level=rule["risk_level"],
        recommended_action=rule["recommended_action"],
        explanation=explanation,
    )
