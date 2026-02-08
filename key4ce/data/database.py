"""Database operations for Key4ce.

Uses SQLite with async operations via aiosqlite.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
import uuid

from key4ce.data.models import Session, UserStats, Achievement, DEFAULT_ACHIEVEMENTS


# Schema version for migrations
SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    source_type TEXT DEFAULT 'builtin',
    source_ref TEXT DEFAULT '',
    wpm_final REAL DEFAULT 0,
    accuracy REAL DEFAULT 0,
    total_chars INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0,
    max_combo INTEGER DEFAULT 0,
    keystrokes_json TEXT DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- User stats table (single row)
CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    total_sessions INTEGER DEFAULT 0,
    total_chars_typed INTEGER DEFAULT 0,
    total_time_seconds REAL DEFAULT 0,
    avg_wpm REAL DEFAULT 0,
    best_wpm REAL DEFAULT 0,
    avg_accuracy REAL DEFAULT 0,
    best_accuracy REAL DEFAULT 0,
    longest_combo INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Achievements table
CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT DEFAULT '*',
    category TEXT DEFAULT 'general',
    target INTEGER DEFAULT 1,
    progress INTEGER DEFAULT 0,
    unlocked_at TEXT
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_info (
    version INTEGER PRIMARY KEY
);

-- Index for session queries
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_wpm ON sessions(wpm_final);
"""


class Database:
    """SQLite database manager for Key4ce."""
    
    def __init__(self, db_path: Path) -> None:
        """Initialize the database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
    
    def connect(self) -> None:
        """Connect to the database and initialize schema."""
        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._connection = sqlite3.connect(str(self._db_path))
        self._connection.row_factory = sqlite3.Row
        
        # Initialize schema
        self._init_schema()
    
    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _init_schema(self) -> None:
        """Initialize or migrate the database schema."""
        if not self._connection:
            return
        
        cursor = self._connection.cursor()
        
        # Create tables
        cursor.executescript(SCHEMA_SQL)
        
        # Check schema version
        cursor.execute("SELECT version FROM schema_info LIMIT 1")
        row = cursor.fetchone()
        
        if row is None:
            # Fresh database
            cursor.execute("INSERT INTO schema_info (version) VALUES (?)", (SCHEMA_VERSION,))
            self._init_default_data()
        
        self._connection.commit()
    
    def _init_default_data(self) -> None:
        """Initialize default data (achievements, stats)."""
        if not self._connection:
            return
        
        cursor = self._connection.cursor()
        
        # Initialize user stats
        cursor.execute("""
            INSERT OR IGNORE INTO user_stats (id) VALUES (1)
        """)
        
        # Initialize achievements
        for achievement in DEFAULT_ACHIEVEMENTS:
            cursor.execute("""
                INSERT OR IGNORE INTO achievements (id, name, description, icon, category, target, progress)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                achievement.id,
                achievement.name,
                achievement.description,
                achievement.icon,
                achievement.category,
                achievement.target,
                0,
            ))
        
        self._connection.commit()
    
    # Session operations
    
    def save_session(self, session: Session) -> None:
        """Save a typing session to the database."""
        if not self._connection:
            return
        
        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (id, started_at, ended_at, source_type, source_ref, wpm_final, 
             accuracy, total_chars, total_errors, max_combo, keystrokes_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.id,
            session.started_at.isoformat(),
            session.ended_at.isoformat() if session.ended_at else None,
            session.source_type,
            session.source_ref,
            session.wpm_final,
            session.accuracy,
            session.total_chars,
            session.total_errors,
            session.max_combo,
            session.keystrokes_json,
            session.created_at.isoformat(),
        ))
        
        self._connection.commit()
        
        # Update user stats
        self._update_stats_after_session(session)
    
    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID."""
        if not self._connection:
            return None
        
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        
        if row:
            return Session.from_dict(dict(row))
        return None
    
    def get_recent_sessions(self, limit: int = 10) -> list[Session]:
        """Get the most recent sessions."""
        if not self._connection:
            return []
        
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM sessions 
            ORDER BY started_at DESC 
            LIMIT ?
        """, (limit,))
        
        return [Session.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_best_session(self) -> Session | None:
        """Get the session with the highest WPM."""
        if not self._connection:
            return None
        
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM sessions 
            ORDER BY wpm_final DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            return Session.from_dict(dict(row))
        return None
    
    # Stats operations
    
    def get_user_stats(self) -> UserStats:
        """Get the user's aggregated statistics."""
        if not self._connection:
            return UserStats()
        
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM user_stats WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return UserStats.from_dict(dict(row))
        return UserStats()
    
    def _update_stats_after_session(self, session: Session) -> None:
        """Update user stats after completing a session."""
        if not self._connection:
            return
        
        stats = self.get_user_stats()
        
        # Calculate new averages
        total = stats.total_sessions + 1
        
        # Running average for WPM
        stats.avg_wpm = (
            (stats.avg_wpm * stats.total_sessions + session.wpm_final) / total
        )
        
        # Running average for accuracy
        stats.avg_accuracy = (
            (stats.avg_accuracy * stats.total_sessions + session.accuracy) / total
        )
        
        # Update bests
        stats.best_wpm = max(stats.best_wpm, session.wpm_final)
        stats.best_accuracy = max(stats.best_accuracy, session.accuracy)
        stats.longest_combo = max(stats.longest_combo, session.max_combo)
        
        # Update totals
        stats.total_sessions = total
        stats.total_chars_typed += session.total_chars
        
        if session.started_at and session.ended_at:
            duration = (session.ended_at - session.started_at).total_seconds()
            stats.total_time_seconds += duration
        
        stats.updated_at = datetime.now()
        
        # Save updated stats
        cursor = self._connection.cursor()
        cursor.execute("""
            UPDATE user_stats SET
                total_sessions = ?,
                total_chars_typed = ?,
                total_time_seconds = ?,
                avg_wpm = ?,
                best_wpm = ?,
                avg_accuracy = ?,
                best_accuracy = ?,
                longest_combo = ?,
                updated_at = ?
            WHERE id = 1
        """, (
            stats.total_sessions,
            stats.total_chars_typed,
            stats.total_time_seconds,
            stats.avg_wpm,
            stats.best_wpm,
            stats.avg_accuracy,
            stats.best_accuracy,
            stats.longest_combo,
            stats.updated_at.isoformat(),
        ))
        
        self._connection.commit()
        
        # Check achievements
        self._check_achievements_after_session(session, stats)
    
    # Achievement operations
    
    def get_achievements(self) -> list[Achievement]:
        """Get all achievements."""
        if not self._connection:
            return []
        
        cursor = self._connection.cursor()
        cursor.execute("SELECT * FROM achievements ORDER BY category, id")
        
        return [Achievement.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def get_unlocked_achievements(self) -> list[Achievement]:
        """Get all unlocked achievements."""
        if not self._connection:
            return []
        
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT * FROM achievements 
            WHERE unlocked_at IS NOT NULL 
            ORDER BY unlocked_at DESC
        """)
        
        return [Achievement.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def unlock_achievement(self, achievement_id: str) -> Achievement | None:
        """Unlock an achievement and return it."""
        if not self._connection:
            return None
        
        now = datetime.now()
        
        cursor = self._connection.cursor()
        cursor.execute("""
            UPDATE achievements 
            SET unlocked_at = ?, progress = target
            WHERE id = ? AND unlocked_at IS NULL
        """, (now.isoformat(), achievement_id))
        
        self._connection.commit()
        
        # Return the updated achievement
        cursor.execute("SELECT * FROM achievements WHERE id = ?", (achievement_id,))
        row = cursor.fetchone()
        
        if row:
            return Achievement.from_dict(dict(row))
        return None
    
    def update_achievement_progress(self, achievement_id: str, progress: int) -> None:
        """Update an achievement's progress."""
        if not self._connection:
            return
        
        cursor = self._connection.cursor()
        cursor.execute("""
            UPDATE achievements 
            SET progress = ?
            WHERE id = ? AND unlocked_at IS NULL
        """, (progress, achievement_id))
        
        self._connection.commit()
    
    def _check_achievements_after_session(self, session: Session, stats: UserStats) -> list[Achievement]:
        """Check and unlock achievements after a session.
        
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        # First session
        if stats.total_sessions == 1:
            achievement = self.unlock_achievement("first_session")
            if achievement:
                newly_unlocked.append(achievement)
        
        # Speed achievements
        for speed_id, speed_target in [("speed_50", 50), ("speed_75", 75), ("speed_100", 100)]:
            if session.wpm_final >= speed_target:
                achievement = self.unlock_achievement(speed_id)
                if achievement:
                    newly_unlocked.append(achievement)
        
        # Accuracy achievements
        for acc_id, acc_target in [("accuracy_95", 95), ("accuracy_99", 99)]:
            if session.accuracy >= acc_target:
                achievement = self.unlock_achievement(acc_id)
                if achievement:
                    newly_unlocked.append(achievement)
        
        # Combo achievements
        for combo_id, combo_target in [("combo_25", 25), ("combo_50", 50), ("combo_100", 100)]:
            if session.max_combo >= combo_target:
                achievement = self.unlock_achievement(combo_id)
                if achievement:
                    newly_unlocked.append(achievement)
        
        # Session count achievements
        for session_id, session_target in [("sessions_10", 10), ("sessions_50", 50), ("sessions_100", 100)]:
            self.update_achievement_progress(session_id, stats.total_sessions)
            if stats.total_sessions >= session_target:
                achievement = self.unlock_achievement(session_id)
                if achievement:
                    newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())
