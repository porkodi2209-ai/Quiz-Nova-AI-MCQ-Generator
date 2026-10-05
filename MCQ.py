import os
import re
import json
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="QuizNova AI", page_icon="🧠")

st.title("🧠 QuizNova AI")
st.caption("AI Powered MCQ Assessment")

MODEL = "Qwen/Qwen2.5-72B-Instruct"
client = InferenceClient(
    model=MODEL,
    token=os.getenv("HF_TOKEN")
)

topic = st.text_input("📚 Enter Topic")

c1, c2 = st.columns(2)

with c1:
    n = st.slider("🔢 Questions", 5, 10, 5)

with c2:
    level = st.selectbox("🎯 Difficulty", ["Easy", "Medium", "Hard"])

prompt = """
Generate {n} multiple-choice questions about {topic}.
Difficulty: {level}.

Return ONLY JSON.

- Carefully solve every question before selecting the correct answer.
- Verify every answer against the options.
- For mathematical or code-output questions, calculate the result yourself first.
- The "answer" field MUST contain the index of the actually correct option.

Each question must have 4 options and one correct answer.

Format:
[
 {{
  "question": "question",
  "options": ["A", "B", "C", "D"],
  "answer": 0,
  "explanation": "short explanation"
 }}
]
"""

if st.button("🚀 Generate Quiz") and topic.strip():

    with st.spinner("Creating your quiz..."):
        try:
            r = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.format(
                            n=n,
                            topic=topic,
                            level=level
                        )
                    }
                ],
                max_tokens=2000,
                temperature=0.5
            )

            text = r.choices[0].message.content
            data = json.loads(
                re.search(r"\[.*\]", text, re.S).group()
            )

            st.session_state.quiz = data

        except Exception as e:
            st.error(f"Quiz generation failed: {e}")


quiz = st.session_state.get("quiz")

if quiz:

    st.subheader("📝 Answer the Questions")

    answers = []

    for i, q in enumerate(quiz):
        ans = st.radio(
            f"{i+1}. {q['question']}",
            q["options"],
            index=None,
            key=f"q{i}"
        )
        answers.append(ans)

    if st.button("✅ Submit Quiz"):

        score = 0

        for i, (q, ans) in enumerate(zip(quiz, answers)):

            correct = q["options"][q["answer"]]

            if ans == correct:
                score += 1
                st.success(f"Q{i+1}: ✅ Correct")
            else:
                st.error(
                    f"Q{i+1}: ❌ Correct answer: {correct}"
                )

            st.caption("💡 " + q["explanation"])

        st.subheader(f"🎉 Score: {score}/{len(quiz)}")

    if st.button("🔄 Create New Quiz"):
        st.session_state.quiz = None
        st.rerun()