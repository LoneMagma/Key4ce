"""Built-in practice content for key4ce."""
from __future__ import annotations
import random


# ── Word lists ─────────────────────────────────────────────────────────────────

COMMON_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
    "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
    "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know",
    "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how",
    "our", "work", "first", "well", "way", "even", "new", "want", "because",
    "any", "these", "give", "day", "most", "us", "great", "between", "need",
    "large", "often", "hand", "high", "place", "hold", "turn", "help",
    "start", "show", "hear", "play", "run", "move", "live", "believe",
    "hold", "bring", "happen", "write", "provide", "sit", "stand", "lose",
    "pay", "meet", "include", "continue", "set", "learn", "change", "lead",
    "understand", "watch", "follow", "stop", "create", "speak", "read",
    "spend", "grow", "open", "walk", "win", "offer", "remember", "love",
    "consider", "appear", "buy", "wait", "serve", "die", "send", "expect",
    "build", "stay", "fall", "cut", "reach", "kill", "remain", "suggest",
]

SENTENCES = [
    "the quick brown fox jumps over the lazy dog",
    "pack my box with five dozen liquor jugs",
    "how vexingly quick daft zebras jump",
    "the five boxing wizards jump quickly",
    "sphinx of black quartz judge my vow",
    "practice makes perfect and patience pays off",
    "focus on accuracy first and speed will follow naturally",
    "every expert was once a beginner who refused to give up",
    "small consistent improvements lead to remarkable results over time",
    "your fingers remember patterns better than your conscious mind does",
    "the best time to start improving was yesterday the second best is now",
    "slow down to speed up let accuracy guide your fingers first",
    "typing is a skill built through repetition not through rushing",
    "keep your wrists relaxed and let your fingers find their natural rhythm",
    "consistency beats intensity when building any long term skill like typing",
    "each keystroke is a small decision that shapes your overall fluency",
    "the keyboard is an instrument and like any instrument practice rewires your brain",
    "errors are not failures they are data points that guide your improvement",
    "building muscle memory takes time but once built it becomes effortless",
    "trust the process and enjoy the incremental progress you make each day",
    "technology is best when it brings people together and helps them communicate clearly",
    "a smooth workflow depends on the tools you use and how well you use them",
    "clear communication starts with the ability to express your thoughts quickly",
    "the mark of a skilled typist is consistency not just sheer speed",
    "in the long run the habit of daily practice outweighs any single session",
]

QUOTES = [
    "whether you think you can or you think you cannot you are right henry ford",
    "the only way to do great work is to love what you do steve jobs",
    "in the middle of difficulty lies opportunity albert einstein",
    "it does not matter how slowly you go as long as you do not stop confucius",
    "success is not final failure is not fatal it is the courage to continue that counts winston churchill",
    "the future belongs to those who believe in the beauty of their dreams eleanor roosevelt",
    "it always seems impossible until it is done nelson mandela",
    "strive not to be a success but rather to be of value albert einstein",
    "the best revenge is massive success frank sinatra",
    "life is what happens to you while you are busy making other plans john lennon",
    "you miss one hundred percent of the shots you never take wayne gretzky",
    "whether you think you can or you think you cannot you are right henry ford",
    "the only limit to our realization of tomorrow will be our doubts of today franklin d roosevelt",
    "do not go where the path may lead go instead where there is no path and leave a trail emerson",
    "two roads diverged in a wood and i took the one less traveled by and that has made all the difference robert frost",
]

CODE_SNIPPETS = [
    "def greet(name): return f'hello {name}'",
    "for i in range(10): print(i * i)",
    "result = [x for x in data if x > 0]",
    "with open('file.txt', 'r') as f: content = f.read()",
    "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)",
    "class Node: def __init__(self, val): self.val = val; self.next = None",
    "sorted_list = sorted(items, key=lambda x: x.name)",
    "words = text.strip().lower().split()",
    "count = sum(1 for char in text if char.isalpha())",
    "pairs = {k: v for k, v in zip(keys, values)}",
    "import os; path = os.path.join(base, 'data', 'records.json')",
    "def clamp(val, lo, hi): return max(lo, min(hi, val))",
    "avg = sum(values) / len(values) if values else 0",
    "unique = list(dict.fromkeys(items))",
    "matrix = [[0] * cols for _ in range(rows)]",
    "def retry(fn, attempts=3): return next(fn() for _ in range(attempts))",
    "headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}",
    "chunks = [data[i:i+n] for i in range(0, len(data), n)]",
]

NUMBERS = [
    "1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0",
    "3 14159 26535 89793 23846 26433 83279 50288",
    "2 71828 18284 59045 23536 02874 71352 66249",
    "100 200 300 400 500 600 700 800 900 1000",
    "1024 2048 4096 8192 16384 32768 65536 131072",
    "192 168 1 1 255 255 255 0 10 0 0 1 172 16 0 1",
    "42 17 99 3 58 71 24 86 13 67 45 92 36 81 29",
    "2024 2025 2026 1999 2000 1984 1776 1066 1492",
]


# ── Category definitions ───────────────────────────────────────────────────────

CATEGORIES: dict[str, dict] = {
    "words": {
        "label": "Common Words",
        "description": "Top 200 words — great for finger placement",
        "emoji": "📝",
    },
    "sentences": {
        "label": "Sentences",
        "description": "Natural prose with varied rhythm",
        "emoji": "📖",
    },
    "quotes": {
        "label": "Quotes",
        "description": "Famous quotes — motivating and varied",
        "emoji": "💬",
    },
    "code": {
        "label": "Code",
        "description": "Python snippets — symbols and syntax",
        "emoji": "🖥",
    },
    "numbers": {
        "label": "Numbers",
        "description": "Numeric sequences — for data entry focus",
        "emoji": "🔢",
    },
}


# ── Public API ─────────────────────────────────────────────────────────────────

def get_text(category: str, word_target: int = 40) -> str:
    """Return a ready-to-type string for the given category.

    Args:
        category: One of the CATEGORIES keys.
        word_target: Approximate number of words to aim for.

    Returns:
        A clean, single-line string to type.
    """
    if category == "words":
        pool = COMMON_WORDS.copy()
        random.shuffle(pool)
        words: list[str] = []
        while len(words) < word_target:
            words.extend(pool)
        return " ".join(words[:word_target])

    elif category == "sentences":
        pool = SENTENCES.copy()
        random.shuffle(pool)
        result = ""
        for s in pool:
            if len(result.split()) >= word_target:
                break
            result = (result + " " + s).strip()
        return result

    elif category == "quotes":
        pool = QUOTES.copy()
        random.shuffle(pool)
        result = ""
        for q in pool:
            if len(result.split()) >= word_target:
                break
            result = (result + " " + q).strip()
        return result

    elif category == "code":
        pool = CODE_SNIPPETS.copy()
        random.shuffle(pool)
        result = ""
        for snippet in pool:
            if len(result.split()) >= word_target:
                break
            result = (result + "  " + snippet).strip()
        return result

    elif category == "numbers":
        pool = NUMBERS.copy()
        random.shuffle(pool)
        result = ""
        for n in pool:
            if len(result.split()) >= word_target:
                break
            result = (result + " " + n).strip()
        return result

    # Fallback
    return get_text("sentences", word_target)

from key4ce.content.base import TextContent, ContentProvider


BUILTIN_TEXTS: list[TextContent] = [
    TextContent(
        id="easy_common_1",
        title="Easy Common 1",
        text="the quick brown fox jumps over the lazy dog",
        source_type="builtin",
        difficulty="easy",
        tags=["common", "pangram"],
    ),
    TextContent(
        id="easy_common_2",
        title="Easy Common 2",
        text="practice makes perfect and patience pays off",
        source_type="builtin",
        difficulty="easy",
        tags=["common"],
    ),
    TextContent(
        id="medium_sentence_1",
        title="Medium Sentence 1",
        text="small consistent improvements lead to remarkable results over time",
        source_type="builtin",
        difficulty="medium",
        tags=["sentence"],
    ),
    TextContent(
        id="hard_code_1",
        title="Hard Code 1",
        text="def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)",
        source_type="builtin",
        difficulty="hard",
        tags=["code"],
    ),
]


class BuiltinContent(ContentProvider):
    @property
    def name(self) -> str:
        return "Built-in Samples"

    @property
    def source_type(self) -> str:
        return "builtin"

    async def get_random(self) -> TextContent:
        return random.choice(BUILTIN_TEXTS)

    async def get_by_id(self, content_id: str) -> TextContent | None:
        for item in BUILTIN_TEXTS:
            if item.id == content_id:
                return item
        return None

    async def list_available(self, limit: int = 20) -> list[TextContent]:
        return BUILTIN_TEXTS[:limit]

    async def list_by_difficulty(self, difficulty: str, limit: int = 20) -> list[TextContent]:
        items = [i for i in BUILTIN_TEXTS if i.difficulty == difficulty]
        return items[:limit]

    async def get_random_by_difficulty(self, difficulty: str) -> TextContent:
        items = await self.list_by_difficulty(difficulty)
        if not items:
            return await self.get_random()
        return random.choice(items)

    async def search(self, query: str, limit: int = 10) -> list[TextContent]:
        q = query.lower().strip()
        if not q:
            return []
        matched = [
            item
            for item in BUILTIN_TEXTS
            if q in item.title.lower() or q in item.text.lower() or any(q in t for t in item.tags or [])
        ]
        return matched[:limit]
