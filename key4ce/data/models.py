"""Data models for Key4ce."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class Session:
    """A typing session record."""
    id: str
    started_at: datetime
    ended_at: datetime | None = None
    source_type: str = "builtin"  # builtin, custom, gutenberg, github
    source_ref: str = ""
    wpm_final: float = 0.0
    accuracy: float = 0.0
    total_chars: int = 0
    total_errors: int = 0
    max_combo: int = 0
    keystrokes_json: str = "[]"
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "source_type": self.source_type,
            "source_ref": self.source_ref,
            "wpm_final": self.wpm_final,
            "accuracy": self.accuracy,
            "total_chars": self.total_chars,
            "total_errors": self.total_errors,
            "max_combo": self.max_combo,
            "keystrokes_json": self.keystrokes_json,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            source_type=data.get("source_type", "builtin"),
            source_ref=data.get("source_ref", ""),
            wpm_final=data.get("wpm_final", 0.0),
            accuracy=data.get("accuracy", 0.0),
            total_chars=data.get("total_chars", 0),
            total_errors=data.get("total_errors", 0),
            max_combo=data.get("max_combo", 0),
            keystrokes_json=data.get("keystrokes_json", "[]"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )


@dataclass
class UserStats:
    """Aggregated user statistics."""
    total_sessions: int = 0
    total_chars_typed: int = 0
    total_time_seconds: float = 0.0
    avg_wpm: float = 0.0
    best_wpm: float = 0.0
    avg_accuracy: float = 0.0
    best_accuracy: float = 0.0
    longest_combo: int = 0
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_sessions": self.total_sessions,
            "total_chars_typed": self.total_chars_typed,
            "total_time_seconds": self.total_time_seconds,
            "avg_wpm": self.avg_wpm,
            "best_wpm": self.best_wpm,
            "avg_accuracy": self.avg_accuracy,
            "best_accuracy": self.best_accuracy,
            "longest_combo": self.longest_combo,
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserStats:
        """Create from dictionary."""
        return cls(
            total_sessions=data.get("total_sessions", 0),
            total_chars_typed=data.get("total_chars_typed", 0),
            total_time_seconds=data.get("total_time_seconds", 0.0),
            avg_wpm=data.get("avg_wpm", 0.0),
            best_wpm=data.get("best_wpm", 0.0),
            avg_accuracy=data.get("avg_accuracy", 0.0),
            best_accuracy=data.get("best_accuracy", 0.0),
            longest_combo=data.get("longest_combo", 0),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
        )


@dataclass
class Achievement:
    """An achievement that can be unlocked."""
    id: str
    name: str
    description: str
    icon: str = "*"  # ASCII icon
    category: str = "general"  # speed, accuracy, consistency, streak, special
    target: int = 1
    progress: int = 0
    unlocked_at: datetime | None = None
    
    @property
    def is_unlocked(self) -> bool:
        """Check if achievement is unlocked."""
        return self.unlocked_at is not None
    
    @property
    def progress_percent(self) -> float:
        """Get progress as percentage."""
        if self.target == 0:
            return 100.0
        return min(100.0, (self.progress / self.target) * 100)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "target": self.target,
            "progress": self.progress,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Achievement:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            icon=data.get("icon", "*"),
            category=data.get("category", "general"),
            target=data.get("target", 1),
            progress=data.get("progress", 0),
            unlocked_at=datetime.fromisoformat(data["unlocked_at"]) if data.get("unlocked_at") else None,
        )


# Default achievements to create on first run
DEFAULT_ACHIEVEMENTS = [
    Achievement(
        id="first_session",
        name="First Steps",
        description="Complete your first typing session",
        icon="[>]",
        category="general",
        target=1,
    ),
    Achievement(
        id="speed_50",
        name="Getting Warmed Up",
        description="Reach 50 WPM",
        icon=">>",
        category="speed",
        target=50,
    ),
    Achievement(
        id="speed_75",
        name="Speed Runner",
        description="Reach 75 WPM",
        icon=">>>",
        category="speed",
        target=75,
    ),
    Achievement(
        id="speed_100",
        name="Centurion",
        description="Reach 100 WPM",
        icon="!>>",
        category="speed",
        target=100,
    ),
    Achievement(
        id="accuracy_95",
        name="Precision",
        description="Achieve 95% accuracy",
        icon="[+]",
        category="accuracy",
        target=95,
    ),
    Achievement(
        id="accuracy_99",
        name="Perfect Touch",
        description="Achieve 99% accuracy",
        icon="[!]",
        category="accuracy",
        target=99,
    ),
    Achievement(
        id="combo_25",
        name="Combo Starter",
        description="Reach a 25 character combo",
        icon="x25",
        category="streak",
        target=25,
    ),
    Achievement(
        id="combo_50",
        name="Chain Master",
        description="Reach a 50 character combo",
        icon="x50",
        category="streak",
        target=50,
    ),
    Achievement(
        id="combo_100",
        name="Unstoppable",
        description="Reach a 100 character combo",
        icon="x!!",
        category="streak",
        target=100,
    ),
    Achievement(
        id="sessions_10",
        name="Regular",
        description="Complete 10 sessions",
        icon="[10]",
        category="general",
        target=10,
    ),
    Achievement(
        id="sessions_50",
        name="Dedicated",
        description="Complete 50 sessions",
        icon="[50]",
        category="general",
        target=50,
    ),
    Achievement(
        id="sessions_100",
        name="Veteran",
        description="Complete 100 sessions",
        icon="[!!]",
        category="general",
        target=100,
    ),
]
