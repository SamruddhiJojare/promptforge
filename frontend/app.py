import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from configs.settings import settings

st.set_page_config(page_title="PromptForge", page_icon="🛠️", layout="wide")

st.title("🛠️ PromptForge")
st.caption("Adaptive prompt optimization & evaluation — analyze, rewrite, and score a prompt side by side.")

with st.form("optimize_form"):
    prompt = st.text_area(
        "Enter your prompt",
        placeholder="e.g. Explain machine learning.",
        height=120,
    )
    submitted = st.form_submit_button("Optimize")

if submitted:
    if not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        with st.spinner("Analyzing and optimizing..."):
            try:
                resp = requests.post(
                    f"{settings.backend_url}/optimize",
                    json={"prompt": prompt},
                    timeout=60,
                )
                resp.raise_for_status()
                result = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("Couldn't reach the backend. Is `uvicorn backend.api.main:app --reload` running?")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"Backend error: {e.response.text}")
                st.stop()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original")
            st.text_area("original_prompt_display", result["original_prompt"], height=200, label_visibility="collapsed")
            st.metric("Overall score", result["original_score"]["overall"])

        with col2:
            st.subheader("Optimized")
            st.text_area("optimized_prompt_display", result["optimized_prompt"], height=200, label_visibility="collapsed")
            st.metric(
                "Overall score",
                result["optimized_score"]["overall"],
                delta=result["improvement"],
            )

        st.divider()
        st.subheader("Score breakdown")
        score_col1, score_col2, score_col3 = st.columns(3)
        score_col1.metric("Relevance (optimized)", result["optimized_score"]["relevance"])
        score_col2.metric("Clarity (optimized)", result["optimized_score"]["clarity"])
        score_col3.metric("Format adherence (optimized)", result["optimized_score"]["format_adherence"])

st.divider()

with st.expander("Recent runs"):
    try:
        history_resp = requests.get(f"{settings.backend_url}/history", timeout=10)
        history_resp.raise_for_status()
        runs = history_resp.json()
        if runs:
            st.dataframe(runs, use_container_width=True)
        else:
            st.write("No runs yet.")
    except requests.exceptions.ConnectionError:
        st.write("Backend not reachable.")