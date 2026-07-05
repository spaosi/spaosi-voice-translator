from __future__ import annotations

import html
from dataclasses import dataclass

from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from spaosi_voice_translator.ui.theme.colors import Colors


@dataclass(frozen=True)
class LogRecord:
    line: str
    category: str
    color: str


class _LogTextArea(QTextEdit):
    def contextMenuEvent(self, event) -> None:
        menu = self.createStandardContextMenu()
        menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: #111111;
                color: {Colors.TEXT};
                border: 1px solid {Colors.BORDER};
                padding: 4px;
                font-size: 12px;
            }}
            QMenu::item {{
                background-color: transparent;
                color: {Colors.TEXT};
                padding: 6px 22px 6px 18px;
                min-width: 110px;
            }}
            QMenu::item:selected {{
                background-color: {Colors.CYAN_DARK};
                color: #FFFFFF;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {Colors.BORDER_DARK};
                margin: 4px 6px;
            }}
            """
        )
        menu.exec(event.globalPos())


class LogTextEdit(QWidget):
    ERROR_WORDS = (
        "ошибка",
        "не удалось",
        "не хватает",
        "пуст",
        "потерян",
        "не прош",
        "закрыто",
        "failed",
        "error",
        "empty",
    )

    SUCCESS_WORDS = (
        "готов",
        "создан",
        "загружен",
        "запущ",
        "установлено",
        "подключение установлено",
        "канал готов",
        "интерфейс загружен",
        "приложение готово",
        "захват системного звука",
    )

    INCOMING_WORDS = (
        "внешние голоса:",
        "входящий текст:",
        "распознано:",
        "микрофон:",
    )

    TRANSLATION_WORDS = (
        "перевод:",
        "перевод внешних голосов:",
        "перевод микрофона:",
    )

    MAX_RECORDS = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records: list[LogRecord] = []
        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.text = _LogTextArea()
        self.text.setReadOnly(True)
        self.text.document().setMaximumBlockCount(self.MAX_RECORDS)
        self.text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {Colors.PANEL_3};
                border: 1px solid {Colors.BORDER};
                border-bottom: none;
                border-top-left-radius: 7px;
                border-top-right-radius: 7px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                color: {Colors.TEXT_MUTED};
                padding: 10px;
                font-size: 13px;
                selection-background-color: {Colors.CYAN_DARK};
                selection-color: #FFFFFF;
            }}
            """
        )

        self.filter_bar = QFrame()
        self.filter_bar.setFixedHeight(38)
        self.filter_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.PANEL_3};
                border: 1px solid {Colors.BORDER};
                border-top: none;
                border-bottom-left-radius: 7px;
                border-bottom-right-radius: 7px;
            }}
            """
        )

        filter_layout = QHBoxLayout(self.filter_bar)
        filter_layout.setContentsMargins(10, 0, 10, 0)
        filter_layout.setSpacing(12)

        self.chk_incoming = self._make_checkbox("Входящий текст")
        self.chk_translation = self._make_checkbox("Перевод")
        self.chk_system = self._make_checkbox("Системные логи")
        self.chk_errors = self._make_checkbox("Ошибки")

        filter_layout.addWidget(self.chk_incoming)
        filter_layout.addWidget(self.chk_translation)
        filter_layout.addWidget(self.chk_system)
        filter_layout.addWidget(self.chk_errors)
        filter_layout.addStretch(1)

        root.addWidget(self.text, 1)
        root.addWidget(self.filter_bar)

    def apply_translations(
        self,
        *,
        incoming: str,
        translation: str,
        system: str,
        errors: str,
    ) -> None:
        self.chk_incoming.setText(incoming)
        self.chk_translation.setText(translation)
        self.chk_system.setText(system)
        self.chk_errors.setText(errors)

    def append(self, line: str) -> None:
        self.append_log_line(line)

    def append_log_line(self, line: str, category: str | None = None) -> None:
        record = self._make_record(str(line), category)
        self.records.append(record)

        if len(self.records) > self.MAX_RECORDS:
            self.records = self.records[-self.MAX_RECORDS :]

        if self._record_visible(record):
            self._append_record_to_text(record)

    def clear(self) -> None:
        self.records.clear()
        self.text.clear()

    def _make_checkbox(self, text: str) -> QCheckBox:
        checkbox = QCheckBox(text)
        checkbox.setChecked(True)
        checkbox.toggled.connect(self._render_records)
        checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                color: {Colors.TEXT_MUTED};
                font-size: 11px;
                font-weight: 800;
                spacing: 6px;
                background: transparent;
                border: none;
            }}
            QCheckBox:hover {{
                color: {Colors.TEXT};
            }}
            QCheckBox::indicator {{
                width: 13px;
                height: 13px;
                border: 1px solid {Colors.BORDER};
                border-radius: 3px;
                background-color: #101010;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.CYAN_DARK};
                border: 1px solid {Colors.CYAN};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #101010;
                border: 1px solid {Colors.BORDER};
            }}
            """
        )
        return checkbox

    def _make_record(self, line: str, category: str | None) -> LogRecord:
        normalized_category = self._normalize_category(category) or self._line_category(line)
        color = self._line_color(line, normalized_category)
        return LogRecord(line=line, category=normalized_category, color=color)

    def _normalize_category(self, category: str | None) -> str | None:
        if not category:
            return None

        normalized = str(category).strip().lower()
        if normalized in {"incoming", "translation", "system", "error"}:
            return normalized

        return None

    def _line_category(self, line: str) -> str:
        lowered = str(line).lower()

        if any(word in lowered for word in self.ERROR_WORDS):
            return "error"

        if any(word in lowered for word in self.TRANSLATION_WORDS):
            return "translation"

        if any(word in lowered for word in self.INCOMING_WORDS):
            return "incoming"

        return "system"

    def _line_color(self, line: str, category: str) -> str:
        lowered = str(line).lower()

        if category == "error":
            return "#FF5555"

        if category == "incoming":
            return Colors.CYAN

        if category == "translation":
            return Colors.ORANGE

        if any(word in lowered for word in self.SUCCESS_WORDS):
            return Colors.GREEN

        return Colors.TEXT_MUTED

    def _record_visible(self, record: LogRecord) -> bool:
        if record.category == "incoming":
            return self.chk_incoming.isChecked()

        if record.category == "translation":
            return self.chk_translation.isChecked()

        if record.category == "error":
            return self.chk_errors.isChecked()

        return self.chk_system.isChecked()

    def _append_record_to_text(self, record: LogRecord) -> None:
        safe_line = html.escape(record.line)
        self.text.append(f'<span style="color:{record.color};">{safe_line}</span>')

    def _render_records(self) -> None:
        scrollbar = self.text.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 4

        self.text.clear()

        for record in self.records:
            if self._record_visible(record):
                self._append_record_to_text(record)

        if was_at_bottom:
            scrollbar.setValue(scrollbar.maximum())