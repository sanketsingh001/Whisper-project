import streamlit as st, pathlib, subprocess, datetime as dt, json
from pipelines.metrics import quick_accuracy

st.set_page_config(page_title="AI Call‑Intelligence", layout="wide")
tabs = st.tabs(["Upload", "Live Transcript", "Metrics", "History", "Ask‑Your‑Calls"])

with tabs[0]:
    st.header("Upload")
    up = st.file_uploader("WAV/MP3", type=["wav","mp3"])
    if up:
        fn = pathlib.Path("data")/up.name
        fn.parent.mkdir(exist_ok=True)
        fn.write_bytes(up.read())
        st.write("Saved to", fn)
        st.session_state['latest_path'] = str(fn)

with tabs[1]:
    st.header("Live Transcript")
    if 'latest_path' in st.session_state:
        txt_path = pathlib.Path(st.session_state['latest_path']).with_suffix('.txt')
        if txt_path.exists():
            st.text(txt_path.read_text())

with tabs[2]:
    st.header("Metrics")
    if 'latest_path' in st.session_state:
        txt_path = pathlib.Path(st.session_state['latest_path']).with_suffix('.txt')
        if txt_path.exists():
            acc = quick_accuracy(txt_path.read_text())
            st.metric("Accuracy %", f"{acc*100:.1f}")

with tabs[4]:
    st.info("Upgrade to unlock RAG Q&A")
