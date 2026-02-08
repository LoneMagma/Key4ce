"""Built-in content provider for Key4ce.

Provides sample texts for offline use.
"""

from __future__ import annotations

import random
from typing import Any

from key4ce.content.base import ContentProvider, TextContent


# Built-in sample texts covering various difficulty levels
BUILTIN_TEXTS = [
    # Easy - Common words, short sentences
    TextContent(
        id="easy_common_1",
        title="Common Words",
        text="The quick brown fox jumps over the lazy dog. A simple sentence with all letters.",
        source_type="builtin",
        author="Sample",
        difficulty="easy",
        tags=["pangram", "short"],
    ),
    TextContent(
        id="easy_common_2",
        title="Daily Activities",
        text="I wake up early in the morning. I eat breakfast and drink coffee. Then I go to work. The day is long but good.",
        source_type="builtin",
        author="Sample",
        difficulty="easy",
        tags=["simple", "daily"],
    ),
    TextContent(
        id="easy_common_3",
        title="Simple Story",
        text="The cat sat on the mat. It was a warm day. The sun was bright. The cat was happy. It closed its eyes and slept.",
        source_type="builtin",
        author="Sample",
        difficulty="easy",
        tags=["story", "simple"],
    ),
    
    # Medium - Varied vocabulary, longer sentences
    TextContent(
        id="medium_tech_1",
        title="Technology Basics",
        text="Computers have transformed the way we work and communicate. Modern systems process millions of operations per second, enabling complex applications that were once impossible. Programming languages allow developers to create software that solves real-world problems.",
        source_type="builtin",
        author="Sample",
        difficulty="medium",
        tags=["technology", "informative"],
    ),
    TextContent(
        id="medium_nature_1",
        title="The Forest",
        text="Deep within the ancient forest, sunlight filters through the dense canopy above. Moss-covered trees stand like silent guardians, their roots intertwined beneath the soft earth. The air is fresh and carries the scent of pine needles and wild flowers.",
        source_type="builtin",
        author="Sample",
        difficulty="medium",
        tags=["nature", "descriptive"],
    ),
    TextContent(
        id="medium_science_1",
        title="The Universe",
        text="The universe is vast beyond human comprehension. Billions of galaxies, each containing billions of stars, stretch across the cosmic void. Our own Milky Way is just one spiral galaxy among countless others, spinning through space at incredible speeds.",
        source_type="builtin",
        author="Sample",
        difficulty="medium",
        tags=["science", "space"],
    ),
    TextContent(
        id="medium_history_1",
        title="Ancient Civilizations",
        text="Throughout history, great civilizations have risen and fallen. The Egyptians built pyramids that still stand today. The Romans constructed roads and aqueducts across their vast empire. Each culture left behind knowledge and artifacts that continue to fascinate us.",
        source_type="builtin",
        author="Sample",
        difficulty="medium",
        tags=["history", "culture"],
    ),
    
    # Hard - Complex vocabulary, technical content
    TextContent(
        id="hard_code_1",
        title="Python Functions",
        text="def calculate_fibonacci(n: int) -> int: if n <= 1: return n else: return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
        source_type="builtin",
        author="Sample",
        difficulty="hard",
        tags=["code", "python"],
    ),
    TextContent(
        id="hard_code_2",
        title="JavaScript Promise",
        text="const fetchData = async (url) => { try { const response = await fetch(url); const data = await response.json(); return data; } catch (error) { console.error('Error:', error); throw error; } };",
        source_type="builtin",
        author="Sample",
        difficulty="hard",
        tags=["code", "javascript"],
    ),
    TextContent(
        id="hard_philosophy_1",
        title="Philosophical Inquiry",
        text="The epistemological foundations of empiricism suggest that knowledge derives primarily from sensory experience. This contrasts with rationalist traditions that emphasize innate ideas and deductive reasoning. Contemporary philosophy continues to grapple with these fundamental questions about the nature of knowledge and reality.",
        source_type="builtin",
        author="Sample",
        difficulty="hard",
        tags=["philosophy", "academic"],
    ),
    TextContent(
        id="hard_science_1",
        title="Quantum Mechanics",
        text="Quantum superposition allows particles to exist in multiple states simultaneously until observation collapses the wave function. This probabilistic nature of quantum mechanics challenged classical determinism and led to ongoing debates about the interpretation of quantum theory.",
        source_type="builtin",
        author="Sample",
        difficulty="hard",
        tags=["science", "physics"],
    ),
    
    # Practice-focused texts
    TextContent(
        id="practice_home_row",
        title="Home Row Practice",
        text="asdf jkl; asdf jkl; fjdk slaf fjdk slaf asdfjkl; asdfjkl; fall lads fall lads ask dad ask dad",
        source_type="builtin",
        author="Practice",
        difficulty="easy",
        tags=["practice", "home-row"],
    ),
    TextContent(
        id="practice_numbers",
        title="Number Practice",
        text="1234567890 0987654321 1a2b3c4d5e 2024 2025 2026 100 200 300 42 128 256 512 1024",
        source_type="builtin",
        author="Practice",
        difficulty="medium",
        tags=["practice", "numbers"],
    ),
    TextContent(
        id="practice_symbols",
        title="Symbol Practice",
        text="!@#$%^&*() hello@email.com https://example.com file.txt config.yaml <div class='test'> [array, items] {key: value}",
        source_type="builtin",
        author="Practice",
        difficulty="hard",
        tags=["practice", "symbols"],
    ),
]


class BuiltinContent(ContentProvider):
    """Provider for built-in sample texts."""
    
    def __init__(self) -> None:
        self._texts = {t.id: t for t in BUILTIN_TEXTS}
    
    @property
    def name(self) -> str:
        return "Built-in Samples"
    
    @property
    def source_type(self) -> str:
        return "builtin"
    
    async def get_random(self) -> TextContent:
        """Get a random built-in text."""
        return random.choice(BUILTIN_TEXTS)
    
    async def get_random_by_difficulty(self, difficulty: str) -> TextContent:
        """Get a random text of specified difficulty.
        
        Args:
            difficulty: easy, medium, or hard
            
        Returns:
            Random TextContent of that difficulty
        """
        filtered = [t for t in BUILTIN_TEXTS if t.difficulty == difficulty]
        if not filtered:
            return await self.get_random()
        return random.choice(filtered)
    
    async def get_by_id(self, content_id: str) -> TextContent | None:
        """Get a specific text by ID."""
        return self._texts.get(content_id)
    
    async def list_available(self, limit: int = 20) -> list[TextContent]:
        """List all available built-in texts."""
        return BUILTIN_TEXTS[:limit]
    
    async def list_by_difficulty(self, difficulty: str) -> list[TextContent]:
        """List texts by difficulty level.
        
        Args:
            difficulty: easy, medium, or hard
            
        Returns:
            List of texts with that difficulty
        """
        return [t for t in BUILTIN_TEXTS if t.difficulty == difficulty]
    
    async def list_by_tag(self, tag: str) -> list[TextContent]:
        """List texts by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of texts with that tag
        """
        return [t for t in BUILTIN_TEXTS if tag in (t.tags or [])]
    
    async def search(self, query: str, limit: int = 10) -> list[TextContent]:
        """Search built-in texts by title or content."""
        query_lower = query.lower()
        results = []
        
        for text in BUILTIN_TEXTS:
            if query_lower in text.title.lower() or query_lower in text.text.lower():
                results.append(text)
                if len(results) >= limit:
                    break
        
        return results
