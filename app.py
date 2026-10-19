import json
from pathlib import Path
import streamlit as st
import core

st.set_page_config(page_title="Cynbit Inquiry-to-Proposal Assistant", page_icon="🧭")
st.title("🧭 Inquiry-to-Proposal Assistant")
st.caption("AI triage and draft proposals for Cynbit-style service inquiries (assessment PoC)")

samples = json.loads((Path(__file__).parent / "data/sample_inquiries.json").read_text())
use_llm = bool(__import__("os").getenv("ANTHROPIC_API_KEY"))
st.sidebar.markdown(f"**Mode:** {'LLM (' + core.MODEL + ')' if use_llm else 'Offline heuristic (no API key)'}")
st.sidebar.markdown("Set `ANTHROPIC_API_KEY` to enable the LLM extractor.")

pick = st.selectbox("Load a sample inquiry", ["(write your own)"] + [f"#{s['id']}: {s['text'][:60]}…" for s in samples])
default = "" if pick.startswith("(") else samples[int(pick[1:].split(":")[0]) - 1]["text"]
text = st.text_area("Client inquiry", value=default, height=140)

if st.button("Analyze", type="primary") and text.strip():
    with st.spinner("Analyzing…"):
        a = core.analyze(text)
    c1, c2, c3 = st.columns(3)
    c1.metric("Lead score", f"{a['score']}/100", a["band"])
    c2.metric("Service", a["service"])
    c3.metric("Urgency", a["urgency"].title())
    st.write(f"**Budget (INR):** {a['budget_inr']:,}" if a.get("budget_inr") else "**Budget:** not stated")
    st.caption(f"Score breakdown: {a['score_parts']}  |  Extractor: {a['source']}")
    l, r = st.columns(2)
    l.subheader("Requirements")
    for x in a.get("requirements", []):
        l.write(f"- {x}")
    r.subheader("Risks")
    for x in a.get("risks", []):
        r.write(f"- {x}")
    st.subheader("Clarifying questions")
    for x in a.get("clarifying_questions", []):
        st.write(f"- {x}")
    st.divider(); st.markdown(a["proposal"])
    st.download_button("Download proposal (.md)", a["proposal"], "proposal.md")
