"""NRC emotion scores through NRCLex, whichever of its two APIs is installed (#1719).

NRCLex 4 no longer analyzes text in the constructor: NRCLex(text) reads its argument as a lexicon file name,
falls back to the bundled lexicon and analyzes nothing, so `.raw_emotion_scores` does not exist. The text goes
in with `NRCLex().load_raw_text(text)`. NRCLex 3 has only NRCLex(text). nrclex is not pinned, so support both.
"""


def raw_emotion_scores(text, nrclex_class=None):
    """{emotion: count} for text, e.g. {"joy": 2, "trust": 1}; emotions with no word in text are left out."""
    if nrclex_class is None:
        from nrclex import NRCLex as nrclex_class
    if hasattr(nrclex_class, "load_raw_text"):  # NRCLex 4
        emotion_obj = nrclex_class()
        emotion_obj.load_raw_text(text)
    else:  # NRCLex 3
        emotion_obj = nrclex_class(text)
    return dict(getattr(emotion_obj, "raw_emotion_scores", None) or {})


def all_scores_zero(rows, emotions):
    """True when no row has a score above 0 for any of the emotions: no NRC emotion word was found at all."""
    return not any(float(row.get(e, 0) or 0) > 0 for row in rows for e in emotions)
