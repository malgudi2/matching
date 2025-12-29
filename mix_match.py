import streamlit as st
import json
import random

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Gita Ch 15 – Matching Game",
    layout="centered"
)

st.title("🕉️ Gita Chapter 15 – Matching Game")
st.markdown(
    "Match the **Sanskrit term** with the correct **explanation number**.\n\n"
    "📱 *Mobile-friendly version*"
)

# ---------- INPUT JSON ----------
glossary_json = """
{
  "Aśvattha": "The world-tree of samsāra (empirical existence), ever-changing and impermanent; that which does not remain the same even till tomorrow.",
  "Mūlam": "The root or cause; symbolically Brahman, the unseen foundation from which the world appears to arise.",
  "Ūrdhva-mūlam": "Having its roots above; indicating that the origin of the universe lies in the transcendental Reality, not in matter.",
  "Adhaḥ-śākham": "Branches growing downward; the manifestation of the world into grosser levels of existence.",
  "Chandāṁsi": "The Vedic hymns; rituals and promises that nourish worldly involvement when misunderstood.",
  "Parṇāni": "Leaves of the tree; symbolic of Vedic injunctions that sustain worldly life.",
  "Guṇa": "The three qualities—sattva, rajas, and tamas—which bind consciousness to matter.",
  "Karma-anubandhīni": "Bound by actions; indicating that worldly life continues due to past actions and their vasanas.",
  "Asaṅga-śastra": "The weapon of detachment; discriminative knowledge used to cut attachment to the world.",
  "Padam Avyayam": "The imperishable state; Brahman, beyond change, time, and decay.",
  "Puruṣa": "Consciousness, the Self, which illumines all experiences.",
  "Kṣara Puruṣa": "The perishable self; the ego-bound individual identified with body and mind.",
  "Akṣara Puruṣa": "The imperishable; the subtle, unmanifest causal state (Hiraṇyagarbha or total mind).",
  "Uttama Puruṣa": "The Supreme Self (Puruṣottama); Brahman that transcends both the perishable and imperishable.",
  "Paramātma": "The Supreme Consciousness that enlivens, sustains, and governs all beings.",
  "Jīva-bhūtaḥ": "The individual soul; Pure Consciousness conditioned by the mind and senses.",
  "Vaishvānara": "The digestive fire; the same Consciousness functioning as the power of digestion in all beings.",
  "Smṛti": "Memory; the power of recollection bestowed by the Lord.",
  "Apohanam": "Forgetfulness; also governed by the Lord, essential for functional living."
}
"""

glossary = json.loads(glossary_json)
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
    st.session_state.incorrect = []  # store incorrect matches

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

