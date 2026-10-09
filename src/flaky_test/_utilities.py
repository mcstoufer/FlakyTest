from collections import Counter
import math

def test_result_entropy(text: str, overlapping: bool = True) -> float:
    """Calculates the Shannon entropy of 2-character sequences (bigrams) in a string."""
    step = 1 if overlapping else 2
    pairs = [text[i:i + 2] for i in range(0, len(text) - 1, step) if len(text[i:i + 2]) == 2]
    if not pairs:
        return 0.0

    counts = Counter(pairs)
    total = len(pairs)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())