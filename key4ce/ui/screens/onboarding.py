"""Onboarding screen for Key4ce - first-time user tutorial."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding


ONBOARDING_STEPS = [
    {
        "title": "Welcome to Key4ce",
        "content": """
Welcome to your new typing practice companion!

Key4ce is designed to help you:
  - Improve your typing speed
  - Increase your accuracy
  - Track your progress over time
  - Have fun while doing it

Press [ENTER] to continue...
""",
    },
    {
        "title": "How It Works",
        "content": """
The typing experience is simple:

  1. Text appears on screen
  2. Type what you see
  3. Watch your WPM and accuracy in real-time
  4. Get detailed analysis after each session

Correct characters fade out.
Errors are highlighted in red.
Build combos by typing correctly!

Press [ENTER] to continue...
""",
    },
    {
        "title": "Navigation",
        "content": """
Controls are intuitive:

  Arrow Keys    Navigate menus
  Enter         Select option
  Escape        Go back / Exit
  ?             Show help

During typing:
  Just type     The text you see
  Backspace     Correct mistakes
  Escape        Abort session

Press [ENTER] to continue...
""",
    },
    {
        "title": "Customization",
        "content": """
Make it yours through Settings:

  Themes        Choose your color palette
  Animations    Toggle effects on/off
  Cursor Style  Block, underline, or bar
  
All settings are saved in config files
that you can edit directly if you prefer.

Press [ENTER] to continue...
""",
    },
    {
        "title": "Ready to Start!",
        "content": """
That's all you need to know!

Tips for improvement:
  - Focus on accuracy first
  - Speed comes naturally with practice  
  - Short daily sessions beat long ones
  - Use the Practice mode for weak areas

Ready to test your skills?

Press [ENTER] to begin...
""",
    },
]


class OnboardingScreen(Screen):
    """First-time user tutorial screen."""
    
    BINDINGS = [
        Binding("enter", "next_step", "Continue", show=True),
        Binding("escape", "skip", "Skip", show=True),
        Binding("left", "prev_step", "Previous", show=False),
        Binding("right", "next_step", "Next", show=False),
    ]
    
    CSS = """
    OnboardingScreen {
        align: center middle;
        background: #0a0e27;
    }
    
    #onboarding-container {
        width: 70%;
        max-width: 60;
        height: auto;
        padding: 2;
        background: #151b3d;
        border: round #00ff9f;
    }
    
    #step-indicator {
        text-align: center;
        color: #6a6a8a;
        margin-bottom: 1;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        color: #00ff9f;
        margin-bottom: 1;
    }
    
    #content {
        width: 100%;
        height: auto;
        padding: 1;
        color: #e0e0e0;
    }
    
    #footer {
        text-align: center;
        color: #6a6a8a;
        margin-top: 1;
    }
    
    #progress-dots {
        text-align: center;
        margin-top: 1;
        color: #00ff9f;
    }
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_step = 0
    
    def compose(self) -> ComposeResult:
        """Create the onboarding layout."""
        step = ONBOARDING_STEPS[0]
        
        with Container(id="onboarding-container"):
            yield Static(self._get_step_indicator(), id="step-indicator")
            yield Static(step["title"], id="title")
            yield Static(step["content"], id="content")
            yield Static(self._get_progress_dots(), id="progress-dots")
            yield Static("[ENTER] Continue  [ESC] Skip", id="footer")
    
    def _get_step_indicator(self) -> str:
        """Get the step indicator text."""
        return f"Step {self._current_step + 1} of {len(ONBOARDING_STEPS)}"
    
    def _get_progress_dots(self) -> str:
        """Get the progress dots visualization."""
        dots = []
        for i in range(len(ONBOARDING_STEPS)):
            if i < self._current_step:
                dots.append("[x]")
            elif i == self._current_step:
                dots.append("[>]")
            else:
                dots.append("[ ]")
        return " ".join(dots)
    
    def _update_display(self) -> None:
        """Update the display for current step."""
        if self._current_step >= len(ONBOARDING_STEPS):
            return
        
        data = ONBOARDING_STEPS[self._current_step]
        
        try:
            self.query_one("#step-indicator", Static).update(self._get_step_indicator())
            self.query_one("#title", Static).update(data["title"])
            self.query_one("#content", Static).update(data["content"])
            self.query_one("#progress-dots", Static).update(self._get_progress_dots())
        except Exception:
            pass
    
    def action_next_step(self) -> None:
        """Go to the next step or complete onboarding."""
        if self._current_step >= len(ONBOARDING_STEPS) - 1:
            self._complete_onboarding()
        else:
            self._current_step += 1
            self._update_display()
    
    def action_prev_step(self) -> None:
        """Go to the previous step."""
        if self._current_step > 0:
            self._current_step -= 1
            self._update_display()
    
    def action_skip(self) -> None:
        """Skip the onboarding."""
        self._complete_onboarding()
    
    def _complete_onboarding(self) -> None:
        """Mark onboarding as complete and close."""
        # Update config
        self.app.config.update_setting("onboarding", "completed", value=True)
        self.app.config.save_settings()
        
        self.app.notify("Welcome to Key4ce!")
        self.app.pop_screen()
        
        # Push main menu
        from key4ce.ui.screens.main_menu import MainMenuScreen
        self.app.push_screen(MainMenuScreen())
