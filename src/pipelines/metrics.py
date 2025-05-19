from jiwer import wer
def quick_accuracy(hyp, ref_path='tests/50_gold_sentences.txt'):
    import pathlib
    ref = pathlib.Path(ref_path).read_text().lower()
    return 1 - wer(ref, hyp.lower())
