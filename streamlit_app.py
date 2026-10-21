from pathlib import Path

import joblib
import streamlit as st


st.set_page_config(
    page_title="AI Phishing & Spam Detector",
    page_icon="🛡️",
    layout="centered",
)


MODEL_PATH = Path(__file__).parent / "backend" / "model" / "advanced_phishing_model.pkl"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def extract_advanced_features(text):
    text_lower = text.lower()

    urgency_words = [
        "48 hours",
        "24 hours",
        "immediately",
        "urgent",
        "suspended",
        "permanently removed",
        "action required",
        "block",
    ]
    billing_words = [
        "update payment",
        "billing information",
        "verify your identity",
        "click the link",
        "invoice",
        "login here",
        "click here",
    ]
    safe_keywords = [
        "frontier language models",
        "researchers",
        "provenance",
        "benchmarks",
        "word choice",
        "tone",
        "sentence structure",
    ]

    has_urgency = any(word in text_lower for word in urgency_words)
    has_billing = any(word in text_lower for word in billing_words)
    is_educational_or_safe = any(word in text_lower for word in safe_keywords)

    return has_urgency, has_billing, is_educational_or_safe


def predict_message(model_pipeline, user_text):
    prediction = int(model_pipeline.predict([user_text])[0])
    probabilities = model_pipeline.predict_proba([user_text])[0]

    has_urgency, has_billing, is_educational_or_safe = extract_advanced_features(user_text)

    is_spam = False
    confidence = float(probabilities[0] * 100)
    reason = "The message appears safe, normal, and informative."

    if is_educational_or_safe and not has_urgency and not has_billing:
        confidence = max(confidence, 90.0)
        reason = "Research and technical information (safe educational content)"
    elif (has_urgency and has_billing) or prediction == 1:
        is_spam = True
        confidence = float(probabilities[1] * 100) if prediction == 1 else 95.0

        reasons = []
        if has_urgency:
            reasons.append("Urgency trigger (pressure to take immediate action)")
        if has_billing:
            reasons.append(
                "Billing/credential hazard (request for sensitive payment or login information)"
            )
        if not reasons:
            reasons.append("AI pattern detection")
        reason = " | ".join(reasons)

    return is_spam, round(confidence, 2), reason


st.title("🛡️ Advanced AI Phishing Detector")
st.write("Paste your suspicious email or SMS text below:")

email_text = st.text_area(
    "Message text",
    height=180,
    placeholder="e.g. Dear Customer, your account is suspended. Click here to verify...",
    label_visibility="collapsed",
)

if st.button("🚀 Scan with AI", type="primary", use_container_width=True):
    if not email_text.strip():
        st.warning("Please type or paste some text first.")
    else:
        try:
            model_pipeline = load_model()
            is_spam, confidence, reason = predict_message(model_pipeline, email_text.strip())

            if is_spam:
                st.error("🚨 Alert: Phishing / Spam Detected!")
            else:
                st.success("✅ Safe: Legitimate message detected")

            st.metric("Confidence", f"{confidence}%")
            st.info(f"Reason: {reason}")
        except Exception as error:
            st.error(f"Unable to load or run the detection model: {error}")
