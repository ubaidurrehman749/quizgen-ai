import base64
import html as htmllib
import json
import os
from difflib import SequenceMatcher
from pathlib import Path

import streamlit as st

from document_reader import extract_text
from quiz_engine import create_quiz

# ============== PAGE CONFIG ==============

st.set_page_config(
    page_title="PDF to Quiz AI · StudySpark AI",
    page_icon="🧠",
    layout="wide",
)

OWNER_NAME = "Ubaid ur Rehman"

# ============== SESSION STATE ==============

defaults = {
    "quiz": None,
    "answers": {},
    "submitted": False,
    "last_result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

ss = st.session_state


# ============== LOGO ==============

def logo_tag():
    mimes = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }
    for ext, mime in mimes.items():
        p = Path(__file__).parent / f"logo{ext}"
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            return (
                f'<img class="logo" src="data:{mime};base64,{b64}" '
                f'alt="StudySpark AI logo">'
            )
    return '<span class="spark">✦</span>'


# ============== STYLING ==============

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=DM+Sans:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
.block-container { padding-top: 1.2rem; max-width: 1100px; }

.topbar { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;
          padding-bottom:14px; border-bottom:1px solid #DCE4FA; }
.brand { display:flex; align-items:center; gap:12px; font-family:'Bricolage Grotesque',sans-serif;
         font-weight:800; font-size:1.45rem; color:#0F1B3D; }
.brand .logo { height:46px; width:46px; object-fit:contain; border-radius:10px; }
.brand .spark { color:#06B6D4; font-size:1.6rem; }
.brand b { color:#4F46E5; }
.owner { background:#0F1B3D; color:#F2F6FF; padding:8px 16px; border-radius:999px; font-weight:500; font-size:.95rem; }
.owner b { color:#22D3EE; }

.hero h1 { font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:2.4rem;
           line-height:1.1; color:#0F1B3D; margin:1.2rem 0 .3rem; letter-spacing:-.02em; }
.hero p { color:#4A5878; font-size:1.1rem; margin-bottom:.8rem; }

.card { background:#fff; border:1px solid #DCE4FA; border-top:5px solid #4F46E5; border-radius:16px;
        padding:18px 20px; margin-bottom:14px; box-shadow:0 16px 28px -24px rgba(15,27,61,.55); }
.card h3 { font-family:'Bricolage Grotesque',sans-serif; color:#0F1B3D; margin:0 0 6px; font-size:1.15rem; }
.card p { color:#4A5878; margin:0; font-size:.98rem; }

.rev { background:#fff; border:1px solid #DCE4FA; border-left:6px solid #16A34A; border-radius:12px;
       padding:10px 14px; margin:6px 0; color:#0F1B3D; }
.rev.bad { border-left-color:#DC2626; }
.rev small { color:#4A5878; }

div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
    border-radius:12px; font-weight:700; padding:.6rem 1rem; }
div.stButton > button[kind="primary"], div.stDownloadButton > button, div.stFormSubmitButton > button {
    background:#4F46E5; color:#fff; border:0; }
div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button:hover,
div.stFormSubmitButton > button:hover { background:#3D35C4; color:#fff; }
[data-testid="stMetricValue"] { color:#4F46E5; font-family:'Bricolage Grotesque',sans-serif; }
[data-testid="stFileUploader"] { border-radius:14px; }
.stTabs [data-baseweb="tab"] { font-weight:700; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="topbar">
  <div class="brand">{logo_tag()}<span>StudySpark <b>AI</b></span></div>
  <div class="owner">Created by <b>{OWNER_NAME}</b></div>
</div>
<div class="hero">
  <h1>PDF to Quiz AI</h1>
  <p>Upload your notes, get a quiz in seconds, and check your score with explanations.</p>
</div>
""", unsafe_allow_html=True)


# ============== HELPERS ==============

def is_answer_correct(user_answer, correct_answer, has_options):
    if not isinstance(user_answer, str) or not user_answer.strip():
        return False

    user = user_answer.strip().casefold().rstrip(".!? ")
    correct = correct_answer.strip().casefold().rstrip(".!? ")

    if user == correct:
        return True

    if has_options:
        return False

    return SequenceMatcher(None, user, correct).ratio() >= 0.85


def validate_quiz(quiz):
    if not isinstance(quiz, dict):
        raise ValueError("The quiz engine did not return a valid quiz.")

    questions = quiz.get("questions", [])

    if not isinstance(questions, list) or not questions:
        raise ValueError("No valid questions were generated.")

    for index, item in enumerate(questions):
        if not isinstance(item, dict):
            raise ValueError(f"Question {index + 1} has invalid format.")

        if not item.get("question"):
            raise ValueError(f"Question {index + 1} is missing its text.")

        if not isinstance(item.get("answer"), str):
            raise ValueError(f"Question {index + 1} has no valid answer.")


def clear_question_keys():
    for k in [k for k in ss.keys() if k.startswith("ua_question_")]:
        del ss[k]


def evaluate(quiz, answers):
    details = []
    score = 0

    for index, item in enumerate(quiz.get("questions", [])):
        user_answer = answers.get(index)
        if isinstance(user_answer, str):
            user_answer = user_answer.strip()

        ok = is_answer_correct(user_answer, item["answer"], bool(item.get("options")))
        score += 1 if ok else 0

        details.append({
            "question": item["question"],
            "your_answer": user_answer or "",
            "correct_answer": item["answer"],
            "correct": ok,
            "explanation": item.get("explanation", ""),
        })

    total = len(details)
    return {
        "title": quiz.get("title", "Your Quiz"),
        "score": score,
        "total": total,
        "percentage": round(score / total * 100) if total else 0,
        "details": details,
    }


def retry_quiz():
    clear_question_keys()
    ss["answers"] = {}
    ss["submitted"] = False
    ss["last_result"] = None


def new_quiz():
    retry_quiz()
    ss["quiz"] = None


def render_results(result, prefix):
    pct = result["percentage"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Score", f"{result['score']} / {result['total']}")
    m2.metric("Percentage", f"{pct}%")
    m3.metric("Wrong or skipped", result["total"] - result["score"])
    st.progress(pct / 100)

    if pct >= 80:
        st.success("Excellent work. You know this material well.")
    elif pct >= 50:
        st.warning("Good effort. Review the questions you missed and try again.")
    else:
        st.error("Needs more revision. Read your notes again, then retry the quiz.")

    st.download_button(
        "Download results (.json)",
        json.dumps(result, ensure_ascii=False, indent=2),
        file_name="quiz-results.json",
        mime="application/json",
        key=f"dl_{prefix}",
        use_container_width=True,
    )

    st.markdown("#### Review")
    for index, d in enumerate(result["details"], start=1):
        icon = "✅" if d["correct"] else "❌"
        short = d["question"][:80] + ("…" if len(d["question"]) > 80 else "")
        with st.expander(f"{icon} Question {index}: {short}"):
            st.write(d["question"])
            yours = d["your_answer"] or "Not answered"
            st.markdown(
                f'<div class="rev {"" if d["correct"] else "bad"}"><small>Your answer</small><br>'
                f'{htmllib.escape(yours)}</div>'
                f'<div class="rev"><small>Correct answer</small><br>'
                f'{htmllib.escape(d["correct_answer"])}</div>',
                unsafe_allow_html=True,
            )
            if d["explanation"]:
                st.info(d["explanation"])


# ============== API KEY ==============

try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")


# ============== TABS ==============

tab_create, tab_results, tab_about = st.tabs(
    ["① Create & take quiz", "② My results", "③ About"]
)

# ======================= CREATE & TAKE =======================
with tab_create:

    if not api_key:
        st.warning(
            "Gemini API key missing. Add GEMINI_API_KEY to your Streamlit app Secrets."
        )

    uploaded_file = st.file_uploader(
        "📂 Upload your document (PDF, Word, TXT or Markdown)",
        type=["pdf", "docx", "txt", "md"],
        key="ua_document_upload",
    )

    if uploaded_file:
        st.success(f"Selected file: {uploaded_file.name}")

    st.markdown("#### ⚙️ Customize your quiz")

    col1, col2 = st.columns(2)

    with col1:
        question_count = st.selectbox("Number of questions", [5, 10, 15, 20, 30, 50], index=1)
        question_type = st.selectbox("Question type", ["MCQ", "True/False", "Short Answer"])

    with col2:
        language = st.selectbox("Quiz language", ["English", "Urdu"])
        difficulty = st.selectbox("Difficulty level", ["Easy", "Medium", "Hard"])

    if st.button("✨ Generate my quiz", type="primary", use_container_width=True,
                 key="generate_quiz_button"):

        if not uploaded_file:
            st.error("Please upload a document first.")

        elif not api_key:
            st.error("Please configure your Gemini API key first.")

        else:
            try:
                with st.spinner("📖 Reading your document..."):
                    document_text = extract_text(uploaded_file)

                if not document_text or not document_text.strip():
                    raise ValueError(
                        "No readable text found. Please upload a text-based document."
                    )

                with st.spinner("🤖 AI is creating your quiz..."):
                    quiz = create_quiz(
                        api_key=api_key,
                        document_text=document_text,
                        question_count=question_count,
                        question_type=question_type,
                        language=language,
                        difficulty=difficulty,
                    )

                validate_quiz(quiz)

                clear_question_keys()
                ss["quiz"] = quiz
                ss["answers"] = {}
                ss["submitted"] = False
                ss["last_result"] = None

                st.success("🎉 Your quiz is ready!")

            except Exception as exc:
                st.error("Unable to generate your quiz. Please check your settings and try again.")

                with st.expander("Technical details"):
                    st.code(str(exc))

    # ---------- display quiz ----------

    quiz = ss.get("quiz")

    if quiz:

        st.divider()
        st.subheader(f"📚 {quiz.get('title', 'Your Quiz')}")

        questions = quiz.get("questions", [])

        if not ss.get("submitted", False):

            with st.form("ua_quiz_form"):

                selected_answers = {}

                for index, item in enumerate(questions):

                    st.markdown(f"**Question {index + 1}**")
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

                submitted = st.form_submit_button("✅ Submit my quiz", use_container_width=True)

                if submitted:
                    ss["answers"] = selected_answers
                    ss["last_result"] = evaluate(quiz, selected_answers)
                    ss["submitted"] = True
                    st.rerun()

        else:
            result = ss.get("last_result") or evaluate(quiz, ss.get("answers", {}))

            st.markdown("### 📊 Your quiz results")
            render_results(result, "create")

            b1, b2 = st.columns(2)
            b1.button("🔁 Retry this quiz", on_click=retry_quiz, use_container_width=True)
            b2.button("🆕 Create a new quiz", on_click=new_quiz, type="primary",
                      use_container_width=True)

# ======================= MY RESULTS =======================
with tab_results:
    result = ss.get("last_result")

    if not result:
        st.info("No results yet. Create a quiz and submit it to see your score here.")
    else:
        st.subheader(f"📊 {result['title']}")
        render_results(result, "results")

# ======================= ABOUT =======================
with tab_about:
    st.markdown("""
    <div class="card"><h3>📄 Smart upload</h3>
    <p>Upload PDF, Word, TXT or Markdown documents. Scanned PDFs without text are not supported.</p></div>
    <div class="card"><h3>🤖 AI quiz generator</h3>
    <p>Choose MCQ, True/False or Short Answer questions, the language, difficulty and number of questions.</p></div>
    <div class="card"><h3>📊 Instant results</h3>
    <p>See your score, the correct answers and a short explanation for every question.</p></div>
    """, unsafe_allow_html=True)

    st.caption("Powered by Gemini AI. Quizzes are made from your document only. "
               "Always double-check important answers with your textbook.")

st.markdown(
    f"<hr><center style='color:#4A5878'>© StudySpark AI · Created by {OWNER_NAME}</center>",
    unsafe_allow_html=True,
)
