"""Focus mode text generator — creates practice text targeting weak spots."""
from __future__ import annotations

import random
from collections import Counter

from key4ce.content.builtin import COMMON_WORDS, SENTENCES


# ── Word bank helpers ─────────────────────────────────────────────────────────

def _words_containing(digraph: str, pool: list[str] | None = None) -> list[str]:
    """Return words from pool that contain the given two-char sequence."""
    if pool is None:
        pool = COMMON_WORDS
    dg = digraph.lower()
    return [w for w in pool if dg in w.lower()]


def _score_word(word: str, digraphs: list[str], problem_chars: list[str]) -> int:
    """Score a word higher the more target patterns it contains."""
    word_l = word.lower()
    score = 0
    for dg in digraphs:
        if dg in word_l:
            score += 3
    for ch in problem_chars:
        score += word_l.count(ch)
    return score


# ── Public API ────────────────────────────────────────────────────────────────

def generate_focus_text(
    weak_digraphs: list[str],
    problem_chars: list[str],
    word_target: int = 40,
) -> str:
    """Generate a typing text heavily biased toward weak digraphs and problem chars.

    Strategy:
      - 60 % high-scoring words (contain at least one target pattern)
      - 40 % filler common words (to keep text natural)

    Falls back to a shuffled SENTENCES excerpt if no matching words found.
    """
    if not weak_digraphs and not problem_chars:
        # Nothing specific to target — return a random sentences excerpt
        pool = SENTENCES.copy()
        random.shuffle(pool)
        out = ""
        for s in pool:
            out = (out + " " + s).strip()
            if len(out.split()) >= word_target:
                break
        return " ".join(out.split()[:word_target])

    # Score every word in our pool
    pool = COMMON_WORDS[:]
    scored = [(w, _score_word(w, weak_digraphs, problem_chars)) for w in pool]
    scored.sort(key=lambda x: -x[1])

    high = [w for w, s in scored if s > 0]
    filler = [w for w, s in scored if s == 0]

    if not high:
        high = filler  # fallback: no matching words, just use all

    # Mix: 60% targeted, 40% filler
    n_high = max(1, int(word_target * 0.6))
    n_filler = word_target - n_high

    selected: list[str] = []

    # Sample with replacement so we can always hit the target count
    if high:
        for _ in range(n_high):
            selected.append(random.choice(high))
    if filler:
        for _ in range(n_filler):
            selected.append(random.choice(filler))

    # Shuffle so it doesn't feel repetitive
    random.shuffle(selected)
    return " ".join(selected[:word_target])


def describe_focus(
    weak_digraphs: list[str], problem_chars: list[str]
) -> str:
    """Return a one-line description of what will be practiced."""
    parts = []
    if weak_digraphs:
        parts.append("digraphs: " + ", ".join(f"'{d}'" for d in weak_digraphs[:3]))
    if problem_chars:
        parts.append("keys: " + ", ".join(f"'{c}'" for c in problem_chars[:3]))
    return "  ·  ".join(parts) if parts else "general practice"
