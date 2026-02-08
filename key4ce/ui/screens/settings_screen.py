"""Settings screen for Key4ce."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Static, Switch, RadioSet, RadioButton
from textual.binding import Binding

from key4ce.logging import get_logger, log_exception


class SettingRow(Horizontal):
    """A row containing a setting label and control."""
    
    DEFAULT_CSS = """
    SettingRow {
        width: 100%;
        height: auto;
        min-height: 3;
        padding: 0 1;
        margin: 1 0;
    }
    
    .setting-label {
        width: 50%;
        height: auto;
        color: #e0e0e0;
    }
    
    .setting-control {
        width: 50%;
        height: auto;
        align: right middle;
    }
    """


class SettingsScreen(Screen):
    """Settings configuration screen."""
    
    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("s", "save", "Save", show=True),
    ]
    
    CSS = """
    SettingsScreen {
        align: center middle;
        background: #0a0e27;
    }
    
    #settings-container {
        width: 70%;
        max-width: 70;
        height: 80%;
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
    
    .section-header {
        text-style: bold;
        color: #00d4ff;
        margin-top: 1;
        margin-bottom: 1;
    }
    
    #buttons {
        dock: bottom;
        height: 4;
        align: center middle;
        padding: 1;
    }
    
    .action-btn {
        margin: 0 1;
        min-width: 16;
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
    
    Switch {
        background: #0d1229;
    }
    
    Switch.-on {
        background: #00ff9f 30%;
    }
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._log = get_logger("settings")
    
    def compose(self) -> ComposeResult:
        """Create the settings layout."""
        self._log.debug("Composing settings screen")
        
        try:
            settings = self.app.config.settings
        except Exception as e:
            log_exception(e, "Error loading settings")
            settings = {}
        
        with Container(id="settings-container"):
            yield Static("SETTINGS", id="title")
            
            with ScrollableContainer():
                # Display settings
                yield Static("Display", classes="section-header")
                
                with SettingRow():
                    yield Static("Enable Animations", classes="setting-label")
                    yield Switch(
                        value=settings.get("display", {}).get("animations_enabled", True),
                        id="animations-toggle",
                    )
                
                with SettingRow():
                    yield Static("Background Effects", classes="setting-label")
                    yield Switch(
                        value=settings.get("display", {}).get("background_effects", True),
                        id="background-toggle",
                    )
                
                # Typing settings
                yield Static("Typing", classes="section-header")
                
                with SettingRow():
                    yield Static("Show Ghost Racer", classes="setting-label")
                    yield Switch(
                        value=settings.get("typing", {}).get("show_ghost_racer", True),
                        id="ghost-toggle",
                    )
                
                with SettingRow():
                    yield Static("Combo Meter", classes="setting-label")
                    yield Switch(
                        value=settings.get("typing", {}).get("combo_enabled", True),
                        id="combo-toggle",
                    )
                
                with SettingRow():
                    yield Static("Live WPM Display", classes="setting-label")
                    yield Switch(
                        value=settings.get("typing", {}).get("show_live_wpm", True),
                        id="wpm-toggle",
                    )
                
                # Current theme display
                yield Static("Theme", classes="section-header")
                current_theme = settings.get("display", {}).get("theme", "cyberpunk")
                yield Static(f"Current: {current_theme}", id="current-theme")
                yield Static("(Edit ~/.config/key4ce/settings.yaml to change)", classes="setting-label")
            
            with Horizontal(id="buttons"):
                yield Button("Save [S]", id="btn-save", classes="action-btn", variant="primary")
                yield Button("Cancel [ESC]", id="btn-cancel", classes="action-btn")
    
    def on_mount(self) -> None:
        """Focus save button on mount."""
        self._log.debug("Settings screen mounted")
        try:
            self.query_one("#btn-save").focus()
        except Exception:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-save":
            self.action_save()
        elif event.button.id == "btn-cancel":
            self.action_go_back()
    
    def action_save(self) -> None:
        """Save settings and return."""
        self._log.info("Saving settings")
        
        try:
            # Get values from controls
            animations_enabled = self.query_one("#animations-toggle", Switch).value
            background_effects = self.query_one("#background-toggle", Switch).value
            ghost_racer = self.query_one("#ghost-toggle", Switch).value
            combo_enabled = self.query_one("#combo-toggle", Switch).value
            show_wpm = self.query_one("#wpm-toggle", Switch).value
            
            self._log.debug(f"animations_enabled={animations_enabled}, background={background_effects}")
            
            # Update config
            self.app.config.update_setting("display", "animations_enabled", value=animations_enabled)
            self.app.config.update_setting("display", "background_effects", value=background_effects)
            self.app.config.update_setting("typing", "show_ghost_racer", value=ghost_racer)
            self.app.config.update_setting("typing", "combo_enabled", value=combo_enabled)
            self.app.config.update_setting("typing", "show_live_wpm", value=show_wpm)
            
            # Save to files
            self.app.config.save_all()
            
            self._log.info("Settings saved successfully")
            self.app.notify("Settings saved!")
        except Exception as e:
            log_exception(e, "Error saving settings")
            self.app.notify(f"Error saving: {e}", severity="error")
        
        self.app.pop_screen()
    
    def action_go_back(self) -> None:
        """Return without saving."""
        self._log.debug("Canceling settings changes")
        self.app.pop_screen()
