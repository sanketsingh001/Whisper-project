from jiwer import wer
import pathlib

def quick_accuracy(hyp: str,
                   ref_path: str = "tests/50_gold_sentences.txt") -> float:
    ref = pathlib.Path(ref_path).read_text().lower()
    return 1 - wer(ref, hyp.lower())
