def normalize_score(score: float, method="l2") -> float:
    if method == "l2":
        # Cosine similarity -1 ile 1 arasında gelir → %0-100 arası normalize edilir
        return round(((score + 1) / 2) * 100, 2)
    return 0.0
