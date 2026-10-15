import json
import os
import streamlit as st

from document_reader import extract_text
from quiz_engine import create_quiz

==================================================

PAGE CONFIGURATION

==================================================

st.set_page_config(
page_title="UA Quiz AI",
page_icon="🧠",
layout="wide",
initial_sidebar_state="expanded",
)

==================================================

SESSION STATE

==================================================

defaults = {
"quiz": None,
"answers": {},
"submitted": False,
"last_result": None,
"navigation_target": None,
}

for key, value in defaults.items():
if key not in st.session_state:
st.session_state[key] = value

==================================================

CUSTOM CSS

==================================================

st.markdown(
"""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

:root {
    --ua-purple: #8b5cf6;
    --ua-cyan: #67e8f9;
    --ua-bg: #0b1020;
    --ua-card: #182441;
    --ua-border: #33446b;
    --ua-text: #f1f5f9;
    --ua-muted: #a5b4cc;
}

.stApp {
    background: linear-gradient(
        135deg,
        #0b1020 0%,
        #10172d 55%,
        #15132e 100%
    );
    color: var(--ua-text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(11, 16, 32, 0.85);
}

[data-testid="stSidebar"] {
    background: #10172d;
    border-right: 1px solid #273451;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #e2e8f0;
}

/* HEADER */

.ua-header {
    background: linear-gradient(
        120deg,
        #111827 0%,
        #312e81 55%,
        #6d28d9 100%
    );
    border: 1px solid #6754a5;
    border-radius: 20px;
    padding: 25px 16px;
    margin: 0 0 28px 0;
    text-align: center;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.22);
}

.ua-header-brand {
    font-size: clamp(27px, 5vw, 43px);
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1px;
    margin: 0;
    line-height: 1.3;
}

.ua-header-brand span {
    color: #a5f3fc;
}

.ua-header-tagline {
    color: #ddd6fe;
    font-size: 14px;
    line-height: 1.7;
    margin-top: 8px;
}

.ua-header-badge {
    display: inline-block;
    color: #e0f2fe;
    background: rgba(103, 232, 249, 0.12);
    border: 1px solid rgba(103, 232, 249, 0.35);
    padding: 5px 12px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 12px;
}

/* HERO */

.hero-card {
    background: linear-gradient(
        135deg,
        #182448,
        #30205b
    );
    border: 1px solid #493c82;
    padding: 28px 20px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.16);
}

.hero-title {
    font-size: clamp(27px, 4vw, 42px);
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
    font-size: 15px;
    line-height: 1.8;
}

/* CONTENT CARDS */

.section-card {
    background: rgba(24, 36, 65, 0.78);
    border: 1px solid #33446b;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    min-height: 125px;
    transition: border-color 0.2s ease;
}

.section-card:hover {
    border-color: #8b5cf6;
}

.section-card h3 {
    color: #c4b5fd !important;
    font-size: 19px;
    margin-top: 0;
}

.section-card p {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 0;
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

/* BUTTONS */

div.stButton > button,
div.stFormSubmitButton > button,
div.stDownloadButton > button {
    border-radius: 12px;
    border: 1px solid #8b5cf6;
    background: linear-gradient(
        100deg,
        #7c3aed,
        #4f46e5
    );
    color: #ffffff;
    font-weight: 700;
    min-height: 44px;
    transition: 0.2s ease;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover,
div.stDownloadButton > button:hover {
    border-color: #67e8f9;
    color: #ffffff;
    filter: brightness(1.12);
}

/* FILE UPLOADER */

div[data-testid="stFileUploader"] {
    background: rgba(24, 36, 65, 0.55);
    border: 1px dashed #6754a5;
    border-radius: 14px;
    padding: 12px;
}

/* METRICS */

div[data-testid="stMetric"] {
    background: rgba(24, 36, 65, 0.78);
    border: 1px solid #33446b;
    border-radius: 14px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #c4b5fd;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}

/* FORM ELEMENTS */

div[data-baseweb="select"] > div {
    background-color: #182441;
    border-color: #493c82;
    border-radius: 10px;
}

div[data-testid="stTextInput"] input {
    background-color: #182441;
    color: #ffffff;
    border-color: #493c82;
    border-radius: 10px;
}

div[role="radiogroup"] {
    gap: 8px;
}

/* GENERAL */

h1, h2, h3 {
    color: #f8fafc !important;
}

p, label, li {
    color: #e2e8f0;
}

hr {
    border-color: #2b3b60;
}

/* FOOTER */

.ua-footer {
    background: linear-gradient(
        135deg,
        #111827,
        #1e1b4b
    );
    border: 1px solid #373064;
    border-top: 3px solid #8b5cf6;
    border-radius: 16px;
    padding: 24px 14px;
    text-align: center;
    margin-top: 50px;
    margin-bottom: 8px;
}

.ua-footer-brand {
    font-size: 23px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}

.ua-footer-brand span {
    color: #a5f3fc;
}

.ua-footer-description {
    color: #cbd5e1;
    font-size: 13px;
    margin: 7px 0;
    line-height: 1.7;
}

.ua-footer-credit {
    color: #c4b5fd;
    font-size: 13px;
    margin-top: 15px;
}

.ua-footer-name {
    color: #a5f3fc;
    font-size: 17px;
    font-weight: 800;
    margin: 6px 0 14px 0;
}

.ua-footer-copyright {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 12px;
}

@media (max-width: 640px) {
    .ua-header {
        padding: 22px 12px;
        border-radius: 15px;
    }

    .ua-header-tagline {
        font-size: 12px;
    }

    .hero-card {
        padding: 22px 12px;
    }

    .hero-subtitle {
        font-size: 13px;
    }

    .section-card {
        padding: 15px;
        min-height: auto;
    }

    .ua-footer {
        padding: 20px 10px;
    }
}
</style>
""",
unsafe_allow_html=True,

)

==================================================

HEADER

==================================================

def show_header():
st.markdown(
"""
<div class="ua-header">
<div class="ua-header-badge">
✦ AI-POWERED LEARNING PLATFORM
</div>
<div class="ua-header-brand">
🧠 UA <span>Quiz AI</span>
</div>
<div class="ua-header-tagline">
Transform Documents into Smart Interactive Quizzes
<br>
Learn Smarter. Practice Better. Achieve More.
</div>
</div>
""",
unsafe_allow_html=True,
)

==================================================

FOOTER

==================================================

def show_footer():
st.markdown(
"""
<div class="ua-footer">
<div class="ua-footer-brand">
🧠 UA <span>Quiz AI</span>
</div>

        <div class="ua-footer-description">
            AI-Powered Smart Quiz Generator
        </div>

        <div class="ua-footer-credit">
            Designed &amp; Developed with ❤️ by
        </div>

        <div class="ua-footer-name">
            Ubaid Ur Rehman
        </div>

        <div class="ua-footer-description">
            Learn smarter with the power of Artificial Intelligence.
        </div>

        <div class="ua-footer-copyright">
            © 2026 UA Quiz AI. All Rights Reserved.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

==================================================

HERO

==================================================

def show_hero():
st.markdown(
"""
<div class="hero-card">
<div class="hero-title">
Welcome to <span>UA Quiz AI</span> 🧠
</div>
<div class="hero-subtitle">
Turn your study material into interactive quizzes.
<br>
Test your knowledge and track your performance.
</div>
</div>
""",
unsafe_allow_html=True,
)

==================================================

API KEY

==================================================

try:
api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")

==================================================

SIDEBAR NAVIGATION

==================================================

with st.sidebar:
st.markdown("## 🧠 UA Quiz AI")
st.caption("Your AI-powered learning companion")
st.divider()

navigation_options = [
    "🏠 Home",
    "📝 Quiz Generator",
    "📊 My Results",
    "ℹ️ About",
]

current_target = st.session_state.get("navigation_target")

if current_target in navigation_options:
    default_index = navigation_options.index(current_target)
else:
    default_index = 0

page = st.radio(
    "NAVIGATION",
    navigation_options,
    index=default_index,
    key="ua_navigation",
    label_visibility="collapsed",
)

st.session_state["navigation_target"] = page

st.divider()

st.markdown("**⚡ Powered by Gemini AI**")
st.caption("Upload. Generate. Learn.")

st.divider()

st.caption("Created by Ubaid Ur Rehman")

==================================================

DISPLAY HEADER

==================================================

show_header()

==================================================

HOME

==================================================

if page == "🏠 Home":

show_hero()

st.subheader("Welcome to Your AI Learning Workspace")

st.write(
    "Generate quizzes from your study materials, "
    "test your knowledge, and review your performance."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="section-card">
            <h3>📄 Smart Upload</h3>
            <p>
                Upload supported PDF, Word, text
                and Markdown documents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="section-card">
            <h3>🤖 AI Quiz Generator</h3>
            <p>
                Turn your documents into personalized
                interactive quizzes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="section-card">
            <h3>📊 Instant Results</h3>
            <p>
                Check your score, review correct answers
                and understand explanations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### 🚀 Ready to Get Started?")

st.write(
    "Choose your quiz settings and generate your first quiz."
)

if st.button(
    "🚀 Open Quiz Generator",
    use_container_width=True,
    key="home_open_generator",
):
    st.session_state["navigation_target"] = "📝 Quiz Generator"
    st.session_state["ua_navigation"] = "📝 Quiz Generator"
    st.rerun()

==================================================

QUIZ GENERATOR

==================================================

elif page == "📝 Quiz Generator":

show_hero()

st.subheader("📝 Create Your Quiz")

st.caption(
    "Upload your study material and customize your quiz settings."
)

if not api_key:
    st.warning(
        "Gemini API key is missing. Add GEMINI_API_KEY "
        "to your Streamlit app Secrets."
    )

uploaded_file = st.file_uploader(
    "📂 Upload Your Document",
    type=["pdf", "docx", "txt", "md"],
    help="Supported formats: PDF, Word, TXT and Markdown.",
    key="ua_document_upload",
)

if uploaded_file:
    st.success(f"Selected file: {uploaded_file.name}")

st.markdown("### ⚙️ Customize Your Quiz")

col1, col2 = st.columns(2)

with col1:
    question_count = st.selectbox(
        "Number of Questions",
        [5, 10, 15, 20, 30, 50],
        index=1,
    )

    question_type = st.selectbox(
        "Question Type",
        ["MCQ", "True/False", "Short Answer"],
    )

with col2:
    language = st.selectbox(
        "Quiz Language",
        ["English", "Urdu"],
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
    )

if st.button(
    "✨ Generate My Quiz",
    use_container_width=True,
    key="generate_quiz_button",
):

    if not uploaded_file:
        st.error("Please upload a document first.")

    elif not api_key:
        st.error("Please configure your Gemini API key first.")

    else:
        try:
            with st.spinner("📖 Reading your document..."):
                document_text = extract_text(uploaded_file)

            if not document_text or not document_text.strip():
                st.error(
                    "No readable text found. "
                    "Please upload a text-based document."
                )
                st.stop()

            with st.spinner("🤖 AI is creating your quiz..."):
                quiz = create_quiz(
                    api_key=api_key,
                    document_text=document_text,
                    question_count=question_count,
                    question_type=question_type,
                    language=language,
                    difficulty=difficulty,
                )

            if not isinstance(quiz, dict):
                raise ValueError(
                    "The quiz engine did not return a valid quiz object."
                )

            questions = quiz.get("questions", [])

            if not isinstance(questions, list) or not questions:
                raise ValueError(
                    "No valid questions were returned. Please try again."
                )

            for index, item in enumerate(questions):
                if not isinstance(item, dict):
                    raise ValueError(
                        f"Question {index + 1} has an invalid format."
                    )

                if not item.get("question"):
                    raise ValueError(
                        f"Question {index + 1} has no question text."
                    )

                if not isinstance(item.get("answer"), str):
                    raise ValueError(
                        f"Question {index + 1} has no valid answer."
                    )

                if not isinstance(item.get("options", []), list):
                    raise ValueError(
                        f"Question {index + 1} has invalid options."
                    )

            st.session_state["quiz"] = quiz
            st.session_state["answers"] = {}
            st.session_state["submitted"] = False
            st.session_state["last_result"] = None

            st.success("🎉 Your quiz is ready!")

        except Exception as exc:
            st.error(
                "Unable to generate your quiz. "
                "Please check your settings and try again."
            )

            with st.expander("Technical Details"):
                st.code(str(exc))

# DISPLAY CURRENT QUIZ

quiz = st.session_state.get("quiz")

if quiz:

    st.divider()

    st.subheader(
        f"📚 {quiz.get('title', 'Your Quiz')}"
    )

    questions = quiz.get("questions", [])

    if not st.session_state.get("submitted", False):

        with st.form("ua_quiz_form"):

            selected_answers = {}

            for index, item in enumerate(questions):

                st.markdown(f"### Question {index + 1}")

                st.write(item["question"])

                options = item.get("options", [])

                if options:
                    selected_answers[index] = st.radio(
                        "Choose Your Answer",
                        options,
                        key=f"ua_question_{index}",
                        index=None,
                    )
                else:
                    selected_answers[index] = st.text_input(
                        "Write Your Answer",
                        key=f"ua_question_{index}",
                    )

                st.divider()

            submitted = st.form_submit_button(
                "✅ Submit My Quiz",
                use_container_width=True,
            )

            if submitted:
                st.session_state["answers"] = selected_answers
                st.session_state["submitted"] = True
                st.rerun()

    else:

        answers = st.session_state.get("answers", {})
        score = 0

        st.subheader("📊 Your Quiz Results")

        for index, item in enumerate(questions):

            user_answer = answers.get(index)
            correct_answer = item["answer"]

            if isinstance(user_answer, str):
                user_answer = user_answer.strip()

            is_correct = (
                isinstance(user_answer, str)
                and user_answer.casefold()
                == correct_answer.strip().casefold()
            )

            if is_correct:
                score += 1

            with st.container(border=True):

                st.markdown(f"### Question {index + 1}")

                st.write(item["question"])

                st.write(
                    "**Your Answer:** "
                    f"{user_answer if user_answer else 'Not answered'}"
                )

                st.write(f"**Correct Answer:** {correct_answer}")

                if is_correct:
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect")

                explanation = item.get("explanation", "")

                if explanation:
                    st.info(f"💡 Explanation: {explanation}")

        total = len(questions)

        percentage = (
            score / total * 100
            if total
            else 0
        )

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Score", f"{score}/{total}")

        with col2:
            st.metric("Percentage", f"{percentage:.1f}%")

        with col3:
            st.metric("Incorrect", str(total - score))

        st.progress(int(percentage))

        if percentage >= 80:
            st.success("🌟 Excellent work! Keep it up.")
        elif percentage >= 50:
            st.info("💪 Good effort! Keep practising.")
        else:
            st.warning(
                "📚 Review the material and try again."
            )

        result_data = {
            "quiz": quiz,
            "answers": {
                str(key): value
                for key, value in answers.items()
            },
            "score": score,
            "total": total,
            "percentage": round(percentage, 2),
        }

        st.session_state["last_result"] = result_data

        st.download_button(
            "📥 Download Results (JSON)",
            data=json.dumps(
                result_data,
                ensure_ascii=False,
                indent=2,
            ),
            file_name="ua_quiz_ai_results.json",
            mime="application/json",
            use_container_width=True,
        )

        if st.button(
            "🔄 Take Quiz Again",
            use_container_width=True,
            key="take_quiz_again",
        ):
            st.session_state["answers"] = {}
            st.session_state["submitted"] = False
            st.rerun()

==================================================

MY RESULTS

==================================================

elif page == "📊 My Results":

show_hero()

st.subheader("📊 Your Latest Quiz Results")

result = st.session_state.get("last_result")

if result:

    total = result.get("total", 0)
    score = result.get("score", 0)
    percentage = result.get("percentage", 0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score", f"{score}/{total}")

    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")

    with col3:
        st
