"""Main Textual application for Key4ce."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from key4ce import __version__, __app_name__
from key4ce.config import get_config
from key4ce.data import Database
from key4ce.logging import setup_logging, get_logger, log_exception


class Key4ceApp(App):
    """The Key4ce terminal typing game application."""
    
    TITLE = __app_name__
    SUB_TITLE = f"v{__version__}"
    
    CSS = """
    Screen {
        background: #0a0e27;
    }
    
    Header {
        background: #151b3d;
        color: #00ff9f;
    }
    
    Footer {
        background: #151b3d;
        color: #6a6a8a;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: #00ff9f;
        margin-bottom: 1;
    }
    
    .subtitle {
        text-align: center;
        color: #6a6a8a;
        margin-bottom: 2;
    }
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("?", "show_help", "Help", show=True),
        Binding("ctrl+r", "reload_config", "Reload Config", show=False),
    ]
    
    def __init__(self) -> None:
        super().__init__()
        
        # Set up logging first
        setup_logging()
        self._log = get_logger("app")
        self._log.info("Initializing Key4ce application")
        
        try:
            # Initialize configuration
            self._config = get_config()
            self._config.create_default_configs()
            self._log.info("Configuration loaded")
            
            # Initialize database
            self._db = Database(self._config.database_path)
            self._log.info(f"Database initialized at {self._config.database_path}")
        except Exception as e:
            log_exception(e, "Failed to initialize application")
            raise
    
    @property
    def config(self):
        """Get the configuration manager."""
        return self._config
    
    @property
    def database(self) -> Database:
        """Get the database instance."""
        return self._db
    
    def compose(self) -> ComposeResult:
        """Create child widgets - App level only, screens added via push_screen."""
        self._log.debug("Composing app widgets")
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle application mount."""
        self._log.info("Application mounted")
        
        try:
            # Connect database
            self._db.connect()
            self._log.info("Database connected")
            
            # Check if onboarding needed
            onboarding_done = self._config.settings.get("onboarding", {}).get("completed", False)
            self._log.debug(f"Onboarding completed: {onboarding_done}")
            
            if not onboarding_done:
                # Show onboarding first
                self._log.info("Showing onboarding screen")
                from key4ce.ui.screens.onboarding import OnboardingScreen
                self.push_screen(OnboardingScreen())
            else:
                # Go to main menu
                self._log.info("Showing main menu")
                from key4ce.ui.screens.main_menu import MainMenuScreen
                self.push_screen(MainMenuScreen())
        except Exception as e:
            log_exception(e, "Error in on_mount")
            self.notify(f"Error: {e}", severity="error")
    
    def on_unmount(self) -> None:
        """Handle application unmount."""
        self._log.info("Application unmounting")
        try:
            self._db.close()
            self._log.info("Database closed")
        except Exception as e:
            log_exception(e, "Error closing database")
    
    def action_go_back(self) -> None:
        """Go back to previous screen or menu."""
        if len(self.screen_stack) > 1:
            self._log.debug("Going back to previous screen")
            self.pop_screen()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.notify("Help: Arrow keys to navigate, Enter to select, Escape to go back")
    
    def action_reload_config(self) -> None:
        """Reload configuration files."""
        try:
            self._config.reload()
            self._log.info("Configuration reloaded")
            self.notify("Configuration reloaded")
        except Exception as e:
            log_exception(e, "Error reloading config")
            self.notify(f"Error: {e}", severity="error")
    
    def start_typing_session(self, text: str, source_type: str = "builtin", source_ref: str = "") -> None:
        """Start a new typing session.
        
        Args:
            text: The text to type
            source_type: Content source type
            source_ref: Reference to the source
        """
        self._log.info(f"Starting typing session: source={source_type}, ref={source_ref}")
        try:
            from key4ce.ui.screens.typing_screen import TypingScreen
            self.push_screen(TypingScreen(text, source_type, source_ref))
        except Exception as e:
            log_exception(e, "Error starting typing session")
            self.notify(f"Error: {e}", severity="error")
    
    def show_results(
        self,
        wpm: float,
        accuracy: float,
        session_id: str,
    ) -> None:
        """Show results screen after a session.
        
        Args:
            wpm: Final WPM
            accuracy: Final accuracy percentage
            session_id: ID of the completed session
        """
        self._log.info(f"Showing results: WPM={wpm:.1f}, Accuracy={accuracy:.1f}%")
        try:
            from key4ce.ui.screens.results_screen import ResultsScreen
            self.push_screen(ResultsScreen(wpm, accuracy, session_id))
        except Exception as e:
            log_exception(e, "Error showing results")
            self.notify(f"Error: {e}", severity="error")
