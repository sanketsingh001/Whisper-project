# src/pipelines/metrics.py
from jiwer import wer
import pathlib, logging

def accuracy_vs_ref(hyp_txt: pathlib.Path) -> float | None:
    """
    Returns 1-WER (0-1) if <audio>.ref.txt exists and is readable.
    If the reference file is missing, empty, or any error occurs,
    return None so the rest of the pipeline keeps running.
    """
    try:
        ref_path = hyp_txt.with_suffix(".ref.txt")
        if not ref_path.exists():
            return None

        hyp = hyp_txt.read_text().strip().lower()
        ref = ref_path.read_text().strip().lower()
        if not hyp or not ref:
            return None

        return 1 - wer(ref, hyp)
    except Exception as exc:
        logging.warning("accuracy_vs_ref failed for %s: %s", hyp_txt, exc)
        return None
