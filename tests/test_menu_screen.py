"""Tests for menu screen production-shell helpers."""

from key4ce.themes.themes import DEFAULT_THEME
from key4ce.ui.screens.menu import ALL_CONTENT_KEYS, MenuScreen


def test_selected_category_label_for_builtin():
    screen = MenuScreen(DEFAULT_THEME)
    screen._cat_index = 0
    assert screen._selected_category_label()


def test_selected_category_description_for_focus_uses_hint():
    screen = MenuScreen(DEFAULT_THEME, focus_hint="weak: th, ng")
    screen._cat_index = ALL_CONTENT_KEYS.index("focus")
    assert screen._selected_category_description() == "weak: th, ng"


def test_render_returns_panel_object():
    screen = MenuScreen(DEFAULT_THEME)
    rendered = screen.render()
    assert rendered is not None
