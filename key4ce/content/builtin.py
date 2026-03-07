"""
key4ce/content/builtin.py
──────────────────────────
Built-in text pools for all content modes.

Copy guidelines applied throughout:
  - Clear, precise prose. No filler. No padding.
  - Varied sentence length — short punchy lines mixed with longer ones.
  - Realistic character distribution: commas, periods, capitals, numbers in context.
  - Code samples: real, readable Python and shell — not toy snippets.
  - Terminal-operator tone: professional, technical, direct.
  - No clichés. No "lorem ipsum". No juvenile content.
"""

from __future__ import annotations

import random

# ═════════════════════════════════════════════════════════════════
#  Words — high-frequency, useful English vocabulary
# ═════════════════════════════════════════════════════════════════

WORDS = """
ability access account action activity address adjust advance affect agent
agree ahead alert allow always amount analyse apply approach area argument
aspect assert assign attach audit avoid balance base batch begin benefit
build cache call capture change check class clear client close collect
command commit complete component compute config connect consider contain
context control convert copy count create cycle data debug define delay
deploy detail detect develop direct disable display distribute divide
document drop enable encrypt engine ensure entry error event example
execute expand extend factor fail fetch field filter finish flow focus
force format forward function generate group handle hash header include
increase index init input install invoke iterate keep launch layer learn
level limit list load local log manage match measure merge method modify
monitor move name network notice offset option output parse path pause
perform permit place plan policy poll process profile publish purge queue
read reason record reduce register release remove render request reset
resolve response retry return route rule run scale scan schedule search
secure send sequence service set signal sort source split start state
store stream string submit sync system target task template test timeout
trace transform trigger type update use value verify version wait write
""".split()

# ═════════════════════════════════════════════════════════════════
#  Sentences — professional, technical-ish prose
# ═════════════════════════════════════════════════════════════════

SENTENCES = [
    "A consistent naming convention reduces cognitive load and makes codebases navigable without prior context.",
    "Terminal tools reward precision. Every flag, pipe, and redirect reflects an intentional decision about data flow.",
    "The most effective debugging strategy is often the simplest: read the error message carefully before assuming the cause.",
    "Documentation written for a future colleague is nearly always better than documentation written for the author.",
    "Latency compounds. A 50-millisecond delay in five sequential requests produces a 250-millisecond visible lag.",
    "Defaults matter. Most users never change settings, which means the default configuration is the real product.",
    "A well-structured commit message describes why a change was made, not just what was changed.",
    "Clean interfaces emerge from constraints. Reducing the number of decisions a system exposes usually improves it.",
    "Rate limiting is not a punitive measure. It is a design choice that keeps shared infrastructure stable.",
    "Every abstraction hides something. The question is whether what it hides is worth hiding.",
    "Configuration files are code. They deserve the same scrutiny, version control, and review process.",
    "Naming a variable is not a trivial decision. The name you give it is the first documentation of its purpose.",
    "Distributed systems fail in ways that local systems never do. Plan for partial failure as the normal case.",
    "The time you invest in writing a clear specification usually pays back before the first line of code is reviewed.",
    "Idempotency is not always easy to achieve, but it makes systems dramatically safer to operate and recover.",
    "Logging should be informative without being verbose. A log that contains everything is as useless as one with nothing.",
    "Rollback plans are as important as deployment plans. The ability to reverse a change reduces the cost of making it.",
    "Typing speed correlates with the ability to keep pace with thought. The skill compounds across every task that involves a keyboard.",
    "The fewer moving parts a system has, the fewer things can go wrong at three in the morning.",
    "Technical debt is not inherently bad. The problem is when it accumulates without acknowledgement or a plan.",
    "A good API is one you can use without reading the documentation twice.",
    "Security is not a feature to be added later. It is a property of the architecture from the first commit.",
    "Observability is the difference between knowing a system is broken and knowing why it is broken.",
    "The right tool for a job is the one the team understands deeply, not the one with the most features.",
    "Performance optimisation without measurement is just guessing with extra steps.",
    "Write code that the person debugging it at midnight will thank you for.",
    "A test that never fails is not a safety net. It is a false sense of confidence.",
    "Simplicity is harder to achieve than complexity. It requires knowing what to leave out.",
    "State is the source of most bugs. The less mutable state a system carries, the easier it is to reason about.",
    "Good defaults, clear errors, and short feedback loops are the three properties that make tools enjoyable to use.",
]

# ═════════════════════════════════════════════════════════════════
#  Quotes — genuine, professional, technically adjacent
# ═════════════════════════════════════════════════════════════════

QUOTES = [
    "The art of programming is the art of organising complexity. — Edsger Dijkstra",
    "Simplicity is the ultimate sophistication. — Leonardo da Vinci",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand. — Martin Fowler",
    "First, solve the problem. Then, write the code. — John Johnson",
    "Before software can be reusable it first has to be usable. — Ralph Johnson",
    "The best performance improvement is the transition from the nonworking state to the working state. — John Ousterhout",
    "Walking on water and developing software from a specification are easy if both are frozen. — Edward V. Berard",
    "It always takes longer than you expect, even when you take into account Hofstadter's Law. — Douglas Hofstadter",
    "Measuring programming progress by lines of code is like measuring aircraft building progress by weight. — Bill Gates",
    "The most dangerous phrase in the language is: we have always done it this way. — Grace Hopper",
    "Software is a great combination of artistry and engineering. — Bill Gates",
    "The function of good software is to make the complex appear to be simple. — Grady Booch",
    "One of my most productive days was throwing away 1000 lines of code. — Ken Thompson",
    "Programs must be written for people to read, and only incidentally for machines to execute. — Abelson and Sussman",
    "The computing scientist's main challenge is not to get confused by the complexities of his own making. — Dijkstra",
    "Debugging is twice as hard as writing the code in the first place. — Brian Kernighan",
    "Premature optimisation is the root of all evil. — Donald Knuth",
    "Make it work, make it right, make it fast. In that order. — Kent Beck",
    "Software entities should be open for extension, but closed for modification. — Bertrand Meyer",
    "There are only two hard things in computer science: cache invalidation and naming things. — Phil Karlton",
]

# ═════════════════════════════════════════════════════════════════
#  Code — real, readable Python snippets
# ═════════════════════════════════════════════════════════════════

CODE_SAMPLES = [
    """def retry(fn, attempts=3, delay=1.0):
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            if i == attempts - 1:
                raise
            time.sleep(delay * (i + 1))""",

    """def paginate(query, page_size=100):
    offset = 0
    while True:
        batch = query.offset(offset).limit(page_size).all()
        if not batch:
            break
        yield from batch
        offset += page_size""",

    """class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self._calls = []

    def is_allowed(self):
        now = time.time()
        self._calls = [t for t in self._calls if now - t < self.period]
        if len(self._calls) < self.max_calls:
            self._calls.append(now)
            return True
        return False""",

    """def flatten(nested, depth=None):
    for item in nested:
        if isinstance(item, list) and depth != 0:
            yield from flatten(item, None if depth is None else depth - 1)
        else:
            yield item""",

    """def chunk(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            return
        yield batch""",

    """@contextmanager
def timer(label="elapsed"):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")""",

    """def deep_merge(base, override):
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result""",

    """def safe_get(mapping, *keys, default=None):
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current""",
]

# ═════════════════════════════════════════════════════════════════
#  Numbers — realistic numeric sequences
# ═════════════════════════════════════════════════════════════════

NUMBER_PHRASES = [
    "192.168.1.1 255.255.255.0 10.0.0.0 172.16.0.1 127.0.0.1",
    "2024-01-15 2023-12-31 2025-06-01 1999-08-24 2010-03-07",
    "3.14159 2.71828 1.61803 0.69315 1.41421 1.73205",
    "1024 2048 4096 8192 16384 32768 65536 131072",
    "100 200 400 800 1600 3200 6400 12800 25600",
    "8080 443 80 22 3306 5432 6379 27017 9200",
    "0x1A 0xFF 0x4C 0x2B 0x8E 0xAD 0x7F 0x00 0xC3",
    "273.15 -40.0 100.0 37.0 -196.0 2730.0 5778.0",
    "1e3 2.5e-4 9.81e0 6.674e-11 1.380e-23 6.022e23",
    "1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987",
]

# ═════════════════════════════════════════════════════════════════
#  Public interface
# ═════════════════════════════════════════════════════════════════

def get_builtin_text(mode: str, target_words: int = 50) -> str:
    """
    Return a text string for the given mode and approximate word count.
    """
    mode = mode.lower().strip()

    if mode == "words":
        return _words_text(target_words)
    elif mode == "sentences":
        return _sentences_text(target_words)
    elif mode == "quotes":
        return _quotes_text(target_words)
    elif mode == "code":
        return _code_text()
    elif mode == "numbers":
        return _numbers_text(target_words)
    else:
        return _words_text(target_words)


def _words_text(target: int) -> str:
    words = random.sample(WORDS, min(target, len(WORDS)))
    if len(words) < target:
        words += random.choices(WORDS, k=target - len(words))
    return " ".join(words[:target])


def _sentences_text(target_words: int) -> str:
    pool    = random.sample(SENTENCES, len(SENTENCES))
    result  = []
    count   = 0
    for s in pool:
        result.append(s)
        count += len(s.split())
        if count >= target_words:
            break
    return " ".join(result)


def _quotes_text(target_words: int) -> str:
    pool   = random.sample(QUOTES, len(QUOTES))
    result = []
    count  = 0
    for q in pool:
        result.append(q)
        count += len(q.split())
        if count >= target_words:
            break
    return " ".join(result)


def _code_text() -> str:
    return random.choice(CODE_SAMPLES).strip()


def _numbers_text(target_words: int) -> str:
    pool   = random.sample(NUMBER_PHRASES, len(NUMBER_PHRASES))
    result = []
    count  = 0
    for phrase in pool:
        result.append(phrase)
        count += len(phrase.split())
        if count >= target_words:
            break
    return " ".join(result)
