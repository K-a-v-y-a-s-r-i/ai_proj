import streamlit as st
import pandas as pd
from pathlib import Path
import json, time

HYP_FILE = Path("data/processed/hypotheses.csv")
FB_FILE = Path("data/processed/feedback.csv")
FB_FILE.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Gene–Disease Hypothesis Explorer", layout="wide")
st.title("Gene–Disease Hypothesis Explorer")

if HYP_FILE.exists():
    df = pd.read_csv(HYP_FILE)
else:
    df = pd.DataFrame(columns=["hypothesis_id","gene_symbol","disease_name","hypothesis_text","evidence_passages","novelty_flag","novelty_score","created_at"])

col1, col2 = st.columns([3,1])
with col1:
    q = st.text_input("Search gene or disease")
    if q:
        res = df[df["gene_symbol"].str.contains(q, case=False, na=False) | df["disease_name"].str.contains(q, case=False, na=False)]
    else:
        res = df
    st.dataframe(res[["hypothesis_id","gene_symbol","disease_name","novelty_flag","created_at"]].sort_values("created_at", ascending=False))

    sel = st.selectbox("Select hypothesis id", options=list(res["hypothesis_id"].astype(str).unique()) if not res.empty else [])
    if sel:
        row = df[df["hypothesis_id"].astype(str) == sel].iloc[0]
        st.subheader(f"{row['gene_symbol']} → {row['disease_name']}")
        st.write(row["hypothesis_text"])
        try:
            evid = eval(row.get("evidence_passages","[]"))
        except:
            evid = []
        st.markdown("**Evidence passages:**")
        for e in evid:
            st.write("-", e)
        judgment = st.radio("Expert judgment", ["Useful","Not useful","Unsure"])
        comment = st.text_area("Comments (optional)")
        if st.button("Submit feedback"):
            with open(FB_FILE, "a", encoding="utf-8") as f:
                f.write(",".join([str(sel), judgment, comment.replace(",", ";"), str(time.time())]) + "\n")
            st.success("Feedback saved")

with col2:
    st.markdown("## Controls")
    if st.button("Reload"):
        st.experimental_rerun()
    st.markdown("### Stats")
    st.write("Total hypotheses:", len(df))
    if "novelty_flag" in df.columns:
        try:
            nov = df["novelty_flag"].astype(int).sum()
        except:
            nov = df["novelty_flag"].astype(bool).sum()
        st.write("Novel hypotheses:", int(nov))
