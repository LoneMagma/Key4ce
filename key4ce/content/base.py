"""Base content provider interface for Key4ce."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class TextContent:
    """A piece of text content for typing practice."""
    id: str
    title: str
    text: str
    source_type: str
    source_ref: str = ""
    author: str = ""
    language: str = "en"
    difficulty: str = "medium"  # easy, medium, hard
    tags: list[str] | None = None
    
    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []
    
    @property
    def word_count(self) -> int:
        """Get the approximate word count."""
        return len(self.text.split())
    
    @property
    def char_count(self) -> int:
        """Get the character count."""
        return len(self.text)


class ContentProvider(ABC):
    """Abstract base class for content providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name."""
        pass
    
    @property
    @abstractmethod
    def source_type(self) -> str:
        """Get the source type identifier."""
        pass
    
    @abstractmethod
    async def get_random(self) -> TextContent:
        """Get a random piece of content.
        
        Returns:
            Random TextContent from this provider
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, content_id: str) -> TextContent | None:
        """Get content by ID.
        
        Args:
            content_id: The content identifier
            
        Returns:
            TextContent if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_available(self, limit: int = 20) -> list[TextContent]:
        """List available content.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of available TextContent
        """
        pass
    
    async def search(self, query: str, limit: int = 10) -> list[TextContent]:
        """Search for content.
        
        Default implementation returns empty list.
        Override for providers that support search.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching TextContent
        """
        return []
    
    def is_available(self) -> bool:
        """Check if this provider is available.
        
        Returns:
            True if the provider can be used
        """
        return True
