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
                <h3>🤖 AI Quiz</h3>
                <p>Create quizzes from your documents.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="section-card">
                <h3>📊 Results</h3>
                <p>Review answers and check your score.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Get started")

    if st.button("🚀 Open Quiz Generator", use_container_width=True):
        st.session_state["navigation_target"] = "📝 Quiz Generator"
        st.rerun()


# ---------------- QUIZ GENERATOR ----------------

elif page == "📝 Quiz Generator":

    show_hero()

    st.subheader("Create your quiz")
    st.caption(
        "Upload your study material and customize your quiz settings."
    )

    if not api_key:
        st.warning(
            "Gemini API key is missing. Add GEMINI_API_KEY "
            "in your Streamlit app Secrets."
        )

    uploaded_file = st.file_uploader(
        "📂 Upload your document",
        type=["pdf", "docx", "txt", "md"],
        help="Supported formats: PDF, Word, TXT and Markdown.",
    )

    if uploaded_file:
        st.success(f"Selected file: {uploaded_file.name}")

    col1, col2 = st.columns(2)

    with col1:
        question_count = st.selectbox(
            "Number of questions",
            [5, 10, 15, 20, 30, 50],
            index=1,
        )

        question_type = st.selectbox(
            "Question type",
            ["MCQ", "True/False", "Short Answer"],
        )

    with col2:
        language = st.selectbox(
            "Quiz language",
            ["English", "Urdu"],
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
        )

    if st.button("✨ Generate My Quiz", use_container_width=True):

        if not uploaded_file:
            st.error("Please upload a document first.")

        elif not api_key:
            st.error("Configure your Gemini API key first.")

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

                st.session_state["quiz"] = quiz
                st.session_state["answers"] = {}
                st.session_state["submitted"] = False
                st.session_state["last_result"] = None

                st.success("Your quiz is ready!")

            except Exception as exc:
                st.error(
                    "Unable to generate your quiz. "
                    "Please try again."
                )

                with st.expander("Technical details"):
                    st.code(str(exc))

    quiz = st.session_state.get("quiz")

    if quiz:

        st.divider()
        st.subheader(quiz.get("title", "Your Quiz"))

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
                            "Choose your answer",
                            options,
                            key=f"ua_question_{index}",
                            index=None,
                        )
                    else:
                        selected_answers[index] = st.text_input(
                            "Write your answer",
                            key=f"ua_question_{index}",
                        )

                    st.divider()

                submitted = st.form_submit_button(
                    "Submit My Quiz",
                    use_container_width=True,
                )

                if submitted:
                    st.session_state["answers"] = selected_answers
                    st.session_state["submitted"] = True
                    st.rerun()

        else:

            answers = st.session_state.get("answers", {})
            score = 0

            st.subheader("📊 Quiz Results")

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
                        f"**Your answer:** "
                        f"{user_answer if user_answer else 'Not answered'}"
                    )

                    st.write(f"**Correct answer:** {correct_answer}")

                    if is_correct:
                        st.success("Correct!")
                    else:
                        st.error("Incorrect")

                    explanation = item.get("explanation", "")

                    if explanation:
                        st.info(f"Explanation: {explanation}")

            total = len(questions)
            percentage = score / total * 100 if total else 0

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Score", f"{score}/{total}")

            with col2:
                st.metric("Percentage", f"{percentage:.1f}%")

            with col3:
                st.metric(
                    "Incorrect",
                    str(total - score),
                )

            st.progress(int(percentage))

            if percentage >= 80:
                st.success("Excellent work! 🌟")
            elif percentage >= 50:
                st.info("Good effort! Keep practising. 💪")
            else:
                st.warning("Review the material and try again. 📚")

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

            if st.button("🔄 Take Quiz Again", use_container_width=True):
                st.session_state["answers"] = {}
                st.session_state["submitted"] = False
                st.rerun()


# ---------------- MY RESULTS ----------------

elif page == "📊 My Results":

    show_hero()

    st.subheader("Your latest quiz results")

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
            st.metric("Questions", total)

        st.progress(int(percentage))

        st.download_button(
            "📥 Download Latest Results",
            data=json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            ),
            file_name="ua_quiz_ai_results.json",
            mime="application/json",
            use_container_width=True,
        )

    else:
        st.info(
            "You have no completed quiz results in this session yet. "
            "Generate and submit a quiz to see your results here."
        )


# ---------------- ABOUT ----------------

elif page == "ℹ️ About":

    show_hero()

    st.subheader("About UA Quiz AI")

    st.write(
        """
        **UA Quiz AI** is an AI-powered learning application
        that transforms study documents into interactive quizzes.

        Upload supported documents, select your quiz settings,
        answer the questions, and review your results.
        """
    )

    st.markdown("### Features")

    st.markdown(
        """
        - 📄 PDF, DOCX, TXT and Markdown support
        - 🧠 AI-generated quizzes
        - 🎯 Adjustable difficulty
        - 🌐 English and Urdu options
        - 📊 Instant scoring and explanations
        - 📥 Downloadable quiz results
        """
    )

    st.caption("UA Quiz AI | Learn smarter with AI.")
