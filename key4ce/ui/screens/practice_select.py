"""Practice mode selection screen for Key4ce."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Grid
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.binding import Binding
import asyncio

from key4ce.content.builtin import BuiltinContent


class PracticeCard(Button):
    """A card-style button for practice options."""
    
    DEFAULT_CSS = """
    PracticeCard {
        width: 25;
        height: 7;
        padding: 1;
        background: #0d1229;
        border: solid #00ff9f;
        text-align: center;
    }
    
    PracticeCard:hover {
        background: #1a2548;
    }
    
    PracticeCard:focus {
        background: #1f2d54;
        border: double #00d4ff;
    }
    """
    
    def __init__(self, title: str, description: str, difficulty: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._description = description
        self._difficulty = difficulty
        self.label = f"{title}\n\n{description}"


class PracticeSelectScreen(Screen):
    """Screen for selecting practice mode options."""
    
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("1", "easy", "Easy", show=False),
        Binding("2", "medium", "Medium", show=False),
        Binding("3", "hard", "Hard", show=False),
    ]
    
    CSS = """
    PracticeSelectScreen {
        align: center middle;
        background: #0a0e27;
    }
    
    #practice-container {
        width: 80%;
        max-width: 90;
        height: auto;
        padding: 2;
        background: #151b3d;
        border: round #00ff9f;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: #00ff9f;
        margin-bottom: 2;
    }
    
    #cards {
        grid-size: 3;
        grid-gutter: 2;
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 2;
    }
    
    #footer {
        text-align: center;
        color: #6a6a8a;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Create the practice selection layout."""
        with Container(id="practice-container"):
            yield Static("SELECT DIFFICULTY", id="title")
            
            with Grid(id="cards"):
                yield PracticeCard(
                    "[1] Easy",
                    "Simple words\nShort sentences",
                    "easy",
                    id="card-easy",
                )
                yield PracticeCard(
                    "[2] Medium",
                    "Varied vocab\nLonger text",
                    "medium",
                    id="card-medium",
                )
                yield PracticeCard(
                    "[3] Hard",
                    "Code & symbols\nComplex text",
                    "hard",
                    id="card-hard",
                )
            
            yield Static("[ESC] Back to Menu", id="footer")
    
    def on_mount(self) -> None:
        """Focus the first card."""
        try:
            self.query_one("#card-easy").focus()
        except Exception:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle card selection."""
        card = event.button
        if isinstance(card, PracticeCard):
            self._start_practice(card._difficulty)
    
    def _start_practice(self, difficulty: str) -> None:
        """Start a practice session with the selected difficulty."""
        async def start():
            content = BuiltinContent()
            text = await content.get_random_by_difficulty(difficulty)
            self.app.pop_screen()
            self.app.start_typing_session(text.text, text.source_type, text.id)
        
        asyncio.create_task(start())
    
    def action_easy(self) -> None:
        """Select easy difficulty."""
        self._start_practice("easy")
    
    def action_medium(self) -> None:
        """Select medium difficulty."""
        self._start_practice("medium")
    
    def action_hard(self) -> None:
        """Select hard difficulty."""
        self._start_practice("hard")
    
    def action_go_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()
