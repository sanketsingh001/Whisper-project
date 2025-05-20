

import streamlit as st, pathlib, subprocess, json, datetime as dt, pandas as pd, sqlite3, os
from pipelines.metrics import quick_accuracy

st.set_page_config(page_title="AI Call-Intelligence", layout="wide")

tabs = st.tabs(["Upload", "Live Transcript", "Metrics", "History", "Ask-Your-Calls"])
workdir = pathlib.Path("data"); workdir.mkdir(exist_ok=True)
db_path = pathlib.Path("call_intel.db")

# 1 ─ Upload
with tabs[0]:
    st.header("📤 Upload Call Recording")
    up = st.file_uploader("Drag-drop WAV / MP3", type=["wav", "mp3"])
    if up:
        raw = workdir / up.name
        raw.write_bytes(up.read())
        prog = st.progress(0, "Cleaning…")
        subprocess.run(["python", "-m", "src.pipelines.cleaner", str(raw)], check=True)
        prog.progress(25, "Transcribing…")
        subprocess.run(["python", "-m", "src.pipelines.asr", str(raw.with_suffix('.clean.wav'))], check=True)
        prog.progress(60, "Redacting…")
        subprocess.run(["python", "-m", "src.pipelines.redactor", str(raw.with_suffix('.clean.txt'))], check=True)
        prog.progress(75, "Sentiment & Compliance…")
        sent = json.loads(subprocess.check_output(
            ["python", "-m", "src.pipelines.sentiment", str(raw.with_suffix('.clean.redacted.txt'))]))
        comp = json.loads(subprocess.check_output(
            ["python", "-m", "src.pipelines.compliance", str(raw.with_suffix('.clean.redacted.txt'))]))
        txt = raw.with_suffix('.clean.redacted.txt').read_text()
        acc = quick_accuracy(txt)
        prog.progress(100, "Saving…")
        from pipelines.store import store_row
        store_row(db_path, {
            "agent": "unknown",
            "date": dt.datetime.now().isoformat(timespec='seconds'),
            "redacted": txt,
            "accuracy": acc,
            "sentiment": sent["sentiment"],
            "flags": comp["flags"]
        })
        st.session_state["latest"] = txt, acc, sent["sentiment"], comp["flags"]
        st.success("Done!")

# 2 ─ Live Transcript
with tabs[1]:
    st.header("📝 Live Transcript")
    if "latest" in st.session_state:
        st.write(st.session_state["latest"][0])

# 3 ─ Metrics
with tabs[2]:
    st.header("📊 Metrics")
    if "latest" in st.session_state:
        _, acc, sent_score, flags = st.session_state["latest"]
        st.metric("Accuracy %", f"{acc*100:.1f}")
        st.metric("Sentiment", f"{sent_score:+.2f}")
        st.write("Flags:", flags)

# 4 ─ History
with tabs[3]:
    st.header("📚 History")
    if db_path.exists():
        con = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM transcripts", con)
        st.dataframe(df, height=400)
        st.download_button("Download CSV", df.to_csv(index=False), "calls.csv")
        st.download_button("Download XLSX", df.to_excel(index=False), "calls.xlsx")

# 5 ─ Ask-Your-Calls
with tabs[4]:
    st.header("🧠 Ask-Your-Calls (Upgrade)")
    st.info("RAG-powered Q&A reserved for Phase-2.")
