# src/app.py
import streamlit as st, pathlib, subprocess, json, datetime as dt
import pandas as pd, sqlite3, io

# ───────────────────────── Helpers ──────────────────────────

def conf_label(conf):
    # Handle None or string "null"
    if conf is None:
        return "—"
    if isinstance(conf, str):
        try:
            conf = float(conf)
        except Exception:
            return "—"
    return (
        "Excellent" if conf >= -0.15 else
        "Good"      if conf >= -0.30 else
        "Fair"      if conf >= -0.45 else
        "Poor"
    )


def run_step(cmd: list[str], label: str, pct: int, prog):
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        prog.progress(pct, label)
    except subprocess.CalledProcessError as e:
        st.error(f"{label} failed — see console\n{e.stderr.decode()}")
        st.stop()

def process_one_file(upload):
    """Full pipeline for a single uploaded file; returns a tuple for UI/DB."""
    raw = workdir / upload.name
    raw.write_bytes(upload.read())

    prog = st.progress(0, f"Cleaning {upload.name}…")
    run_step(["python", "-m", "src.pipelines.cleaner", str(raw)], "Cleaning…", 25, prog)
    clean_wav = raw.with_suffix(".clean.wav")

    # --- ASR -------------------------------------------------
    asr_out = json.loads(subprocess.check_output(
        ["python", "-m", "src.pipelines.asr", str(clean_wav)]))
    clean_txt = pathlib.Path(asr_out["txt"])
    conf      = asr_out["avg_logprob"]
    sec       = asr_out["sec"]
    rtf       = asr_out["rtf"]

    # --- Redaction ------------------------------------------
    run_step(["python", "-m", "src.pipelines.redactor", str(clean_txt)],
             "Redacting…", 65, prog)
    red_txt = clean_txt.with_suffix(".redacted.txt")

    # --- Sentiment / Compliance / Coverage ------------------
    prog.progress(80, "Sentiment · Compliance · Coverage…")
    sent = json.loads(subprocess.check_output(
        ["python", "-m", "src.pipelines.sentiment",   str(red_txt)]))
    comp = json.loads(subprocess.check_output(
        ["python", "-m", "src.pipelines.compliance",  str(red_txt)]))
    missing_phrases = comp.get("missing", {})
    cov  = json.loads(subprocess.check_output(
        ["python", "-m", "src.pipelines.coverage",    str(red_txt)]))

    txt = red_txt.read_text()

    # --- Persist row ----------------------------------------
    from pipelines.store import store_row
    store_row(db_path, {
        "agent": "unknown",
        "date": dt.datetime.now().isoformat(timespec="seconds"),
        "redacted": txt,
        "accuracy": None,
        "conf": conf,
        "sentiment": sent["sentiment"],
        "coverage": cov["coverage"],
        "coverage_detail": cov["detail"],
        "flags": comp["flags"],
        "asr_sec": sec,
        "asr_rtf": rtf,
    })

    prog.progress(100, "Done ✔")
    return (upload.name, txt, conf, sent["sentiment"],
            cov["coverage"], sec, rtf, comp["flags"],missing_phrases)

# ───────────────────────── Streamlit boilerplate ────────────
st.set_page_config(page_title="AI Call-Intelligence", layout="wide")
tabs = st.tabs(["Upload", "Live Transcript", "Metrics", "History", "Ask-Your-Calls"])

workdir = pathlib.Path("data"); workdir.mkdir(exist_ok=True)
db_path = pathlib.Path("call_intel.db")
st.session_state.setdefault("latest_batch", [])

# ───────────────────────── 1 │ Upload ───────────────────────
with tabs[0]:
    st.header("📤 Upload Call Recordings")
    uploads = st.file_uploader("Drag-drop files",
                               type=["wav", "mp3", "flac", "m4a"],
                               accept_multiple_files=True,
                               key="uploads")
    if uploads:
        for up in uploads:
            result = process_one_file(up)   # sequential
            st.session_state["latest_batch"].append(result)
        st.success("All files processed!")

# ───────────────────────── 2 │ Live Transcript ──────────────
with tabs[1]:
    st.header("📝 Live Transcripts")
    for fname, txt, *_ in st.session_state["latest_batch"]:
        with st.expander(fname, expanded=False):
            st.write(txt)

# ───────────────────────── 3 │ Metrics (last file) ──────────
with tabs[2]:
    st.header("📊 Latest Metrics")
    with st.popover("ℹ️  what’s this?"):
        st.markdown("""\
            **Metric meanings**
            | Name | What it is |
            |------|------------|
            | **Model conf.** | Mean log-probability per token. −0.05≈excellent, −0.5≈poor. |
            | **Coverage %** | Script-checklist items the agent actually said (hits ÷ total). |
            | **Sentiment** | DistilBERT polarity (−1 🟥 … +1 🟩). |
            | **ASR sec** | Wall-clock seconds Whisper spent on transcription. |
            | **RTF** | Real-Time Factor = ASR sec ÷ audio sec ( < 1 = faster than real-time). |
            | **Compliance flags** | Rule violations caught in `compliance.py` (see below). |
            """)
    if st.session_state["latest_batch"]:
        (conf, sent_score, cov_pct, sec, rtf, flags,missing_phrases) = st.session_state["latest_batch"][-1][2:]
        col1, col2, col3, col4, col5 = st.columns(5)
        label = conf_label(conf)
        val = f"{conf:.2f}" if isinstance(conf, (float, int)) and conf is not None else "—"
        col1.metric("Model conf.", f"{label} ({val})")
        col2.metric("Coverage %", f"{cov_pct:.1f}")
        col3.metric("Sentiment",   f"{sent_score:+.3f}")
        col4.metric("ASR sec",     f"{sec:.2f}s")
        col5.metric("RTF",         f"{rtf:.2f}")
        st.write("Compliance flags:", flags or "—")
        with st.expander("🧐  Missing mandatory phrases"):
            if missing_phrases:
                for sec, plist in missing_phrases.items():
                    st.markdown(f"**{sec}**: " + ", ".join(plist))
            else:
                st.success("All mandatory phrases present ✅")
# ───────────────────────── 4 │ History ──────────────────────
with tabs[3]:
    st.header("📚 History (transcript_v2)")
    if db_path.exists():
        con = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT id, date, conf, sentiment, coverage, asr_sec, asr_rtf, flags "
            "FROM transcript_v2 ORDER BY id DESC", con)
        st.dataframe(df, height=400)
        st.download_button("CSV", df.to_csv(index=False), "calls.csv")
        buf = io.BytesIO(); df.to_excel(buf, index=False, engine="openpyxl"); buf.seek(0)
        st.download_button("XLSX", buf, "calls.xlsx")

# ───────────────────────── 5 │ Ask-Your-Calls ───────────────
with tabs[4]:
    st.header("🧠 Ask-Your-Calls (Phase 2)")
    st.info("RAG-powered Q&A reserved for a later sprint.")
