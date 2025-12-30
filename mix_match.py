import streamlit as st
import json
import random
from pathlib import Path

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Bhagwad Gita  – Learning Game",
    layout="centered"
)

st.title("🕉️ Bhagwad Gita  – Learning Game")
st.markdown(
    "Match the **Sanskrit term** with the correct **explanation number**.\n\n"
    "📱 *Mobile-friendly version*"
)

# ---------- LOAD GLOSSARY FROM FILE ----------
GLOSSARY_FILE = Path("glossary.txt")

if not GLOSSARY_FILE.exists():
    st.error("❌ glossary.txt not found. Please place it in the same folder as this app.")
    st.stop()

try:
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        glossary = json.load(f)
except json.JSONDecodeError:
    st.error("❌ glossary.txt is not valid JSON.")
    st.stop()

NUM_QUESTIONS = 10

# ---------- SESSION STATE ----------
if "terms" not in st.session_state:
    st.session_state.terms = random.sample(
        list(glossary.keys()),
        min(NUM_QUESTIONS, len(glossary))
    )
    explanations = list(glossary.values())
    random.shuffle(explanations)
    st.session_state.explanations = explanations
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.finished = False
    st.session_state.incorrect = []

# ---------- EXPLANATIONS (COLLAPSIBLE) ----------
with st.expander("📖 Tap to view explanations"):
    explanation_map = {}
    for i, exp in enumerate(st.session_state.explanations, start=1):
        st.markdown(f"**{i}.** {exp}")
        explanation_map[i] = exp

# ---------- GAME FLOW ----------
if not st.session_state.finished:
    term = st.session_state.terms[st.session_state.index]
    correct_exp = glossary[term]
    correct_num = next(
        num for num, exp in explanation_map.items()
        if exp == correct_exp
    )

    # Progress indicator
    st.markdown(
        f"### Question {st.session_state.index + 1} of {len(st.session_state.terms)}"
    )
    st.progress((st.session_state.index + 1) / len(st.session_state.terms))

    # Term
    st.markdown(f"## 🕉️ {term}")

    # Numeric input
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

# ---------- FINAL RESULTS ----------
else:
    st.markdown("## 🎯 Final Score")
    st.metric(
        "Your Score",
        f"{st.session_state.score} / {len(st.session_state.terms)}"
    )

    if st.session_state.incorrect:
        st.markdown("## ❌ Review: Incorrect Matches")

        for item in st.session_state.incorrect:
            st.markdown(f"### 🕉️ {item['term']}")
            st.markdown(f"- **Your choice:** {item['chosen']}")
            st.markdown(f"- **Correct number:** {item['correct']}")
            st.markdown(f"- **Correct explanation:** {item['explanation']}")
            st.divider()
    else:
        st.success("Perfect score! All matches correct 🎉")

    if st.button("🔁 Play Again", use_container_width=True):
        st.session_state.clear()
        st.rerun()
