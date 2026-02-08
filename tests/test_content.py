"""Tests for content providers."""

import pytest
from key4ce.content.base import ContentProvider, TextContent
from key4ce.content.builtin import BuiltinContent, BUILTIN_TEXTS


class TestTextContent:
    """Tests for TextContent model."""
    
    def test_word_count(self):
        """Test word count calculation."""
        content = TextContent(
            id="test",
            title="Test",
            text="one two three four five",
            source_type="test",
        )
        
        assert content.word_count == 5
    
    def test_char_count(self):
        """Test character count."""
        content = TextContent(
            id="test",
            title="Test",
            text="hello",
            source_type="test",
        )
        
        assert content.char_count == 5


class TestBuiltinContent:
    """Tests for BuiltinContent provider."""
    
    @pytest.fixture
    def provider(self):
        """Create a builtin content provider."""
        return BuiltinContent()
    
    def test_provider_properties(self, provider):
        """Test provider name and source type."""
        assert provider.name == "Built-in Samples"
        assert provider.source_type == "builtin"
    
    @pytest.mark.asyncio
    async def test_get_random(self, provider):
        """Test getting random content."""
        content = await provider.get_random()
        
        assert content is not None
        assert content.text
        assert content.source_type == "builtin"
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, provider):
        """Test getting content by ID."""
        # Use a known ID from builtin texts
        content = await provider.get_by_id("easy_common_1")
        
        assert content is not None
        assert content.id == "easy_common_1"
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, provider):
        """Test getting non-existent content."""
        content = await provider.get_by_id("nonexistent-id")
        
        assert content is None
    
    @pytest.mark.asyncio
    async def test_list_available(self, provider):
        """Test listing available content."""
        available = await provider.list_available()
        
        assert len(available) > 0
        assert all(isinstance(c, TextContent) for c in available)
    
    @pytest.mark.asyncio
    async def test_list_by_difficulty(self, provider):
        """Test filtering by difficulty."""
        easy = await provider.list_by_difficulty("easy")
        hard = await provider.list_by_difficulty("hard")
        
        assert len(easy) > 0
        assert len(hard) > 0
        assert all(c.difficulty == "easy" for c in easy)
        assert all(c.difficulty == "hard" for c in hard)
    
    @pytest.mark.asyncio
    async def test_get_random_by_difficulty(self, provider):
        """Test getting random content by difficulty."""
        content = await provider.get_random_by_difficulty("medium")
        
        assert content.difficulty == "medium"
    
    @pytest.mark.asyncio
    async def test_search(self, provider):
        """Test searching content."""
        results = await provider.search("quick brown fox")
        
        assert len(results) >= 1
    
    def test_builtin_texts_have_required_fields(self):
        """Test that all builtin texts have required fields."""
        for text in BUILTIN_TEXTS:
            assert text.id
            assert text.title
            assert text.text
            assert text.source_type == "builtin"
            assert text.difficulty in ("easy", "medium", "hard")
