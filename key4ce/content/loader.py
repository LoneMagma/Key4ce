"""External content fetcher with local caching.

Sources:
  - wikipedia  : random Wikipedia article extract
  - quote      : random quote via quotable.io

All fetches are synchronous with a 3-second timeout.
Results are cached in ~/.key4ce/cache/ to avoid repeated network calls.
On any network failure, returns None — callers must fall back to builtin.
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

CACHE_DIR = Path.home() / ".key4ce" / "cache"
TIMEOUT = 4  # seconds


# ── Internal helpers ──────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    h = hashlib.md5(key.encode()).hexdigest()[:10]
    return CACHE_DIR / f"{key}_{h}.txt"


def _fetch_json(url: str) -> dict | list | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "key4ce/2.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _clean(text: str) -> str:
    """Strip non-ASCII, collapse whitespace, normalize to lowercase."""
    text = text.encode("ascii", errors="ignore").decode()
    text = re.sub(r"\s+", " ", text).strip().lower()
    # Remove citation markers like [1], [note 2]
    text = re.sub(r"\[\w+\s*\d*\]", "", text)
    return text.strip()


def _cache_get(key: str) -> str | None:
    p = _cache_path(key)
    if p.exists():
        try:
            return p.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def _cache_set(key: str, value: str) -> None:
    try:
        _cache_path(key).write_text(value, encoding="utf-8")
    except Exception:
        pass


# ── Wikipedia ─────────────────────────────────────────────────────────────────

def fetch_wikipedia(use_cache: bool = True) -> str | None:
    """Fetch a random Wikipedia article extract, ~100-250 words."""
    cache_key = "wikipedia"
    if use_cache:
        cached = _cache_get(cache_key)
        if cached:
            return cached

    data = _fetch_json(
        "https://en.wikipedia.org/api/rest_v1/page/random/summary"
    )
    if not data or not isinstance(data, dict):
        return None

    extract: str = data.get("extract", "")
    if len(extract) < 40:
        return None

    text = _clean(extract)
    # Trim to roughly 200 words
    words = text.split()
    if len(words) > 200:
        words = words[:200]
    text = " ".join(words)

    if len(text) < 40:
        return None

    _cache_set(cache_key, text)
    return text


# ── Quotable ──────────────────────────────────────────────────────────────────

def fetch_quote(use_cache: bool = True) -> str | None:
    """Fetch a random quote from quotable.io (~20-50 words)."""
    cache_key = "quote"
    if use_cache:
        cached = _cache_get(cache_key)
        if cached:
            return cached

    data = _fetch_json("https://api.quotable.io/quotes/random")
    if not data:
        return None

    # API returns a list of quote objects
    if isinstance(data, list) and data:
        item = data[0]
    elif isinstance(data, dict):
        item = data
    else:
        return None

    content = item.get("content", "")
    author = item.get("author", "")

    if not content:
        return None

    text = _clean(f"{content} — {author}")
    if len(text) < 20:
        return None

    _cache_set(cache_key, text)
    return text


# ── Dispatcher ────────────────────────────────────────────────────────────────

def get_external_text(source: str, bust_cache: bool = False) -> str | None:
    """Public API: fetch content for a given external source name.

    Args:
        source: 'wikipedia' or 'quote'
        bust_cache: If True, always fetch fresh content.

    Returns:
        Cleaned text string, or None on failure.
    """
    use_cache = not bust_cache
    if source == "wikipedia":
        return fetch_wikipedia(use_cache)
    if source == "quote":
        return fetch_quote(use_cache)
    return None


EXTERNAL_CATEGORIES: dict[str, dict] = {
    "wikipedia": {
        "label": "Wikipedia",
        "description": "Random article extract — varied, real-world text",
        "emoji": "🌐",
        "requires_network": True,
    },
    "quote": {
        "label": "Live Quote",
        "description": "Fresh random quote from quotable.io",
        "emoji": "✨",
        "requires_network": True,
    },
}
