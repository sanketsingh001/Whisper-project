# AI Call-Intelligence Platform

[![Streamlit](https://img.shields.io/badge/streamlit-v1.33.0-blue)](https://streamlit.io/)  
[![Python](https://img.shields.io/badge/python-3.11-brightgreen.svg)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

AI Call-Intelligence is a powerful, modular system designed to transcribe, analyze, and derive insights from call recordings. It leverages state-of-the-art speech-to-text models, natural language processing (NLP), and sentiment analysis to provide call transcription, quality metrics, compliance checks, and interactive dashboards via a Streamlit web UI.

The project integrates:

- **Faster Whisper** for fast, GPU-accelerated speech recognition
- **Transformers-based models** for sentiment and text analytics
- **Presidio** for PII detection and anonymization
- **SoX and FFmpeg** for audio preprocessing
- **SQLite** for lightweight data storage and query
- **Streamlit** for user-friendly, web-based interaction

---

## Features

- Upload and transcribe audio calls (WAV/MP3)
- Generate accurate text transcripts with confidence scores
- Perform sentiment analysis and speech quality metrics
- Detect and anonymize Personally Identifiable Information (PII)
- Store transcripts and analytics results in a lightweight database
- Interactive dashboards for insights, filtering, and history
- Export results as PDFs and Excel files
- Designed for GPU and CPU deployments with Docker support

---

## Architecture

```plaintext
+-----------------+        +------------------+        +---------------------+
|                 |        |                  |        |                     |
|   Audio Upload  +------->+   Audio Cleaning +------->+ Speech-to-Text Model |
| (WAV / MP3)     |        | (SoX, FFmpeg)    |        | (Faster Whisper)    |
|                 |        |                  |        |                     |
+-----------------+        +------------------+        +-----------+---------+
                                                                |
                                                                v
 +-----------------+         +--------------------+       +---------------------+
 |                 |         |                    |       |                     |
 |   Sentiment &   |<--------+ Text Preprocessing +<------+  Transcript Text     |
 |   Compliance    |         | (Presidio, Regex)  |       | (Segments, Confidence)|
 |   Analysis      |         |                    |       |                     |
 +-----------------+         +--------------------+       +---------------------+

            |
            v
 +-----------------+          +-------------------+
 |                 |          |                   |
 |  SQLite DB      |<---------+  Metrics & Reports |
 |  Storage       |          |                   |
 +-----------------+          +-------------------+

            |
            v
 +--------------------------------+
 |                                |
 |      Streamlit UI / Dashboard  |
 |                                |
 +--------------------------------+

# AI‑Call‑Intelligence

A lightweight, end‑to‑end platform for cleaning, transcribing, and analysing call recordings.  
Powered by **Faster‑Whisper**, **Transformers**, and **Streamlit**, it turns raw audio into structured insights—complete with sentiment, compliance flags, and easy export options.

---

## ✨ Features

* **One‑click upload** – drag‑and‑drop WAV or MP3 files.
* **Automatic audio cleaning** – SoX & FFmpeg pipeline.
* **Fast, accurate ASR** – Faster‑Whisper with optional GPU acceleration.
* **Confidence & sentiment scoring** – each transcript segment is enriched with metrics.
* **Searchable history** – browse past calls, metrics, and reports.
* **Export** – download PDF or Excel transcripts in one click.
* **Container‑ready** – deploy anywhere with Docker (GPU **or** CPU).

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Docker** (recommended) | Simplest, fully reproducible set‑up |
| **Python 3.11+** | For manual installation |
| **ffmpeg & sox** | System packages for audio processing |
| **CUDA 12.8 GPU** *(optional)* | Dramatically faster transcription; CPU mode also supported |

---

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-call-intelligence.git
cd ai-call-intelligence
```

### 2a. Set‑up with Docker (GPU)

**Build the image**
```bash
docker build -t call-intel:gpu .
```

**Run the container**
```bash
docker run --gpus all -p 8501:8501 call-intel:gpu
```
Now open your browser at **http://localhost:8501**.

---

### 2b. Set‑up with Docker (CPU‑only)

1. **Edit `Dockerfile`**
   ```dockerfile
   # Base image
   FROM python:3.11-slim

   # Replace Torch install
   RUN pip install --no-cache-dir torch==2.2.2+cpu
   ```
2. **Build & run**
   ```bash
   docker build -t call-intel:cpu .
   docker run -p 8501:8501 call-intel:cpu
   ```

---

### 2c. Manual Python environment (no Docker)

**Create & activate a virtual environment**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Install system dependencies** (Ubuntu example)
```bash
sudo apt-get update && \
  sudo apt-get install -y ffmpeg sox libsox-fmt-all
```

**Install Python dependencies**
```bash
pip install -r requirements.txt
# GPU (CUDA 12.8)
pip install --extra-index-url https://download.pytorch.org/whl/cu128 torch==2.2.2+cu128
# CPU‑only
# pip install torch==2.2.2+cpu
```

**Run the app**
```bash
streamlit run src/app.py
```

---

## 📈 Usage

1. **Upload** WAV or MP3 files on the *Upload* tab.
2. The app **cleans & transcribes** audio, showing confidence and sentiment in real time.
3. Review **segment‑level** text, search, or jump to specific timestamps.
4. Export the full transcript or summary report as **PDF/Excel**.
5. Navigate to *History* and *Metrics* tabs to revisit past calls.

---

## 🗂️ Project Structure

```text
.
├── Dockerfile
├── README.md
├── requirements.txt
├── src
│   ├── app.py              # Streamlit entry‑point
│   ├── pipelines           # ASR, sentiment, compliance, storage
│   ├── utils               # Helper utilities
│   └── ...
├── data                    # Sample audio / transcripts (git‑ignored)
└── ...
```

---

## 🛠️ Technologies

| Technology | Purpose |
|------------|---------|
| Faster‑Whisper | Fast speech‑to‑text transcription |
| 🤗 Transformers | Sentiment & text classification |
| Presidio | PII detection & anonymisation |
| SoX / FFmpeg | Audio cleaning & conversion |
| SQLite | Lightweight local database |
| Streamlit | Web UI & dashboards |
| Docker | Containerised deployment |

---

## 🤝 Contribution

Found a bug, want a new feature, or wrote a better prompt?  
*Issues* and *pull requests* are warmly welcome—please follow the existing code style and add tests where relevant.

---

## 📄 Licence






