"""Levenshtein-based string similarity, with no third-party dependency.

Why this module exists
----------------------
The Suite used to compute name similarity with ``fuzzywuzzy.fuzz.ratio``. fuzzywuzzy is a thin
wrapper that uses the C library ``python-Levenshtein`` *when it happens to be installed* and
otherwise falls back, with only a warning, to ``difflib.SequenceMatcher`` -- which implements
Ratcliff/Obershelp, a **different** algorithm. So the tool advertised "Levenshtein edit distance"
while, on any machine without the C library (including the development machine), it computed
something else, and the same corpus could score differently on two installs.

This module implements the edit distance directly. Results are now identical on every
installation, and no wheel has to build for the tool to be correct.

Definitions
-----------
``levenshtein_distance`` is the classic unit-cost edit distance (insert / delete / substitute all
cost 1) -- the number a human means by "how many typos apart are these?".

``levenshtein_ratio`` normalizes to 0-100 using the same convention as ``python-Levenshtein.ratio``:
substitutions are weighted 2 (an insert plus a delete), and the score is
``(len(a) + len(b) - weighted_distance) / (len(a) + len(b))``. Weighting keeps the ratio symmetric
and monotone in the length of the strings being compared.
"""


def levenshtein_distance(s1, s2):
    """Unit-cost Levenshtein edit distance: the number of single-character edits between s1 and s2."""
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    previous = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current = [i + 1]
        for j, c2 in enumerate(s2):
            # deletion, insertion, substitution
            current.append(min(previous[j + 1] + 1, current[j] + 1, previous[j] + (c1 != c2)))
        previous = current
    return previous[-1]


def _weighted_distance(s1, s2):
    """Levenshtein distance with substitutions weighted 2, as python-Levenshtein's ratio() uses."""
    if s1 == s2:
        return 0
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    previous = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current = [i + 1]
        for j, c2 in enumerate(s2):
            current.append(min(previous[j + 1] + 1, current[j] + 1, previous[j] + (2 if c1 != c2 else 0)))
        previous = current
    return previous[-1]


def levenshtein_ratio(s1, s2):
    """Similarity of two strings on a 0-100 scale (100 = identical). Case- and order-sensitive."""
    total = len(s1) + len(s2)
    if total == 0:
        return 100.0
    return round((total - _weighted_distance(s1, s2)) / total * 100, 1)


def _normalize(s):
    return ' '.join(str(s).lower().replace(',', ' ').split())


def _sort_tokens(s):
    return ' '.join(sorted(_normalize(s).split()))


def similarity(s1, s2):
    """Similarity on a 0-100 scale, ignoring case, punctuation spacing and word order.

    Case folding matters for this corpus: newspaper text yields both ``COBB`` and ``Cobb``, which a
    case-sensitive ratio scores 25 -- far below any sane threshold -- so the same name read as two.
    Token sorting catches the other common variant, ``Jim Cobb`` vs ``Cobb, Jim`` (47 when compared
    literally). Sorting can only raise a score, so it never suppresses a match the plain ratio found.
    """
    n1, n2 = _normalize(s1), _normalize(s2)
    score = levenshtein_ratio(n1, n2)
    if ' ' in n1 or ' ' in n2:
        score = max(score, levenshtein_ratio(_sort_tokens(s1), _sort_tokens(s2)))
    return score


def best_match(word, candidates, threshold):
    """Return the CLOSEST candidate to ``word`` above ``threshold``, or None.

    ``candidates`` is a sequence of ``(candidate_word, frequency)`` pairs (the shape the spell
    checker keeps its word lists in); a plain sequence of strings is also accepted.

    Returns ``(candidate_word, frequency, score, edit_distance)``.

    Two behaviours worth stating, because the previous implementation had neither:

    * It returns the *best* match. Scanning for the first candidate over the threshold made the
      answer depend on list order -- ``Flemin`` reported ``Flemming`` merely because it was listed
      before the closer ``Fleming``.
    * A candidate that is byte-for-byte identical to ``word`` is skipped (that is the word itself,
      not a variant of it), but one that differs only in case or word order is *kept* and scores
      100, since an inconsistent ``COBB``/``Cobb`` is exactly the inconsistency being looked for.
    """
    best = None
    for candidate in candidates:
        if isinstance(candidate, (tuple, list)):
            cand_word = candidate[0]
            cand_freq = candidate[1] if len(candidate) > 1 else ''
        else:
            cand_word, cand_freq = candidate, ''
        if cand_word == word:
            continue
        score = similarity(word, cand_word)
        if score < threshold:
            continue
        if best is None or score > best[2]:
            best = (cand_word, cand_freq, score, levenshtein_distance(_normalize(word), _normalize(cand_word)))
    return best
