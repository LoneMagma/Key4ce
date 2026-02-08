"""Results screen for Key4ce - post-session analysis."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.binding import Binding


class StatBox(Static):
    """A styled box for displaying a statistic."""
    
    DEFAULT_CSS = """
    StatBox {
        width: 20;
        height: 5;
        padding: 1;
        background: #0d1229;
        border: round #00ff9f;
        text-align: center;
        margin: 0 1;
    }
    """
    
    def __init__(self, label: str, value: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value
    
    def on_mount(self) -> None:
        from rich.text import Text
        text = Text()
        text.append(self._label + "\n", style="dim")
        text.append(self._value, style="bold cyan")
        self.update(text)


class ResultsScreen(Screen):
    """Screen showing typing session results."""
    
    BINDINGS = [
        Binding("r", "retry", "Retry", show=True),
        Binding("m", "menu", "Menu", show=True),
        Binding("escape", "menu", "Menu", show=False),
    ]
    
    CSS = """
    ResultsScreen {
        align: center middle;
        background: #0a0e27;
    }
    
    #results-container {
        width: 80%;
        max-width: 80;
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
    
    #stats-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-bottom: 2;
    }
    
    #analysis {
        width: 100%;
        padding: 1;
        background: #0d1229;
        margin-bottom: 2;
        color: #e0e0e0;
    }
    
    #recommendations {
        width: 100%;
        padding: 1;
        background: #0d1229;
        margin-bottom: 2;
        color: #e0e0e0;
    }
    
    #buttons {
        width: 100%;
        align: center middle;
    }
    
    .action-btn {
        margin: 0 1;
        background: #151b3d;
        border: solid #00ff9f;
    }
    
    .action-btn:hover {
        background: #1a2548;
    }
    
    .action-btn:focus {
        background: #1f2d54;
        border: double #00d4ff;
    }
    """
    
    def __init__(
        self,
        wpm: float,
        accuracy: float,
        session_id: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._wpm = wpm
        self._accuracy = accuracy
        self._session_id = session_id
    
    def compose(self) -> ComposeResult:
        """Create the results layout."""
        with Container(id="results-container"):
            yield Static("SESSION COMPLETE", id="title")
            
            with Horizontal(id="stats-row"):
                yield StatBox("WPM", f"{self._wpm:.1f}")
                yield StatBox("ACCURACY", f"{self._accuracy:.1f}%")
                yield StatBox("RATING", self._get_rating())
            
            yield Static(self._get_analysis_text(), id="analysis")
            yield Static(self._get_recommendations_text(), id="recommendations")
            
            with Horizontal(id="buttons"):
                yield Button("[R] Retry", id="btn-retry", classes="action-btn")
                yield Button("[M] Menu", id="btn-menu", classes="action-btn")
    
    def on_mount(self) -> None:
        """Focus retry button and show achievements."""
        try:
            self.query_one("#btn-retry").focus()
        except Exception:
            pass
        self._show_achievements()
    
    def _get_rating(self) -> str:
        """Get a rating based on WPM and accuracy."""
        score = (self._wpm * 0.6) + (self._accuracy * 0.4)
        
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _get_analysis_text(self) -> str:
        """Generate analysis text."""
        lines = ["ANALYSIS", "-" * 40]
        
        # WPM assessment
        if self._wpm >= 80:
            lines.append("Speed: Excellent! You're typing at an advanced level.")
        elif self._wpm >= 60:
            lines.append("Speed: Good pace. Keep practicing to reach 80+ WPM.")
        elif self._wpm >= 40:
            lines.append("Speed: Getting there! Focus on building muscle memory.")
        else:
            lines.append("Speed: Take your time. Accuracy is more important now.")
        
        # Accuracy assessment
        if self._accuracy >= 98:
            lines.append("Accuracy: Near perfect! Outstanding precision.")
        elif self._accuracy >= 95:
            lines.append("Accuracy: Great accuracy. Minor improvements possible.")
        elif self._accuracy >= 90:
            lines.append("Accuracy: Good, but try to slow down for fewer errors.")
        else:
            lines.append("Accuracy: Focus on accuracy over speed for now.")
        
        return "\n".join(lines)
    
    def _get_recommendations_text(self) -> str:
        """Generate recommendations text."""
        lines = ["RECOMMENDATIONS", "-" * 40]
        
        if self._accuracy < 95:
            lines.append("- Slow down slightly to improve accuracy")
        
        if self._wpm < 40:
            lines.append("- Practice home row keys for better muscle memory")
        elif self._wpm < 60:
            lines.append("- Try the Practice mode with common word patterns")
        else:
            lines.append("- Challenge yourself with harder text sources")
        
        lines.append("- Regular practice sessions work better than long ones")
        
        return "\n".join(lines)
    
    def _show_achievements(self) -> None:
        """Show any newly unlocked achievements."""
        if self._wpm >= 100:
            self.app.notify("Achievement Unlocked: Centurion (100 WPM)!")
        elif self._wpm >= 75:
            self.app.notify("Achievement Unlocked: Speed Runner (75 WPM)!")
        elif self._wpm >= 50:
            self.app.notify("Achievement Unlocked: Getting Warmed Up (50 WPM)!")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-retry":
            self.action_retry()
        elif event.button.id == "btn-menu":
            self.action_menu()
    
    def action_retry(self) -> None:
        """Retry with a new random text."""
        from key4ce.content.builtin import BuiltinContent
        import asyncio
        
        async def start_retry():
            self.app.pop_screen()  # Remove results screen
            content = BuiltinContent()
            text = await content.get_random()
            self.app.start_typing_session(text.text, text.source_type, text.id)
        
        asyncio.create_task(start_retry())
    
    def action_menu(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()
