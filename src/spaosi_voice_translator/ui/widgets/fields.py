from __future__ import annotations

from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QComboBox,
    QLineEdit,
    QSizePolicy,
    QSpinBox,
)

from spaosi_voice_translator.ui.theme.colors import Colors


class CompactCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(34)
        self.setMaxVisibleItems(8)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f"""
            QComboBox {{
                background-color: #111111;
                border: 1px solid {Colors.BORDER};
                border-radius: 5px;
                padding: 5px 9px;
                color: {Colors.TEXT};
                font-size: 12px;
                font-weight: 800;
            }}
            QComboBox:hover {{
                border-color: {Colors.CYAN_DARK};
            }}
            QComboBox:focus {{
                border-color: {Colors.CYAN};
            }}
            QComboBox::drop-down {{
                background-color: #111111;
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: #111111;
                border: 1px solid {Colors.BORDER};
                border-radius: 4px;
                color: {Colors.TEXT};
                selection-background-color: {Colors.CYAN_DARK};
                selection-color: #FFFFFF;
                outline: 0;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 26px;
                padding: 4px 8px;
                background-color: #111111;
            }}
            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected {{
                background-color: {Colors.CYAN_DARK};
                color: #FFFFFF;
            }}
            """
        )

        self.view().setStyleSheet(
            f"""
            QListView {{
                background-color: #111111;
                border: 1px solid {Colors.BORDER};
                color: {Colors.TEXT};
                selection-background-color: {Colors.CYAN_DARK};
                selection-color: #FFFFFF;
                outline: 0;
            }}
            QListView::item {{
                min-height: 26px;
                padding: 4px 8px;
                background-color: #111111;
            }}
            QListView::item:hover,
            QListView::item:selected {{
                background-color: {Colors.CYAN_DARK};
                color: #FFFFFF;
            }}
            """
        )


class CompactLineEdit(QLineEdit):
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: #111111;
                border: 1px solid {Colors.BORDER};
                border-radius: 5px;
                padding: 5px 9px;
                color: {Colors.TEXT};
                font-size: 12px;
                font-weight: 700;
            }}
            QLineEdit:hover {{
                border-color: {Colors.CYAN_DARK};
            }}
            QLineEdit:focus {{
                border-color: {Colors.CYAN};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_DIM};
            }}
            """
        )


class CompactSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(100, 1200)
        self.setSingleStep(50)
        self.setValue(300)
        self.setSuffix(" ms")
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f"""
            QSpinBox {{
                background-color: #111111;
                border: 1px solid {Colors.BORDER};
                border-radius: 5px;
                padding: 5px 9px;
                color: {Colors.TEXT};
                font-size: 12px;
                font-weight: 800;
            }}
            QSpinBox:hover {{
                border-color: {Colors.CYAN_DARK};
            }}
            QSpinBox:focus {{
                border-color: {Colors.CYAN};
            }}
            """
        )
