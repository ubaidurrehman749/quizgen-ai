import json
import os
import streamlit as st

from document_reader import extract_text
from quiz_engine import create_quiz


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="UA Quiz AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- SESSION STATE ----------------

if "quiz" not in st.session_state:
    st.session_state["quiz"] = None

if "answers" not in st.session_state:
    st.session_state["answers"] = {}

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False


# ---------------- CUSTOM DESIGN ----------------

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    .stApp {
        background: linear-gradient(
            135deg,
            #0b1020 0%,
            #10172d 55%,
            #15132e 100%
        );
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 16, 32, 0.85);
    }

    [data-testid="stSidebar"] {
        background: #10172d;
        border-right: 1px solid #273451;
    }

    .hero-card {
        background: linear-gradient(
            135deg,
            #182448,
            #30205b
        );
        border: 1px solid #493c82;
        padding: 32px 24px;
        border-radius: 22px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
    }

    .hero-title {
        font-size: clamp(30px, 5vw, 48px);
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }

    .hero-title span {
        color: #a78bfa;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.7;
    }

    .section-card {
        background: rgba(24, 36, 65, 0.72);
        border: 1px solid #2b3b60;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .section-label {
        color: #a78bfa;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .small-note {
        color: #a5b4cc;
        font-size: 13px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 12px;
        border: 1px solid #8b5cf6;
        background: linear-gradient(
            100deg,
            #7c3aed,
            #4f46e5
        );
        color: white;
        font-weight: 700;
        min-height: 45px;
        transition: 0.2s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        border-color: #67e8f9;
        color: white;
        filter: brightness(1.12);
    }

    div[data-testid="stFileUploader"] {
        background: rgba(24, 36, 65, 0.55);
        border: 1px dashed #6754a5;
        border-radius: 14px;
        padding: 12px;
    }

    div[data-testid="stMetric"] {
        background: rgba(24, 36, 65, 0.78);
        border: 1px solid #33446b;
        border-radius: 14px;
        padding: 18px;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    p, label, li {
        color: #e2e8f0;
    }

    hr {
        border-color: #2b3b60;
    }

    @media (max-width: 640px) {
        .hero-card {
            padding: 24px 14px;
        }

        .hero-subtitle {
            font-size: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🧠 UA Quiz AI")
    st.caption("Your AI-powered learning companion")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Home",
            "📝 Quiz Generator",
            "📊 My Results",
            "ℹ️ About",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("**Powered by Gemini AI**")
    st.caption("Upload. Generate. Learn.")


# ---------------- API KEY ----------------

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")


# ---------------- HERO ----------------

def show_hero():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">
                UA <span>Quiz AI</span> 🧠
            </div>
            <div class="hero-subtitle">
                Transform your documents into interactive quizzes.<br>
                Learn smarter. Practice better. Achieve more.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------- HOME ----------------

if page == "🏠 Home":

    show_hero()

    st.subheader("Welcome to your AI learning workspace")

    st.write(
        "Generate quizzes from your own study materials, "
        "test your knowledge, and review your performance."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="section-card">
                <h3>📄 Smart Upload</h3>
                <p>Upload PDF, Word or text files.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="section-card">
                <
