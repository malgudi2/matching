import streamlit as st
import json
import random
import hashlib
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Bhagavad Gita Learning Game",
    layout="centered"
)

st.title("🕉️ Bhagavad Gita – Learning Game")
st.subheader("Match the Sanskrit term with the correct explanation")

# ---------------- CONSTANTS ----------------
NUM_QUESTIONS = 10
TEACHER_PIN = "108"  # change if needed

# ---------------- SESSION STATE DEFAULTS ----------------
if "teacher_mode" not in st.session_state:
    st.session_state.teacher_mode = False

# ---------------- TEACHER MODE ----------------
with st.expander("🔐 Teacher Mode"):
    pin = st.text_input("Enter PIN", type="password")
    if st.button("Unlock"):
        if pin == TEACHER_PIN:
            st.session_state.teacher_mode = True
            st.success("Teacher mode enabled")
        else:
            st.error("Incorrect PIN")

# ---------------- FILE UPLOADER ----------------
uploaded_file = None
if st.session_state.teacher_mode:
    uploaded_file = st.file_uploader(
        "Upload glossary (JSON)",
        type=["json", "txt"]
    )

# ---------------- LOAD GLOSSARY ----------------
BASE_DIR = Path(__file__).parent
DEFAULT_FILE = BASE_DIR / "glossary.txt"


def validate_glossary(data: dict):
    if not isinstance(data, dict):
        return False, "Glossary must be a JSON dictionary."

    for k, v in data.items():
        if k == "_meta":
            continue
        if not isinstance(k, str):
            return False, "All glossary keys must be strings."
        if not isinstance(v, str) or not v.strip():
            return False, f"Invalid explanation for term: {k}"

    return True, ""


def glossary_signature(glossary_dict: dict) -> str:
    return hashlib.md5(
        json.dumps(glossary_dict, sort_keys=True).encode("utf-8")
    ).hexdigest()


# Load glossary
try:
    if uploaded_file is not None:
        glossary_data = json.load(uploaded_file)
        st.success("✅ Uploaded glossary loaded")
    else:
        with open(DEFAULT_FILE, "r", encoding="utf-8") as f:
            glossary_data = json.load(f)
        st.info("ℹ️ Using default glossary.txt")

except Exception as e:
    st.error(f"Failed to load glossary: {e}")
    st.stop()

# Extract metadata if present
metadata = glossary_data.pop("_meta", {})

# Validate glossary
valid, error_msg = validate_glossary(glossary_data)
if not valid:
    st.error(error_msg)
    st.stop()

glossary = glossary_data

# ---------------- GLOSSARY CHANGE DETECTION ----------------
current_signature = glossary_signature(glossary)

if "glossary_signature" not in st.session_state:
    st.session_state.glossary_signature = current_signature

elif st.session_state.glossary_signature != current_signature:
    # Reset dependent state
    for key in [
        "terms",
        "explanations",
        "index",
        "score",
        "incorrect",
        "finished"
    ]:
        st.session_state.pop(key, None)

    st.session_state.glossary_signature = current_signature
    st.warning("🔄 Glossary changed — starting a new round")
    st.rerun()

# ---------------- SHOW METADATA (TEACHER ONLY) ----------------
if metadata and st.session_state.teacher_mode:
    with st.expander("📘 Glossary Metadata"):
        for k, v in metadata.items():
            st.markdown(f"**{k.title()}:** {v}")

# ---------------- GAME INITIALIZATION ----------------
def start_new_round():
    terms = random.sample(
        list(glossary.keys()),
        min(NUM_QUESTIONS, len(glossary))
    )

    explanations = list(glossary.values())
    random.shuffle(explanations)

    st.session_state.terms = terms
    st.session_state.explanations = explanations
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.incorrect = []
    st.session_state.finished = False


if "terms" not in st.session_state:
    start_new_round()

# ---------------- EXPLANATIONS PANEL ----------------
with st.expander("📖 View Explanations"):
    explanation_map = {}
    for i, exp in enumerate(st.session_state.explanations, start=1):
        st.markdown(f"**{i}.** {exp}")
        explanation_map[i] = exp

# ---------------- GAME FLOW ----------------
if not st.session_state.finished:
    term = st.session_state.terms[st.session_state.index]

    # Defensive safety check
    if term not in glossary:
        st.error("Glossary changed unexpectedly. Restarting safely.")
        st.session_state.clear()
        st.rerun()

    correct_exp = glossary[term]
    correct_num = next(
        num for num, exp in explanation_map.items()
        if exp == correct_exp
    )

    st.markdown(
        f"### Question {st.session_state.index + 1} of {len(st.session_state.terms)}"
    )
    st.progress((st.session_state.index + 1) / len(st.session_state.terms))

    st.markdown(f"## 🕉️ {term}")

    user_input = st.number_input(
        "Enter explanation number",
        min_value=1,
        max_value=len(explanation_map),
        step=1
    )

    if st.button("✅ Submit Answer", use_container_width=True):
        if int(user_input) == correct_num:
            st.session_state.score += 1
            st.success("Correct ✅")
        else:
            st.error("Incorrect ❌")
            st.session_state.incorrect.append({
                "term": term,
                "chosen": int(user_input),
                "correct": correct_num,
                "explanation": correct_exp
            })

        st.session_state.index += 1
        if st.session_state.index >= len(st.session_state.terms):
            st.session_state.finished = True

        st.rerun()

# ---------------- RESULTS ----------------
else:
    st.markdown("## 🎯 Final Score")
    st.metric(
        "Score",
        f"{st.session_state.score} / {len(st.session_state.terms)}"
    )

    if st.session_state.incorrect:
        st.markdown("## ❌ Review Incorrect Matches")
        for item in st.session_state.incorrect:
            st.markdown(f"### 🕉️ {item['term']}")
            st.markdown(f"- Your answer: **{item['chosen']}**")
            st.markdown(f"- Correct answer: **{item['correct']}**")
            st.markdown(f"- Explanation: {item['explanation']}")
            st.divider()
    else:
        st.success("Perfect score! 🎉")

    if st.button("🔁 Play Again", use_container_width=True):
        start_new_round()
        st.rerun()

    if st.session_state.teacher_mode:
        if st.button("♻️ Reset Game"):
            st.session_state.clear()
            st.rerun()
