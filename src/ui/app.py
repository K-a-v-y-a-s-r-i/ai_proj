# src/ui/app.py

import sys
import os
import base64

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(ROOT)

import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path

from src.generation.generate import generate_hypothesis
from src.validation.validate import novelty_score


# -----------------------------------------------------------
#  BACKGROUND IMAGE FUNCTION
# -----------------------------------------------------------

def set_background(image_path):
    """Sets the background image for Streamlit UI."""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
            .stApp {{
                background: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Load background image
set_background("src/ui/bg.jpg")


# -----------------------------------------------------------
#  PAGE CONFIG
# -----------------------------------------------------------

st.set_page_config(
    page_title="Gene–Disease Hypothesis Generator",
    layout="wide"
)


# -----------------------------------------------------------
#  PREMIUM CSS THEME
# -----------------------------------------------------------

st.markdown("""
<style>

    /* Background overlay for readability */
    .main > div {
        background: rgba(255, 255, 255, 0.60);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 25px;
        border-radius: 22px;
        margin-top: 20px;
    }

    /* Title */
    .big-title {
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        color: #E4F1FE;
        text-shadow: 0px 2px 8px rgba(0,0,0,0.5);
        letter-spacing: 2px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #B0D7FF;
        font-size: 20px;
        margin-bottom: 40px;
        letter-spacing: 0.5px;
    }

    /* Section Titles */
    .section-title {
        font-size: 26px;
        font-weight: 700;
        color: #E4F1FE;
        margin-bottom: 15px;
    }

    /* Glass-like panels */
    .panel {
        background: rgba(255,255,255,0.85);
        border-radius: 18px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.4);
        margin-bottom: 25px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);
    }

    /* Text display cards */
    .text-card {
        background: rgba(255,255,255,0.92);
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 5px solid #1A8FE3;
        margin-bottom: 12px;
        color: #E4F1FE;
        font-size: 16px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #005C99, #1A8FE3);
        color: white;
        padding: 12px 20px;
        font-size: 18px;
        border-radius: 10px;
        border: none;
        transition: 0.25s ease;
    }

    .stButton > button:hover {
        transform: scale(1.04);
        background: linear-gradient(90deg, #1A8FE3, #005C99);
        box-shadow: 0 6px 14px rgba(0,0,0,0.3);
    }

</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------
#  STORAGE SETUP
# -----------------------------------------------------------

HYP_FILE = Path("data/processed/hypotheses.csv")
FB_FILE = Path("data/processed/feedback.csv")
FB_FILE.parent.mkdir(parents=True, exist_ok=True)

if not HYP_FILE.exists():
    pd.DataFrame(columns=[
        "hypothesis_id","gene_symbol","disease_name",
        "hypothesis_text","evidence_passages",
        "novelty_flag","novelty_score","created_at"
    ]).to_csv(HYP_FILE, index=False)

df = pd.read_csv(HYP_FILE)


# -----------------------------------------------------------
#  HEADER UI
# -----------------------------------------------------------

st.markdown('<div class="big-title">Gene–Disease Hypothesis Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A Professional RAG-Based Biomedical Discovery Interface</div>', unsafe_allow_html=True)


# -----------------------------------------------------------
#  GENERATE NEW HYPOTHESIS PANEL
# -----------------------------------------------------------

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Generate New Hypothesis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    gene_input = st.text_input("Gene Symbol", placeholder="e.g., BRCA1, TP53")

with col2:
    disease_input = st.text_input("Disease Name", placeholder="e.g., breast cancer")

if st.button("Generate Hypothesis"):
    if gene_input.strip() == "":
        st.error("Please enter a gene symbol.")

    else:
        with st.spinner("Processing biomedical text and generating hypothesis..."):
            hypothesis_text, evidence = generate_hypothesis(gene_input, disease_input, k=5)
            evidence_texts = [e["text"] for e in evidence]

            nscore = novelty_score(gene_input, disease_input)
            nflag = 1 if nscore > 0.5 else 0
            hid = int(time.time())

            pd.DataFrame([{
                "hypothesis_id": hid,
                "gene_symbol": gene_input,
                "disease_name": disease_input,
                "hypothesis_text": hypothesis_text.replace("\n"," "),
                "evidence_passages": json.dumps(evidence_texts),
                "novelty_flag": nflag,
                "novelty_score": nscore,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }]).to_csv(HYP_FILE, mode="a", header=False, index=False)

        st.success("Hypothesis successfully generated.")

        st.markdown("#### Generated Hypothesis")
        st.markdown(f'<div class="text-card">{hypothesis_text}</div>', unsafe_allow_html=True)

        st.markdown("#### Evidence Passages")
        for txt in evidence_texts:
            st.markdown(f'<div class="text-card">{txt}</div>', unsafe_allow_html=True)

        st.markdown("#### Novelty Score")
        st.markdown(f'<div class="text-card">{nscore:.2f}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------
#  BROWSE HYPOTHESES PANEL
# -----------------------------------------------------------

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title" style="color: #E4F1FE;">Browse Existing Hypotheses</div>',
    unsafe_allow_html=True
)



query = st.text_input("Search Gene or Disease")

results = df[df["gene_symbol"].str.contains(query, case=False, na=False) |
             df["disease_name"].str.contains(query, case=False, na=False)] if query else df

st.dataframe(results[["hypothesis_id","gene_symbol","disease_name","novelty_flag","created_at"]])

if not results.empty:
    selected = st.selectbox("Select Hypothesis ID", results["hypothesis_id"].astype(str))
    row = df[df["hypothesis_id"].astype(str) == selected].iloc[0]

    st.markdown("#### Hypothesis")
    st.markdown(f'<div class="text-card">{row["hypothesis_text"]}</div>', unsafe_allow_html=True)

    st.markdown("#### Evidence Passages")
    evid = json.loads(row["evidence_passages"])
    for e in evid:
        st.markdown(f'<div class="text-card">{e}</div>', unsafe_allow_html=True)

    st.markdown("#### Novelty Score")
    st.markdown(f'<div class="text-card">{row["novelty_score"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------------------------------
#  FEEDBACK PANEL
# -----------------------------------------------------------

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Expert Feedback</div>', unsafe_allow_html=True)

if not df.empty:
    fb_selected = st.selectbox("Choose Hypothesis ID to Review", df["hypothesis_id"].astype(str))

    fb_choice = st.radio(
        "How would you rate this hypothesis?",
        ["Strong / Useful", "Average / Needs Review", "Weak / Not Useful"],
        horizontal=True
    )

    fb_comment = st.text_area(
        "Additional Comments (optional)",
        placeholder="Write expert notes or evaluation..."
    )

    if st.button("Submit Feedback"):
        with open(FB_FILE, "a", encoding="utf-8") as f:
            f.write(",".join([
                fb_selected,
                fb_choice.replace(",", ";"),
                fb_comment.replace(",", ";"),
                str(time.time())
            ]) + "\n")
        st.success("Feedback successfully recorded.")

st.markdown('</div>', unsafe_allow_html=True)
