def evaluate_transcript(transcript):
    """
    Lightweight deterministic evaluator used until AI provider integration is ready.
    """
    length = len(transcript.strip())
    score = min(100, max(40, length // 4))
    return {
        "score": score,
        "feedback": "التقييم مبدئي. سيتم استبدال هذا التقييم بمحرك ذكاء اصطناعي لاحقاً.",
    }

