from spaosi_voice_translator.ui.theme.colors import Colors


def build_app_stylesheet() -> str:
    return f"""
    QWidget {{
        font-family: "Segoe UI";
        color: {Colors.TEXT};
        background-color: transparent;
        font-size: 13px;
    }}

    QMainWindow {{
        background-color: {Colors.APP_BG};
    }}

    QTextEdit {{
        background-color: {Colors.PANEL_3};
        border: 1px solid {Colors.BORDER};
        color: {Colors.TEXT};
        padding: 10px;
        font-size: 13px;
        selection-background-color: {Colors.CYAN_DARK};
        selection-color: #FFFFFF;
    }}

    QProgressBar {{
        border: 1px solid {Colors.BORDER};
        background-color: {Colors.PANEL_3};
        border-radius: 2px;
    }}

    QProgressBar::chunk {{
        background-color: {Colors.GREEN};
        margin: 1px;
    }}
    """
