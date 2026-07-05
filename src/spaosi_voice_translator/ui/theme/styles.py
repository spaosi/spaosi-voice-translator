from __future__ import annotations

from spaosi_voice_translator.ui.theme.colors import Colors


def panel_style(background: str = Colors.PANEL_3, border: str = Colors.BORDER, radius: int = 7) -> str:
    return f"""
        QFrame {{
            background-color: {background};
            border: 1px solid {border};
            border-radius: {radius}px;
        }}
    """


def transparent_widget_style() -> str:
    return "background: transparent; border: none;"


def input_style(selector: str) -> str:
    return f"""
        {selector} {{
            background-color: #111111;
            border: 1px solid {Colors.BORDER};
            border-radius: 5px;
            padding: 5px 9px;
            color: {Colors.TEXT};
            font-size: 12px;
            font-weight: 800;
        }}
        {selector}:hover {{
            border-color: {Colors.CYAN_DARK};
        }}
        {selector}:focus {{
            border-color: {Colors.CYAN};
        }}
    """
