from __future__ import annotations

import re
from typing import Dict, List


SUSPICIOUS_PHRASES = [
    "shocking",
    "secret",
    "hidden",
    "breaking",
    "exposed",
    "miracle",
    "cure",
    "government hides",
    "doctors hate",
    "100% guaranteed",
    "click here",
    "share now",
    "before deleted",
    "urgent",
    "unbelievable",
    "conspiracy",
    "banned",
    "leaked",
]


def find_suspicious_phrases(text: str) -> List[str]:
    lowered = text.lower()
    return [phrase for phrase in SUSPICIOUS_PHRASES if phrase in lowered]


def punctuation_warning(text: str) -> bool:
    return bool(re.search(r"(!{2,}|\?{2,}|[!?]{3,})", text))


def writing_pattern_warning(text: str) -> bool:
    words = re.findall(r"[A-Za-z]+", text)
    if not words:
        return False
    uppercase_words = [word for word in words if len(word) > 3 and word.isupper()]
    return len(uppercase_words) / max(len(words), 1) > 0.08


def build_explanation(title: str, text: str, fake_probability: float) -> Dict[str, object]:
    combined = f"{title}. {text}".strip()
    phrases = find_suspicious_phrases(combined)
    is_short = len(combined.split()) < 80
    has_punctuation_warning = punctuation_warning(combined)
    has_pattern_warning = writing_pattern_warning(combined)

    reasons: List[str] = []
    if fake_probability >= 75:
        reasons.append("the model found strong high-risk signals")
    elif fake_probability >= 45:
        reasons.append("the model confidence is mixed and needs human review")
    else:
        reasons.append("the model found stronger signals of credible reporting")

    if phrases:
        reasons.append("it contains emotional or exaggerated phrases often seen in misleading posts")
    if is_short:
        reasons.append("the article is short, so there is less evidence for the model to evaluate")
    if has_punctuation_warning:
        reasons.append("it uses excessive punctuation")
    if has_pattern_warning:
        reasons.append("the writing style contains unusual capitalization patterns")

    summary = "The article may be suspicious because " + ", ".join(reasons) + "."
    if fake_probability < 45 and not phrases and not has_punctuation_warning:
        summary = "The article appears more credible based on the model score and writing signals, but it should still be verified with trusted sources."

    return {
        "summary": summary,
        "suspicious_words": phrases,
        "short_article_warning": is_short,
        "excessive_punctuation_warning": has_punctuation_warning,
        "writing_pattern_warning": has_pattern_warning,
        "verification_action": "Compare this article with trusted news outlets, official sources, and original evidence before sharing.",
    }
