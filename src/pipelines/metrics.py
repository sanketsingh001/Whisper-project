from jiwer import wer
import pathlib

def quick_accuracy(hyp: str,
                   ref_path: str = "tests/50_gold_sentences.txt") -> float:
    ref_file = pathlib.Path(ref_path)
    if not ref_file.exists():
        # No gold file in prod – return sentinel 0 accuracy
        return 0.0
    ref = ref_file.read_text().lower()
    return max(0.0, 1 - wer(ref, hyp.lower()))
