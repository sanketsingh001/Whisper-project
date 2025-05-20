import streamlit as st, pathlib, subprocess, json, datetime as dt, pandas as pd, sqlite3, os, sys
from pipelines.metrics import accuracy_vs_ref
import io



st.set_page_config(page_title="AI Call-Intelligence", layout="wide")

tabs = st.tabs(["Upload", "Live Transcript", "Metrics", "History", "Ask-Your-Calls"])
workdir = pathlib.Path("data"); workdir.mkdir(exist_ok=True)
db_path = pathlib.Path("call_intel.db")

def run_step(cmd: list[str], label: str, pct: int, prog):
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        prog.progress(pct, label)
    except subprocess.CalledProcessError as e:
        st.error(f"{label} failed — see console. \n{e.stderr.decode()}")
        st.stop()

# ───────────────────────────── 1 │ Upload
with tabs[0]:
    st.header("📤 Upload Call Recording")
    up = st.file_uploader("Drag-drop WAV / MP3", type=["wav", "mp3"])
    if up:
        raw = workdir / up.name
        raw.write_bytes(up.read())

        prog = st.progress(0, "Cleaning…")
        # ─ Cleaning → my.clean.wav
        run_step(["python", "-m", "src.pipelines.cleaner", str(raw)], "Cleaning…", 25, prog)

        clean_wav = raw.with_suffix(".clean.wav")

        # ─ ASR → my.clean.txt
        run_step(["python", "-m", "src.pipelines.asr", str(clean_wav)], "Transcribing…", 50, prog)
        clean_txt = clean_wav.with_suffix(".txt")

        # ─ Redaction → my.clean.redacted.txt
        run_step(["python", "-m", "src.pipelines.redactor", str(clean_txt)], "Redacting…", 65, prog)
        red_txt = clean_txt.with_suffix(".redacted.txt")

        # ─ Sentiment / Compliance
        prog.progress(80, "Sentiment & Compliance…")
        try:
            sent = json.loads(subprocess.check_output(
                ["python", "-m", "src.pipelines.sentiment", str(red_txt)]))
            comp = json.loads(subprocess.check_output(
                ["python", "-m", "src.pipelines.compliance", str(red_txt)]))
        except subprocess.CalledProcessError as e:
            st.error(e.stderr.decode()); st.stop()

        txt = red_txt.read_text()
        acc = accuracy_vs_ref(clean_txt) 

        # ─ Persist
        from pipelines.store import store_row
        store_row(db_path, {
            "agent": "unknown",
            "date": dt.datetime.now().isoformat(timespec="seconds"),
            "redacted": txt,
            "accuracy": acc,
            "sentiment": sent["sentiment"],
            "flags": comp["flags"]
        })
        st.session_state["latest"] = txt, acc, sent["sentiment"], comp["flags"]
        prog.progress(100, "Done!")
        st.success("Pipeline complete ✔")

# ───────────────────────────── 2 │ Live Transcript
with tabs[1]:
    st.header("📝 Live Transcript")
    if "latest" in st.session_state:
        st.write(st.session_state["latest"][0])


# ───────────────────────────── 3 │ Metrics
with tabs[2]:
    st.header("📊 Metrics")
    if "latest" in st.session_state:
        _, acc, sent_score, flags = st.session_state["latest"]
        col1, col2 = st.columns(2)

        # ← Guard against None
        if acc is None:
            col1.metric("Accuracy %", "—")
        else:
            col1.metric("Accuracy %", f"{acc*100:.1f}")

        col2.metric("Sentiment", f"{sent_score:+.3f}")
        st.write("Compliance flags:", flags or "—")

# ───────────────────────────── 4 │ History
with tabs[3]:
    st.header("📚 History")
    if db_path.exists():
        con = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM transcripts ORDER BY id DESC", con)
        st.dataframe(df, height=400)
        st.download_button("Download CSV", df.to_csv(index=False), "calls.csv")
        excel_buf = io.BytesIO()
        df.to_excel(excel_buf, index=False, engine='openpyxl')
        excel_buf.seek(0)
        st.download_button("Download XLSX", excel_buf, "calls.xlsx")


# ───────────────────────────── 5 │ Ask-Your-Calls
with tabs[4]:
    st.header("🧠 Ask-Your-Calls (Phase 2)")
    st.info("RAG-powered Q&A reserved for a later sprint.")
