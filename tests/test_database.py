"""Tests for the database layer."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from key4ce.data.database import Database
from key4ce.data.models import Session, UserStats, Achievement


class TestDatabase:
    """Tests for Database operations."""
    
    @pytest.fixture
    def db(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            database = Database(db_path)
            database.connect()
            yield database
            database.close()
    
    def test_connect_creates_schema(self, db):
        """Test that connecting creates the schema."""
        # If we got here, schema was created successfully
        assert db._connection is not None
    
    def test_save_and_get_session(self, db):
        """Test saving and retrieving a session."""
        session = Session(
            id="test-123",
            started_at=datetime.now(),
            ended_at=datetime.now(),
            source_type="builtin",
            source_ref="test",
            wpm_final=75.5,
            accuracy=95.2,
            total_chars=100,
            total_errors=5,
            max_combo=25,
        )
        
        db.save_session(session)
        
        retrieved = db.get_session("test-123")
        
        assert retrieved is not None
        assert retrieved.id == "test-123"
        assert retrieved.wpm_final == 75.5
        assert retrieved.accuracy == 95.2
    
    def test_get_recent_sessions(self, db):
        """Test retrieving recent sessions in order."""
        now = datetime.now()
        
        for i in range(5):
            session = Session(
                id=f"session-{i}",
                started_at=now,
                wpm_final=50 + i * 10,
            )
            db.save_session(session)
        
        recent = db.get_recent_sessions(3)
        
        assert len(recent) == 3
    
    def test_user_stats_update(self, db):
        """Test that user stats are updated after session."""
        session = Session(
            id="stats-test",
            started_at=datetime.now(),
            ended_at=datetime.now(),
            wpm_final=80.0,
            accuracy=96.0,
            total_chars=50,
            max_combo=20,
        )
        
        db.save_session(session)
        
        stats = db.get_user_stats()
        
        assert stats.total_sessions == 1
        assert stats.best_wpm == 80.0
        assert stats.total_chars_typed == 50
    
    def test_achievement_unlock(self, db):
        """Test unlocking an achievement."""
        # The test database should have default achievements
        achievement = db.unlock_achievement("first_session")
        
        assert achievement is not None
        assert achievement.is_unlocked
    
    def test_get_unlocked_achievements(self, db):
        """Test retrieving unlocked achievements."""
        db.unlock_achievement("first_session")
        db.unlock_achievement("speed_50")
        
        unlocked = db.get_unlocked_achievements()
        
        assert len(unlocked) >= 2


class TestSessionModel:
    """Tests for Session model."""
    
    def test_to_dict(self):
        """Test session serialization."""
        session = Session(
            id="test",
            started_at=datetime(2026, 1, 1, 12, 0),
            wpm_final=75.0,
        )
        
        data = session.to_dict()
        
        assert data["id"] == "test"
        assert data["wpm_final"] == 75.0
        assert "2026-01-01" in data["started_at"]
    
    def test_from_dict(self):
        """Test session deserialization."""
        data = {
            "id": "test",
            "started_at": "2026-01-01T12:00:00",
            "ended_at": None,
            "source_type": "builtin",
            "source_ref": "",
            "wpm_final": 75.0,
            "accuracy": 95.0,
            "total_chars": 100,
            "total_errors": 5,
            "max_combo": 20,
            "keystrokes_json": "[]",
            "created_at": "2026-01-01T12:00:00",
        }
        
        session = Session.from_dict(data)
        
        assert session.id == "test"
        assert session.wpm_final == 75.0


class TestAchievementModel:
    """Tests for Achievement model."""
    
    def test_progress_percent(self):
        """Test progress percentage calculation."""
        achievement = Achievement(
            id="test",
            name="Test",
            description="Test achievement",
            target=100,
            progress=25,
        )
        
        assert achievement.progress_percent == 25.0
    
    def test_is_unlocked(self):
        """Test unlock status."""
        achievement = Achievement(
            id="test",
            name="Test",
            description="Test",
        )
        
        assert not achievement.is_unlocked
        
        achievement.unlocked_at = datetime.now()
        assert achievement.is_unlocked
