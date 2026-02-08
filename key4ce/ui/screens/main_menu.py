"""Main menu screen for Key4ce."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.binding import Binding

from key4ce.logging import get_logger, log_exception


# ASCII art title
TITLE_ART = """
 _  __          _  _           
| |/ /___ _   _| || |  ___ ___ 
| ' // _ \\ | | | || |_/ __/ _ \\
| . \\  __/ |_| |__   _| (_|  __/
|_|\\_\\___|\\__, |  |_|  \\___\\___|
          |___/                 
"""


class MenuButton(Button):
    """Custom styled menu button."""
    
    DEFAULT_CSS = """
    MenuButton {
        width: 100%;
        min-width: 30;
        height: 3;
        margin: 1 0;
        background: #151b3d;
        border: solid #00ff9f;
        text-align: center;
    }
    
    MenuButton:hover {
        background: #1a2548;
        border: solid #00d4ff;
    }
    
    MenuButton:focus {
        background: #1f2d54;
        border: double #00d4ff;
    }
    """


class MainMenuScreen(Screen):
    """Main menu screen with navigation options."""
    
    BINDINGS = [
        Binding("up", "focus_previous", "Up", show=False),
        Binding("down", "focus_next", "Down", show=False),
        Binding("enter", "select_option", "Select", show=False),
        Binding("1", "quick_start", "Quick Start", show=False),
        Binding("2", "practice", "Practice", show=False),
        Binding("3", "stats", "Stats", show=False),
        Binding("4", "settings", "Settings", show=False),
        Binding("q", "quit_app", "Quit", show=False),
    ]
    
    CSS = """
    MainMenuScreen {
        align: center middle;
        background: #0a0e27;
    }
    
    #menu-container {
        width: auto;
        height: auto;
        padding: 2 4;
        background: #151b3d;
        border: round #00ff9f;
    }
    
    #title-art {
        text-align: center;
        color: #00ff9f;
        margin-bottom: 1;
    }
    
    #subtitle {
        text-align: center;
        color: #6a6a8a;
        margin-bottom: 2;
    }
    
    #menu-buttons {
        width: 40;
        height: auto;
        align: center middle;
    }
    
    #footer {
        text-align: center;
        color: #6a6a8a;
        margin-top: 2;
    }
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._log = get_logger("menu")
    
    def compose(self) -> ComposeResult:
        """Create the menu layout."""
        self._log.debug("Composing main menu")
        with Container(id="menu-container"):
            yield Static(TITLE_ART, id="title-art")
            yield Static("Terminal Typing Game", id="subtitle")
            
            with Vertical(id="menu-buttons"):
                yield MenuButton("[1] Quick Start", id="btn-quick-start")
                yield MenuButton("[2] Practice", id="btn-practice")
                yield MenuButton("[3] Statistics", id="btn-stats")
                yield MenuButton("[4] Settings", id="btn-settings")
            
            yield Static("[Q] Quit  [?] Help", id="footer")
    
    def on_mount(self) -> None:
        """Focus the first button on mount."""
        self._log.debug("Main menu mounted")
        try:
            self.query_one("#btn-quick-start").focus()
        except Exception as e:
            self._log.warning(f"Could not focus button: {e}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        self._log.debug(f"Button pressed: {button_id}")
        
        if button_id == "btn-quick-start":
            self.action_quick_start()
        elif button_id == "btn-practice":
            self.action_practice()
        elif button_id == "btn-stats":
            self.action_stats()
        elif button_id == "btn-settings":
            self.action_settings()
    
    def action_quick_start(self) -> None:
        """Start a quick typing session with random text."""
        self._log.info("Quick start selected")
        from key4ce.content.builtin import BuiltinContent
        import asyncio
        
        async def start_quick():
            try:
                content = BuiltinContent()
                text = await content.get_random()
                self._log.debug(f"Got random text: {text.id}")
                self.app.start_typing_session(text.text, text.source_type, text.id)
            except Exception as e:
                log_exception(e, "Error starting quick session")
                self.app.notify(f"Error: {e}", severity="error")
        
        asyncio.create_task(start_quick())
    
    def action_practice(self) -> None:
        """Open practice mode selection."""
        self._log.info("Practice selected")
        from key4ce.ui.screens.practice_select import PracticeSelectScreen
        self.app.push_screen(PracticeSelectScreen())
    
    def action_stats(self) -> None:
        """Open statistics screen."""
        self._log.info("Stats selected")
        try:
            stats = self.app.database.get_user_stats()
            self.app.notify(
                f"Sessions: {stats.total_sessions} | "
                f"Best WPM: {stats.best_wpm:.1f} | "
                f"Avg Accuracy: {stats.avg_accuracy:.1f}%"
            )
        except Exception as e:
            log_exception(e, "Error getting stats")
            self.app.notify(f"Error: {e}", severity="error")
    
    def action_settings(self) -> None:
        """Open settings screen."""
        self._log.info("Settings selected")
        from key4ce.ui.screens.settings_screen import SettingsScreen
        self.app.push_screen(SettingsScreen())
    
    def action_quit_app(self) -> None:
        """Quit the application."""
        self._log.info("Quit selected")
        self.app.exit()
    
    def action_focus_next(self) -> None:
        """Focus next menu item."""
        self.focus_next()
    
    def action_focus_previous(self) -> None:
        """Focus previous menu item."""
        self.focus_previous()
    
    def action_select_option(self) -> None:
        """Select the currently focused option."""
        focused = self.focused
        if isinstance(focused, Button):
            focused.press()
