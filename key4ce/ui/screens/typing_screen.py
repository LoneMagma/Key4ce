"""Typing screen for Key4ce - the main gameplay area."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static, ProgressBar
from textual.binding import Binding
from textual import events

from key4ce.core.engine import TypingEngine, KeystrokeResult
from key4ce.data.models import Session
from key4ce.logging import get_logger, log_exception


class TypingDisplay(Static):
    """Widget to display the typing text with highlighting."""
    
    DEFAULT_CSS = """
    TypingDisplay {
        width: 100%;
        height: auto;
        min-height: 5;
        padding: 1 2;
        background: #0d1229;
    }
    """
    
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._text = text
        self._position = 0
        self._errors: set[int] = set()
    
    def update_state(self, position: int, error_positions: set[int]) -> None:
        """Update the display with current typing state.
        
        Args:
            position: Current cursor position
            error_positions: Set of positions with errors
        """
        self._position = position
        self._errors = error_positions
        self._render_text()
    
    def set_position(self, pos: int) -> None:
        """Update the current position (legacy)."""
        self._position = pos
        self._render_text()
    
    def mark_error(self, pos: int) -> None:
        """Mark a position as having an error."""
        self._errors.add(pos)
        self._render_text()
    
    def _render_text(self) -> None:
        """Render the text with appropriate styling."""
        from rich.text import Text
        
        text = Text()
        
        for i, char in enumerate(self._text):
            if i < self._position:
                # Already typed
                if i in self._errors:
                    # Error - show in red with strikethrough
                    text.append(char, style="bold red")
                else:
                    # Correct - dim green
                    text.append(char, style="dim green")
            elif i == self._position:
                # Current character - bright cursor
                text.append(char, style="bold reverse cyan")
            else:
                # Upcoming - dim white
                text.append(char, style="dim white")
        
        self.update(text)
    
    def on_mount(self) -> None:
        """Initial render."""
        self._render_text()


class StatsDisplay(Static):
    """Widget to display live typing statistics."""
    
    DEFAULT_CSS = """
    StatsDisplay {
        width: 100%;
        height: 3;
        padding: 0 2;
        text-align: center;
    }
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._wpm = 0.0
        self._accuracy = 100.0
        self._combo = 0
    
    def set_stats(self, wpm: float, accuracy: float, combo: int) -> None:
        """Update all stats at once."""
        self._wpm = wpm
        self._accuracy = accuracy
        self._combo = combo
        self._update_display()
    
    def set_combo(self, combo: int) -> None:
        """Update combo only."""
        self._combo = combo
        self._update_display()
    
    def _update_display(self) -> None:
        """Render the stats display."""
        from rich.text import Text
        
        text = Text()
        text.append(f"{self._wpm:.0f}", style="bold cyan")
        text.append(" wpm  |  ", style="dim")
        
        # Color accuracy based on value
        if self._accuracy >= 95:
            acc_style = "bold green"
        elif self._accuracy >= 90:
            acc_style = "bold yellow"
        else:
            acc_style = "bold red"
        
        text.append(f"{self._accuracy:.1f}%", style=acc_style)
        text.append("  |  ", style="dim")
        
        # Combo display
        if self._combo >= 50:
            combo_text = f"x{self._combo} [!!]"
            combo_style = "bold magenta"
        elif self._combo >= 25:
            combo_text = f"x{self._combo} [!]"
            combo_style = "bold yellow"
        elif self._combo >= 10:
            combo_text = f"x{self._combo}"
            combo_style = "bold cyan"
        else:
            combo_text = f"x{self._combo}"
            combo_style = "dim"
        
        text.append(combo_text, style=combo_style)
        
        self.update(text)
    
    def on_mount(self) -> None:
        self._update_display()


class TypingScreen(Screen):
    """Main typing gameplay screen."""
    
    BINDINGS = [
        Binding("escape", "abort", "Abort", show=True),
    ]
    
    CSS = """
    TypingScreen {
        align: center middle;
        background: #0a0e27;
    }
    
    #typing-container {
        width: 80%;
        max-width: 100;
        height: auto;
        padding: 2;
        background: #151b3d;
        border: round #00ff9f;
    }
    
    #header {
        text-align: center;
        color: #00ff9f;
        margin-bottom: 1;
    }
    
    #progress {
        width: 100%;
        margin: 1 0;
    }
    
    #footer-hint {
        text-align: center;
        color: #6a6a8a;
        margin-top: 1;
    }
    """
    
    def __init__(
        self,
        text: str,
        source_type: str = "builtin",
        source_ref: str = "",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._text = text
        self._source_type = source_type
        self._source_ref = source_ref
        self._engine: TypingEngine | None = None
        self._session_id: str = ""
        self._start_time: datetime | None = None
        self._timer_handle = None
        self._log = get_logger("typing")
    
    def compose(self) -> ComposeResult:
        """Create the typing screen layout."""
        self._log.debug("Composing typing screen")
        with Container(id="typing-container"):
            yield Static("Type the text below:", id="header")
            yield TypingDisplay(self._text, id="typing-display")
            yield ProgressBar(total=100, id="progress", show_eta=False)
            yield StatsDisplay(id="stats")
            yield Static("[ESC] to abort  |  Backspace to correct", id="footer-hint")
    
    def on_mount(self) -> None:
        """Set focus for keyboard input."""
        self._log.info("Typing screen mounted")
        
        try:
            # Create engine after mount when app is available
            self._engine = TypingEngine(
                self._text,
                on_keystroke=self._on_keystroke,
                on_combo_break=self._on_combo_break,
                on_milestone=self._on_milestone,
            )
            self._session_id = self.app.database.generate_session_id()
            self._log.debug(f"Session ID: {self._session_id}")
            
            self.can_focus = True
            self.focus()
            self._start_time = datetime.now()
            
            # Start update timer - every 500ms
            self._timer_handle = self.set_interval(0.5, self._update_stats)
        except Exception as e:
            log_exception(e, "Error in typing screen mount")
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard input."""
        if self._engine is None:
            return
            
        # Ignore modifier keys
        if event.key in ("shift", "ctrl", "alt", "meta", "caps_lock"):
            return
        
        # Handle escape
        if event.key == "escape":
            return
        
        try:
            # Handle backspace
            if event.key == "backspace":
                self._engine.process_key("\b")
                self._update_display()
                return
            
            # Process regular character
            char = event.character
            if char:
                result = self._engine.process_key(char)
                self._update_display()
                
                # Check if complete
                if result == KeystrokeResult.TEXT_COMPLETE:
                    self._log.info("Text complete!")
                    self._complete_session()
        except Exception as e:
            log_exception(e, "Error processing key")
    
    def _on_keystroke(self, keystroke) -> None:
        """Handle keystroke callback."""
        # Display updates are done in _update_display, no need here
        pass
    
    def _on_combo_break(self, combo: int) -> None:
        """Handle combo break."""
        if combo >= 10:
            self._log.debug(f"Combo broken at {combo}")
            self.app.notify(f"Combo broken at x{combo}!", severity="warning")
    
    def _on_milestone(self, milestone_type: str, value: int) -> None:
        """Handle milestone achievement."""
        if milestone_type == "combo":
            self._log.info(f"Combo milestone: {value}")
            self.app.notify(f"Combo x{value}!", severity="information")
    
    def _update_display(self) -> None:
        """Update the display widgets."""
        if self._engine is None:
            return
            
        state = self._engine.state
        
        try:
            # Update text display with error positions
            display = self.query_one("#typing-display", TypingDisplay)
            display.update_state(state.position, state.error_positions)
            
            progress = self.query_one("#progress", ProgressBar)
            progress.progress = state.progress
            
            stats = self.query_one("#stats", StatsDisplay)
            stats.set_combo(state.combo)
        except Exception as e:
            self._log.warning(f"Error updating display: {e}")
    
    def _update_stats(self) -> None:
        """Periodic stats update."""
        if self._engine is None or not self._engine.is_started:
            return
        
        state = self._engine.state
        try:
            stats = self.query_one("#stats", StatsDisplay)
            stats.set_stats(state.wpm, state.accuracy, state.combo)
        except Exception:
            pass
    
    def _complete_session(self) -> None:
        """Complete the typing session and save results."""
        if self._engine is None:
            return
            
        state = self._engine.state
        end_time = datetime.now()
        
        self._log.info(f"Session complete: WPM={state.wpm:.1f}, Accuracy={state.accuracy:.1f}%")
        
        # Cancel the timer
        if self._timer_handle:
            self._timer_handle.stop()
        
        try:
            # Create session record
            session = Session(
                id=self._session_id,
                started_at=self._start_time,
                ended_at=end_time,
                source_type=self._source_type,
                source_ref=self._source_ref,
                wpm_final=state.wpm,
                accuracy=state.accuracy,
                total_chars=state.correct + state.errors,
                total_errors=state.errors,
                max_combo=state.max_combo,
            )
            
            # Save to database
            self.app.database.save_session(session)
            self._log.info("Session saved to database")
            
            # Show results
            self.app.pop_screen()
            self.app.show_results(state.wpm, state.accuracy, self._session_id)
        except Exception as e:
            log_exception(e, "Error completing session")
            self.app.notify(f"Error: {e}", severity="error")
            self.app.pop_screen()
    
    def action_abort(self) -> None:
        """Abort the current session."""
        self._log.info("Session aborted")
        if self._timer_handle:
            self._timer_handle.stop()
        self.app.pop_screen()
