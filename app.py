import json
import os
import streamlit as st

from document_reader import extract_text
from quiz_engine import create_quiz


st.set_page_config(
    page_title="QuizGen AI",
    page_icon="🧠",
    layout="centered",
)


st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        text-align: center;
    }

    .subtitle {
        text-align: center;
        color: gray;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">🧠 QuizGen AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Turn your documents into interactive quizzes.'
    '</div>',
    unsafe_allow_html=True,
)


# Read API key from Streamlit secrets or environment.
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

api_key = api_key or os.getenv("GEMINI_API_KEY", "")


if not api_key:
    st.warning(
        "Gemini API key is not configured. "
        "Add GEMINI_API_KEY to Streamlit secrets."
    )


st.header("1. Upload your document")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "docx", "txt", "md"],
    help="Upload a readable PDF, Word or text document.",
)


st.header("2. Quiz settings")

question_count = st.selectbox(
    "Number of questions",
    [5, 10, 15, 20, 30, 50],
    index=1,
)

question_type = st.selectbox(
    "Question type",
    ["MCQ", "True/False", "Short Answer"],
)

language = st.selectbox(
    "Quiz language",
    ["English", "Urdu"],
)

difficulty = st.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"],
)


if uploaded_file is not None:
    st.info(f"Selected file: {uploaded_file.name}")


if st.button("🚀 Generate Quiz", use_container_width=True):

    if not uploaded_file:
        st.error("Please upload a document first.")

    elif not api_key:
        st.error(
            "API key missing. Configure GEMINI_API_KEY "
            "in Streamlit secrets."
        )

    else:
        try:
            with st.spinner("Reading your document..."):
                document_text = extract_text(uploaded_file)

            st.success(
                f"Document read successfully: "
                f"{len(document_text):,} characters"
            )

            with st.spinner("AI is generating your quiz..."):
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

            st.success("Quiz generated successfully!")

        except Exception as exc:
            st.error(
                "Unable to generate the quiz. "
                "Check your API key, model availability, "
                "document and internet connection."
            )

            with st.expander("Technical details"):
                st.code(str(exc))


quiz = st.session_state.get("quiz")


if quiz:

    st.divider()

    st.header(quiz.get("title", "Your Quiz"))

    questions = quiz.get("questions", [])

    if not st.session_state.get("submitted", False):

        with st.form("quiz_form"):

            selected_answers = {}

            for index, item in enumerate(questions):

                question = item["question"]
                options = item["options"]

                st.subheader(f"Question {index + 1}")
                st.write(question)

                if options:
                    selected_answers[index] = st.radio(
                        "Select your answer",
                        options=options,
                        key=f"question_{index}",
                        index=None,
                    )

                else:
                    selected_answers[index] = st.text_input(
                        "Your answer",
                        key=f"question_{index}",
                    )

                st.write("")

            submitted = st.form_submit_button(
                "Submit Quiz",
                use_container_width=True,
            )

            if submitted:
                st.session_state["answers"] = selected_answers
                st.session_state["submitted"] = True
                st.rerun()

    else:

        answers = st.session_state.get("answers", {})
        score = 0

        st.header("📊 Your Results")

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

            st.subheader(f"Question {index + 1}")
            st.write(item["question"])

            if user_answer:
                st.write(f"Your answer: {user_answer}")
            else:
                st.write("Your answer: Not answered")

            st.write(f"Correct answer: {correct_answer}")

            if is_correct:
                st.success("Correct answer!")
            else:
                st.error("Incorrect answer")

            explanation = item.get("explanation", "")

            if explanation:
                st.info(f"Explanation: {explanation}")

        percentage = (
            score / len(questions) * 100
            if questions else 0
        )

        st.metric(
            "Final Score",
            f"{score} / {len(questions)}",
        )

        st.progress(int(percentage))

        st.write(f"Percentage: {percentage:.1f}%")

        if percentage >= 80:
            st.success("Excellent performance!")
        elif percentage >= 50:
            st.info("Good effort! Keep practising.")
        else:
            st.warning("Review the material and try again.")

        st.download_button(
            "📥 Download Quiz Results",
            data=json.dumps(
                {
                    "quiz": quiz,
                    "answers": {
                        str(key): value
                        for key, value in answers.items()
                    },
                    "score": score,
                    "total": len(questions),
                    "percentage": round(percentage, 2),
                },
                ensure_ascii=False,
                indent=2,
            ),
            file_name="quiz_results.json",
            mime="application/json",
            use_container_width=True,
        )

        if st.button(
            "🔄 Try Again",
            use_container_width=True,
        ):
            st.session_state["answers"] = {}
            st.session_state["submitted"] = False
            st.rerun()
