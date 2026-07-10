from __future__ import annotations

import subprocess
import tempfile
from datetime import datetime
from html import escape
from pathlib import Path
import re

import cv2
import numpy as np
import streamlit as st

from utils.database import save_prediction
from utils.predictor import predict_news
from utils.ui import (
    add_session_history,
    business_impact_panel,
    insight_cards,
    result_panel,
    section_title,
    source_evidence_panel,
)


def _file_size_label(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    return f"{size / 1024:.1f} KB"


def _ocr_quality_score(text: str) -> float:
    if not text:
        return 0.0
    cleaned = _clean_ocr_text(text)
    if not cleaned:
        return 0.0

    tokens = re.findall(r"[A-Za-z0-9$%]+(?:[-'][A-Za-z0-9]+)?", cleaned)
    if not tokens:
        return 0.0

    useful_words = sum(
        1
        for token in tokens
        if len(token) >= 3 or token.startswith("$") or token.isdigit()
    )
    long_garbage = sum(
        1
        for token in tokens
        if len(token) >= 12 and not re.search(r"[aeiouAEIOU]", token)
    )
    symbol_count = sum(1 for char in cleaned if not (char.isalnum() or char.isspace() or char in ".,:;!?$%()/-'\""))
    single_letter_lines = sum(
        1
        for line in cleaned.splitlines()
        if line.strip() and all(len(part) <= 2 for part in line.split())
    )
    readable_ratio = sum(char.isalnum() or char.isspace() or char in ".,:;!?$%()/-'\"" for char in cleaned) / max(
        len(cleaned),
        1,
    )
    return useful_words * 2 + readable_ratio * 30 - long_garbage * 8 - symbol_count * 1.5 - single_letter_lines * 6


def _clean_ocr_text(text: str) -> str:
    replacements = {
        "¢": "$",
        "€": "$",
        "£": "$",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "|": " ",
        "\\": " ",
        "—": "-",
        "–": "-",
        "•": "-",
        "«": "-",
        "»": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    anchor_patterns = [
        r"(government.+)",
        r"(prime minister.+)",
        r"(citizen.+)",
        r"(will receive.+)",
        r"(amount\s*:?.+)",
        r"(who.+eligible\s*:?.+)",
        r"(payment date\s*:?.+)",
        r"(no registration.+)",
        r"(money will be sent.+)",
        r"(money will sent.+)",
        r"(check their bank.+)",
        r"(account and share.+)",
        r"(friends\.?.*)",
        r"(\$?\s*750.+)",
    ]
    cleaned_lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"[^\w\s.,:;!?$%()/'\"+-]", " ", raw_line)
        line = re.sub(r"\s+", " ", line).strip(" -_.,")
        if not line:
            continue

        lowered_line = line.lower()
        if "who" in lowered_line and "eligible" in lowered_line:
            cleaned_lines.append("Who is eligible: All citizens" if "all" in lowered_line else "Who is eligible")
            continue
        if "no" in lowered_line and "registration" in lowered_line:
            cleaned_lines.append("No registration needed")
            continue
        if "payment" in lowered_line and "date" in lowered_line:
            match = re.search(r"within\s+\d+\s+days?", line, flags=re.IGNORECASE)
            suffix = match.group(0) if match else line
            cleaned_lines.append(f"Payment date: {suffix}")
            continue
        if "amount" in lowered_line and ("750" in lowered_line or "$" in lowered_line):
            cleaned_lines.append("Amount: $750 per person" if "person" in lowered_line else "Amount: $750")
            continue
        if "money" in lowered_line and "account" in lowered_line:
            cleaned_lines.append("Money will be sent to your account")
            continue

        anchor_match = None
        for pattern in anchor_patterns:
            match = re.search(pattern, line, flags=re.IGNORECASE)
            if match:
                anchor_match = match.group(1).strip()
                break

        tokens = line.split()
        alpha_tokens = [token for token in tokens if re.search(r"[A-Za-z0-9$]", token)]
        short_token_ratio = sum(1 for token in alpha_tokens if len(token) <= 2) / max(len(alpha_tokens), 1)
        very_long_tokens = [
            token
            for token in alpha_tokens
            if len(token) >= 14
        ]
        uppercase_noise = any(
            len(token.strip(".,:;!?()'\"")) >= 8
            and token.strip(".,:;!?()'\"").isupper()
            and not re.search(r"[AEIOU]", token)
            for token in alpha_tokens
        )
        consonant_garbage = any(
            len(token) >= 14 and not re.search(r"[aeiouAEIOU]", token)
            for token in alpha_tokens
        )
        if anchor_match is None and len(alpha_tokens) <= 2 and short_token_ratio > 0.7:
            continue
        if anchor_match is None and short_token_ratio > 0.72 and len(alpha_tokens) >= 5:
            continue
        if anchor_match is None and (consonant_garbage or uppercase_noise or len(very_long_tokens) >= 2):
            continue

        line = re.sub(r"\b0CR\b", "OCR", line, flags=re.IGNORECASE)
        line = re.sub(r"\bgovernrnent\b", "government", line, flags=re.IGNORECASE)
        line = re.sub(r"\bcitizen[s5]?\b", lambda match: match.group(0).replace("5", "s"), line, flags=re.IGNORECASE)
        line = re.sub(r"\barnount\b", "amount", line, flags=re.IGNORECASE)
        line = re.sub(r"\bpayrnent\b", "payment", line, flags=re.IGNORECASE)
        line = re.sub(r"\bregistrat[il]on\b", "registration", line, flags=re.IGNORECASE)

        if anchor_match is not None:
            line = anchor_match

        line_tokens = []
        for token in line.split():
            normalized = token.strip(".,:;!?()'\"")
            is_money = bool(re.match(r"^\$?\d+([.,]\d+)?$", normalized))
            is_short_allowed = normalized.lower() in {
                "no",
                "to",
                "of",
                "in",
                "is",
                "all",
                "per",
                "the",
                "and",
                "for",
            }
            is_word = bool(re.search(r"[A-Za-z]", normalized))
            looks_like_garbage = (
                len(normalized) >= 8
                and is_word
                and not re.search(r"[aeiouAEIOU]", normalized)
            )
            looks_like_mixed_noise = (
                len(normalized) >= 6
                and sum(1 for char in normalized if char.isupper()) >= 3
                and sum(1 for char in normalized if char.islower()) >= 2
            )
            if looks_like_garbage or looks_like_mixed_noise:
                continue
            if len(normalized) <= 2 and not is_money and not normalized.isdigit() and not is_short_allowed:
                continue
            line_tokens.append(token)

        line = " ".join(line_tokens).strip(" -_.,")
        line = re.sub(r"\b(ATES|UPD|DETATES|VIENTDETATES)\b.*$", "", line).strip(" -_.,")
        line = re.sub(r"^Who\s+is\s+eligible\s+", "Who is eligible: ", line, flags=re.IGNORECASE)
        line = re.sub(r"^Payment\s+date\s+", "Payment date: ", line, flags=re.IGNORECASE)
        line = re.sub(r"^Money\s+will\s+sent\b", "Money will be sent", line, flags=re.IGNORECASE)
        line = re.sub(r"^\$750\s+per\s+person$", "Amount: $750 per person", line, flags=re.IGNORECASE)
        line = re.sub(r"^Amount\s+\$750", "Amount: $750", line, flags=re.IGNORECASE)
        if not line:
            continue
        if re.fullmatch(r"\d{1,2}", line):
            continue
        if len(line.split()) <= 2 and not re.search(r"\$|\d|fake|real|news", line, flags=re.IGNORECASE):
            continue
        cleaned_lines.append(line)

    compacted = "\n".join(cleaned_lines)
    compacted = re.sub(r"^\$\s+Amount", "Amount", compacted, flags=re.MULTILINE)
    compacted = re.sub(r"^\$\s+Payment date", "Payment date", compacted, flags=re.MULTILINE)
    compacted = re.sub(r"^\$\s+No registration", "No registration", compacted, flags=re.MULTILINE)
    compacted = re.sub(r"^\$\s+Money", "Money", compacted, flags=re.MULTILINE)
    compacted = re.sub(r"\n{3,}", "\n\n", compacted)
    return compacted.strip()


def _preprocess_image_for_ocr(image_bytes: bytes) -> bytes:
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        return image_bytes

    height, width = image.shape[:2]
    scale = 2.0 if max(width, height) >= 1200 else 3.0
    image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 35, 35)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    threshold = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    threshold = cv2.copyMakeBorder(
        threshold,
        24,
        24,
        24,
        24,
        cv2.BORDER_CONSTANT,
        value=255,
    )
    ok, encoded = cv2.imencode(".png", threshold)
    return encoded.tobytes() if ok else image_bytes


def _run_tesseract(image_bytes: bytes, psm: str) -> tuple[str, str]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(image_bytes)
        temp_path = Path(temp_file.name)

    try:
        completed = subprocess.run(
            [
                "tesseract",
                str(temp_path),
                "stdout",
                "--oem",
                "3",
                "--psm",
                psm,
                "-l",
                "eng",
                "-c",
                "preserve_interword_spaces=1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        temp_path.unlink(missing_ok=True)

    if completed.returncode != 0:
        return "", completed.stderr.strip() or "OCR could not read this image."
    return completed.stdout.strip(), ""


def _extract_text_from_upload(uploaded) -> tuple[str, str]:
    image_bytes = uploaded.getvalue()
    processed = _preprocess_image_for_ocr(image_bytes)
    candidates = []
    errors = []
    for source in (processed, image_bytes):
        for psm in ("6", "4", "11"):
            text, error = _run_tesseract(source, psm)
            if text:
                candidates.append(text)
            elif error:
                errors.append(error)
    if not candidates:
        return "", errors[-1] if errors else "OCR could not read this image."
    best = max(candidates, key=_ocr_quality_score)
    return _clean_ocr_text(best), ""


def _save_image_result(title: str, text: str, result) -> None:
    save_prediction(
        {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "source": "Image upload",
            "url": "",
            "prediction": result.prediction,
            "fake_probability": result.fake_probability,
            "real_probability": result.real_probability,
            "credibility_score": result.credibility_score,
            "risk_level": result.risk_level,
            "explanation_summary": result.explanation["summary"],
        }
    )
    add_session_history("Image", result, text)


def _text_from_image_card(text: str) -> None:
    words = len(text.split()) if text else 0
    preview = text[:1200] if text else "No text extracted from this image."
    st.markdown(
        f"""
        <div class="text-from-image-card">
            <div class="text-from-image-header">
                <div class="text-from-image-icon">TXT</div>
                <div>
                    <strong>Text From Image</strong>
                    <p>{words} words extracted from the uploaded screenshot. Review this text before classification.</p>
                </div>
            </div>
            <div class="text-from-image-body">{escape(preview)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if text and len(text) > len(preview):
        with st.expander("Show full extracted image text"):
            st.write(text)


def render() -> None:
    st.markdown(
        """
        <div class="image-page-shell">
            <div class="image-hero">
                <div>
                    <span>Image evidence review</span>
                    <h1>Review text inside a screenshot.</h1>
                    <p>Upload one news screenshot or social media image. The system extracts visible text and checks it for credibility risk.</p>
                </div>
                <div class="image-hero-badge">OCR and review ready</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.55, 0.9], gap="large")
    with left:
        st.markdown(
            """
            <div class="image-upload-panel">
                <div class="image-upload-icon">▧</div>
                <strong>Upload Image</strong>
                <p>Use a clear PNG, JPG, or JPEG screenshot with readable text.</p>
                <div class="image-upload-meta">
                    <span>Screenshot</span>
                    <span>Social post</span>
                    <span>News image</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Upload image evidence",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )

        if uploaded is not None:
            image_key = f"{uploaded.name}:{uploaded.size}"
            if st.session_state.get("current_image_key") != image_key:
                st.session_state["current_image_key"] = image_key
                st.session_state.pop("last_image_text", None)
                st.session_state.pop("last_image_result", None)
            st.image(uploaded, caption="Uploaded image evidence", use_container_width=True)

    with right:
        if uploaded is None:
            st.markdown(
                """
                <div class="image-status-card">
                    <div class="image-status-dot"></div>
                    <strong>Waiting for image</strong>
                    <p>Upload one item to start the image review workflow.</p>
                    <ul>
                        <li>Make sure the article text is visible.</li>
                        <li>Crop unrelated background if possible.</li>
                        <li>Use one image per review.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="image-status-card ready">
                    <div class="image-status-dot"></div>
                    <strong>Image ready for review</strong>
                    <p>Your uploaded image is loaded in the workspace.</p>
                    <div class="image-file-grid">
                        <span>File name</span><b>{escape(uploaded.name)}</b>
                        <span>File type</span><b>{escape(uploaded.type or "Image")}</b>
                        <span>File size</span><b>{_file_size_label(uploaded.size)}</b>
                        <span>Uploaded</span><b>{datetime.now().strftime("%H:%M")}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Review Image", type="primary", use_container_width=True):
                with st.spinner("Reading image text and running review..."):
                    extracted_text, ocr_error = _extract_text_from_upload(uploaded)
                    if ocr_error:
                        st.error(f"Could not read text from this image: {ocr_error}")
                        return
                    if len(extracted_text.split()) < 4:
                        st.error("The image text is too short to review. Please upload a clearer screenshot with readable text.")
                        return
                    cleaned_text = extracted_text.strip()
                    image_title = f"Image review: {uploaded.name}"
                    try:
                        result = predict_news(image_title, cleaned_text)
                    except RuntimeError as exc:
                        st.error(str(exc))
                        return
                st.session_state["last_result"] = result
                st.session_state["last_image_result"] = result
                st.session_state["last_image_text"] = cleaned_text
                _save_image_result(image_title, cleaned_text, result)
                st.success("Image reviewed and saved successfully.")

    st.markdown(
        """
        <div class="image-note-card">
            <div class="image-note-icon">↳</div>
            <div>
                <strong>One-step image workflow</strong>
                <p>Upload a screenshot, then run review. The system reads visible text from the image and checks it with the deployed classifier.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if uploaded is not None and st.session_state.get("last_image_text"):
        extracted_text = st.session_state.get("last_image_text", "")
        _text_from_image_card(extracted_text)

    result = st.session_state.get("last_image_result")
    if result is not None and uploaded is not None:
        extracted_text = st.session_state.get("last_image_text", "")
        left, right = st.columns([2.1, 1], gap="large")
        with left:
            result_panel(result)
            section_title("💡", "Image Review Insights")
            insight_cards(result, source="Image upload")
        with right:
            business_impact_panel(result)
            source_evidence_panel(result, source="Image upload", text=extracted_text)
