from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from spaosi_voice_translator.core.i18n import UI_LANGUAGES
from spaosi_voice_translator.core.settings import SettingsStore
from spaosi_voice_translator.services.audio.devices import (
    default_microphone_id,
    default_system_output_id,
    list_microphone_devices,
    list_system_output_devices,
)
from spaosi_voice_translator.ui.settings.hotkey_capture_button import HotkeyCaptureButton
from spaosi_voice_translator.ui.settings.language_catalogs import (
    DEEPGRAM_LANGUAGES,
    LEGACY_LANGUAGE_LABELS,
    TRANSLATION_LANGUAGES,
)
from spaosi_voice_translator.ui.settings.settings_nav import SettingsNavButton
from spaosi_voice_translator.ui.settings.settings_rows import SettingsContentPage
from spaosi_voice_translator.ui.theme.colors import Colors
from spaosi_voice_translator.ui.widgets.buttons import ToggleButton
from spaosi_voice_translator.ui.widgets.fields import CompactCombo, CompactLineEdit, CompactSpinBox



class CopyOnClickLineEdit(CompactLineEdit):
    copied = pyqtSignal(str)

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(placeholder, parent)
        self._idle_tooltip = ""
        self._copied_tooltip = ""
        self.setReadOnly(True)
        self.setCursorPosition(0)

    def set_copy_tooltips(self, *, idle: str, copied: str) -> None:
        self._idle_tooltip = idle
        self._copied_tooltip = copied
        self.setToolTip(idle)

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)

        value = self.text().strip()
        if not value:
            return

        QApplication.clipboard().setText(value)
        self.selectAll()
        self.setToolTip(self._copied_tooltip or self._idle_tooltip)
        self.copied.emit(value)


class SettingsPage(QWidget):
    def __init__(self, parent_window, settings: SettingsStore | None = None):
        super().__init__()
        self.parent_window = parent_window
        self.settings = settings
        self.translator = parent_window.context.translator
        self.nav_buttons: list[SettingsNavButton] = []
        self.nav_entries: list[tuple[SettingsNavButton, str]] = []
        self.rows: dict[str, object] = {}
        self._loading = True
        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("SettingsSurface")
        surface.setStyleSheet(
            f"""
            QFrame#SettingsSurface {{
                background-color: {Colors.PANEL_3};
                border: 1px solid {Colors.BORDER};
                border-radius: 7px;
            }}
            """
        )
        root.addWidget(surface, 1)

        layout = QHBoxLayout(surface)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        nav = QFrame()
        nav.setFixedWidth(148)
        nav.setStyleSheet("background: transparent; border: none;")
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(7)

        self.nav_title = QLabel()
        self.nav_title.setFixedHeight(22)
        self.nav_title.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )
        nav_layout.addWidget(self.nav_title)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent; border: none;")

        self._build_general_page()
        self._build_widgets_page(parent_window)
        self._build_audio_page()
        self._build_keys_page()
        self._load_from_store()

        self._add_page(nav_layout, "settings.nav.general", self.general_page)
        self._add_page(nav_layout, "settings.nav.widgets", self.widgets_page)
        self._add_page(nav_layout, "settings.nav.audio", self.audio_page)
        self._add_page(nav_layout, "settings.nav.keys", self.keys_page)

        nav_layout.addStretch(1)

        separator = QFrame()
        separator.setFixedWidth(1)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_DARK}; border: none;")

        layout.addWidget(nav)
        layout.addWidget(separator)
        layout.addWidget(self.stack, 1)

        self._loading = False
        self.apply_translations()
        self._select_page(0)

    def tr(self, key: str, **kwargs) -> str:
        return self.translator.t(key, **kwargs)

    def ui_language_value(self) -> str:
        return str(self.ui_language_combo.currentData() or self.translator.language_code())

    def deepgram_key_value(self) -> str:
        return self.deepgram_key.text().strip()

    def gemini_key_value(self) -> str:
        return self.gemini_key.text().strip()

    def gemini_proxy_url_value(self) -> str:
        return self.gemini_proxy_url.text().strip()

    def language_code(self) -> str:
        return str(self.language_combo.currentData() or "en")

    def language_name(self) -> str:
        index = self.language_combo.currentIndex()
        target_name = self.language_combo.itemData(index, Qt.ItemDataRole.UserRole + 1)
        return str(target_name or "English")

    def target_language_name(self) -> str:
        return str(self.translation_language_combo.currentData() or "Русский")

    def target_language_deepgram_name(self) -> str:
        target_name = self.target_language_name()
        if self._contains_latin(target_name):
            return target_name

        label = str(self.translation_language_combo.currentText() or "")
        for part in label.split("—"):
            candidate = part.strip()
            if self._contains_latin(candidate):
                return candidate

        return target_name

    def target_language_deepgram_code(self) -> str:
        target_name = self._normalize_language_name(self.target_language_deepgram_name())

        for language in DEEPGRAM_LANGUAGES:
            if self._normalize_language_name(language.target_name) == target_name:
                return language.code

        return "multi"

    def selected_system_device_id(self) -> str:
        return str(self.system_sound_combo.currentData() or "")

    def selected_microphone_device_id(self) -> str:
        return str(self.microphone_combo.currentData() or "")

    def system_endpointing_ms(self) -> int:
        if self.is_video_translation_mode():
            return 600

        return int(self.system_silence_pause.value())

    def microphone_endpointing_ms(self) -> int:
        return int(self.microphone_silence_pause.value())

    def is_video_translation_mode(self) -> bool:
        return bool(self.video_translation_mode_toggle.isChecked())

    def voice_hotkey_value(self) -> str:
        return self.voice_hotkey.hotkey()

    def _contains_latin(self, value: str) -> bool:
        return any(("a" <= char.lower() <= "z") for char in str(value or ""))

    def _normalize_language_name(self, value: str) -> str:
        return " ".join(str(value or "").strip().lower().split())

    def save_to_store(self) -> None:
        if not self.settings:
            return

        self.settings.set("deepgram_key", self.deepgram_key_value())
        self.settings.set("gemini_key", self.gemini_key_value())
        self.settings.set("gemini_proxy_url", self.gemini_proxy_url_value())
        self.settings.set("ui_language", self.ui_language_value())
        self.settings.set("ui_language_selected", True)
        self.settings.set("language", self.language_combo.currentText())
        self.settings.set("language_code", self.language_code())
        self.settings.set("target_language", self.translation_language_combo.currentText())
        self.settings.set("target_language_name", self.target_language_name())
        self.settings.set("voice_hotkey", self.voice_hotkey_value())
        self.settings.set("video_translation_mode", self.is_video_translation_mode())
        self.settings.set("system_device_id", self.selected_system_device_id())
        self.settings.set("microphone_device_id", self.selected_microphone_device_id())
        self.settings.set("system_endpointing_ms", self.system_endpointing_ms())
        self.settings.set("microphone_endpointing_ms", self.microphone_endpointing_ms())
        self.settings.set("obs_widget_url", self.obs_widget_url.text().strip())

    def _load_from_store(self) -> None:
        if not self.settings:
            return

        self._select_combo_by_data(self.ui_language_combo, self.translator.language_code())

        saved_code = str(self.settings.get("language_code", "") or "")
        saved_label = str(self.settings.get("language", "English") or "English")
        saved_label = LEGACY_LANGUAGE_LABELS.get(saved_label, saved_label)

        if saved_code:
            self._select_language_by_code(saved_code)
        else:
            self._select_language_by_label(saved_label)

        saved_target_name = str(self.settings.get("target_language_name", "Русский") or "Русский")
        saved_target_label = str(self.settings.get("target_language", "") or "")
        if saved_target_name:
            self._select_translation_language_by_name(saved_target_name)
        elif saved_target_label:
            self._select_translation_language_by_label(saved_target_label)

        self.voice_hotkey.set_hotkey(str(self.settings.get("voice_hotkey", "F2") or "F2"))
        self.deepgram_key.setText(str(self.settings.get("deepgram_key", "") or ""))
        self.gemini_key.setText(str(self.settings.get("gemini_key", "") or ""))
        self.gemini_proxy_url.setText(str(self.settings.get("gemini_proxy_url", "") or ""))

        self.obs_widget_url.setText(
            str(
                self.settings.get("obs_widget_url", "http://127.0.0.1:8088/obs")
                or "http://127.0.0.1:8088/obs"
            )
        )

        self._select_combo_by_data(
            self.system_sound_combo,
            str(self.settings.get("system_device_id", "") or default_system_output_id()),
        )
        self._select_combo_by_data(
            self.microphone_combo,
            str(self.settings.get("microphone_device_id", "") or default_microphone_id()),
        )

        self.system_silence_pause.setValue(int(self.settings.get("system_endpointing_ms", 300) or 300))
        self.microphone_silence_pause.setValue(
            int(self.settings.get("microphone_endpointing_ms", 300) or 300)
        )

        self.video_translation_mode_toggle.setChecked(
            bool(self.settings.get("video_translation_mode", False))
        )

        self._sync_combo_tooltip(self.system_sound_combo)
        self._sync_combo_tooltip(self.microphone_combo)

    def apply_translations(self) -> None:
        self.nav_title.setText(self.tr("settings.title"))

        self.general_page.set_title(self.tr("settings.section.general"))
        self.widgets_page.set_title(self.tr("settings.section.widgets"))
        self.audio_page.set_title(self.tr("settings.section.audio"))
        self.keys_page.set_title(self.tr("settings.section.keys"))

        row_labels = {
            "ui_language": "settings.row.ui_language",
            "recognition_language": "settings.row.recognition_language",
            "translation_language": "settings.row.translation_language",
            "mode": "settings.row.mode",
            "voice_hotkey": "settings.row.voice_hotkey",
            "external_voices": "settings.row.external_voices",
            "microphone_translation": "settings.row.microphone_translation",
            "obs_widget": "settings.row.obs_widget",
            "microphone": "settings.row.microphone",
            "microphone_pause": "settings.row.microphone_pause",
            "system_audio": "settings.row.system_audio",
            "system_pause": "settings.row.system_pause",
            "deepgram": "settings.row.deepgram",
            "gemini": "settings.row.gemini",
            "gemini_proxy": "settings.row.gemini_proxy",
        }

        for row_name, translation_key in row_labels.items():
            row = self.rows.get(row_name)
            if row is not None:
                row.set_label(self.tr(translation_key))

        for button, translation_key in self.nav_entries:
            button.setText(self.tr(translation_key))

        self.video_translation_mode_toggle.set_base_text(self.tr("settings.video_translation_mode"))
        self.video_translation_mode_toggle.setToolTip(
            self.tr("settings.video_translation_mode.tooltip")
        )
        self.external_voices_toggle.set_base_text(self.tr("settings.external_voices"))
        self.microphone_translation_toggle.set_base_text(self.tr("settings.microphone"))

        self.obs_copy_status.setText(self.tr("settings.obs_copied"))
        self.obs_size_hint.setText(self.tr("settings.obs_size_hint"))
        self.obs_widget_url.set_copy_tooltips(
            idle=self.tr("settings.obs_tooltip"),
            copied=self.tr("settings.obs_copied"),
        )
        self.deepgram_key.setPlaceholderText(self.tr("settings.deepgram_placeholder"))
        self.gemini_key.setPlaceholderText(self.tr("settings.gemini_placeholder"))
        self.gemini_proxy_url.setPlaceholderText(self.tr("settings.gemini_proxy_placeholder"))
        self.gemini_proxy_url.setToolTip(self.tr("settings.gemini_proxy_tooltip"))

        self.voice_hotkey.apply_translations(
            idle_tooltip=self.tr("settings.hotkey_tooltip"),
            capture_text=self.tr("settings.hotkey_capture"),
            capture_tooltip=self.tr("settings.hotkey_capture_tooltip"),
            saved_prefix=self.tr("settings.hotkey_saved"),
        )

        self._refresh_language_tooltips()

    def _refresh_language_tooltips(self) -> None:
        for index, language in enumerate(DEEPGRAM_LANGUAGES):
            self.language_combo.setItemData(
                index,
                self.tr("settings.deepgram_tooltip", label=language.label, code=language.code),
                Qt.ItemDataRole.ToolTipRole,
            )

        for index, language in enumerate(TRANSLATION_LANGUAGES):
            self.translation_language_combo.setItemData(
                index,
                self.tr("settings.translation_tooltip", language=language.name),
                Qt.ItemDataRole.ToolTipRole,
            )

        self._sync_combo_tooltip(self.ui_language_combo)
        self._sync_combo_tooltip(self.language_combo)
        self._sync_combo_tooltip(self.translation_language_combo)

    def _build_general_page(self) -> None:
        self.general_page = SettingsContentPage("")

        self.ui_language_combo = CompactCombo()
        self._fill_ui_languages()

        self.language_combo = CompactCombo()
        self._fill_deepgram_languages()

        self.translation_language_combo = CompactCombo()
        self._fill_translation_languages()

        self.video_translation_mode_toggle = ToggleButton("", checked=False)
        self.video_translation_mode_toggle.toggled.connect(self._on_video_mode_toggled)

        self.voice_hotkey = HotkeyCaptureButton("F2")
        self.voice_hotkey.hotkey_changed.connect(self._on_voice_hotkey_changed)

        self.rows["ui_language"] = self.general_page.add_row("", self.ui_language_combo)
        self.rows["recognition_language"] = self.general_page.add_row("", self.language_combo)
        self.rows["translation_language"] = self.general_page.add_row("", self.translation_language_combo)
        self.rows["mode"] = self.general_page.add_row("", self.video_translation_mode_toggle)
        self.rows["voice_hotkey"] = self.general_page.add_row("", self.voice_hotkey)
        self.general_page.finish()

    def _build_widgets_page(self, parent_window) -> None:
        self.widgets_page = SettingsContentPage("")

        self.external_voices_toggle = ToggleButton("", checked=True)
        self.microphone_translation_toggle = ToggleButton("", checked=True)

        self.obs_widget_url = CopyOnClickLineEdit("http://127.0.0.1:8088/obs")
        self.obs_widget_url.setText("http://127.0.0.1:8088/obs")
        self.obs_widget_url.copied.connect(self._on_obs_link_copied)

        self.obs_size_hint = QLabel()
        self.obs_size_hint.setFixedHeight(24)
        self.obs_size_hint.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.obs_size_hint.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.TEXT_MUTED};
                background-color: transparent;
                border: none;
                padding: 2px 4px;
                font-size: 11px;
                font-weight: 800;
            }}
            """
        )

        self.obs_copy_status = QLabel()
        self.obs_copy_status.setFixedHeight(24)
        self.obs_copy_status.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.obs_copy_status.setVisible(False)
        self.obs_copy_status.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.GREEN};
                background-color: #061406;
                border: 1px solid {Colors.GREEN};
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 900;
            }}
            """
        )

        self.external_voices_toggle.toggled.connect(parent_window.toggle_game_overlay.emit)
        self.microphone_translation_toggle.toggled.connect(parent_window.toggle_voice_overlay.emit)

        self.rows["external_voices"] = self.widgets_page.add_row("", self.external_voices_toggle)
        self.rows["microphone_translation"] = self.widgets_page.add_row("", self.microphone_translation_toggle)
        self.rows["obs_widget"] = self.widgets_page.add_row("", self.obs_widget_url)
        self.rows["obs_size_hint"] = self.widgets_page.add_row("", self.obs_size_hint)
        self.rows["obs_copy_status"] = self.widgets_page.add_row("", self.obs_copy_status)
        self.widgets_page.finish()


    def _build_audio_page(self) -> None:
        self.audio_page = SettingsContentPage("")

        self.microphone_combo = CompactCombo()
        self._fill_microphone_devices()

        self.microphone_silence_pause = CompactSpinBox()

        self.system_sound_combo = CompactCombo()
        self._fill_system_output_devices()

        self.system_silence_pause = CompactSpinBox()

        self.rows["microphone"] = self.audio_page.add_row("", self.microphone_combo)
        self.rows["microphone_pause"] = self.audio_page.add_row("", self.microphone_silence_pause)
        self.rows["system_audio"] = self.audio_page.add_row("", self.system_sound_combo)
        self.rows["system_pause"] = self.audio_page.add_row("", self.system_silence_pause)
        self.audio_page.finish()


    def _build_keys_page(self) -> None:
        self.keys_page = SettingsContentPage("")

        self.deepgram_key = CompactLineEdit("")
        self.deepgram_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.gemini_key = CompactLineEdit("")
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)

        self.gemini_proxy_url = CompactLineEdit("")

        self.rows["deepgram"] = self.keys_page.add_row("", self.deepgram_key)
        self.rows["gemini"] = self.keys_page.add_row("", self.gemini_key)
        self.rows["gemini_proxy"] = self.keys_page.add_row("", self.gemini_proxy_url)
        self.keys_page.finish()


    def _fill_ui_languages(self) -> None:
        self.ui_language_combo.clear()

        for language in UI_LANGUAGES:
            self.ui_language_combo.addItem(language.label, language.code)
            index = self.ui_language_combo.count() - 1
            self.ui_language_combo.setItemData(
                index,
                language.label,
                Qt.ItemDataRole.ToolTipRole,
            )

            item = self.ui_language_combo.model().item(index)
            if item is not None and not language.enabled:
                item.setEnabled(False)

        self.ui_language_combo.currentIndexChanged.connect(self._on_ui_language_changed)
        self._sync_combo_tooltip(self.ui_language_combo)

    def _fill_deepgram_languages(self) -> None:
        self.language_combo.clear()

        for language in DEEPGRAM_LANGUAGES:
            self.language_combo.addItem(language.label, language.code)
            index = self.language_combo.count() - 1
            self.language_combo.setItemData(
                index,
                language.target_name,
                Qt.ItemDataRole.UserRole + 1,
            )
            self.language_combo.setItemData(
                index,
                self.tr("settings.deepgram_tooltip", label=language.label, code=language.code),
                Qt.ItemDataRole.ToolTipRole,
            )

        self.language_combo.currentIndexChanged.connect(
            lambda _index: self._sync_combo_tooltip(self.language_combo)
        )
        self._sync_combo_tooltip(self.language_combo)

    def _fill_translation_languages(self) -> None:
        self.translation_language_combo.clear()

        for language in TRANSLATION_LANGUAGES:
            self.translation_language_combo.addItem(language.label, language.name)
            index = self.translation_language_combo.count() - 1
            self.translation_language_combo.setItemData(
                index,
                self.tr("settings.translation_tooltip", language=language.name),
                Qt.ItemDataRole.ToolTipRole,
            )

        self.translation_language_combo.currentIndexChanged.connect(
            lambda _index: self._sync_combo_tooltip(self.translation_language_combo)
        )
        self._sync_combo_tooltip(self.translation_language_combo)

    def _select_translation_language_by_name(self, name: str) -> None:
        if not name:
            return

        normalized_name = str(name).strip().lower()
        for index in range(self.translation_language_combo.count()):
            item_name = str(self.translation_language_combo.itemData(index) or "")
            if item_name.strip().lower() == normalized_name:
                self.translation_language_combo.setCurrentIndex(index)
                self._sync_combo_tooltip(self.translation_language_combo)
                return

    def _select_translation_language_by_label(self, label: str) -> None:
        if not label:
            return

        for index in range(self.translation_language_combo.count()):
            if self.translation_language_combo.itemText(index) == label:
                self.translation_language_combo.setCurrentIndex(index)
                self._sync_combo_tooltip(self.translation_language_combo)
                return

    def _select_language_by_code(self, code: str) -> None:
        if not code:
            return

        for index in range(self.language_combo.count()):
            if str(self.language_combo.itemData(index) or "") == code:
                self.language_combo.setCurrentIndex(index)
                self._sync_combo_tooltip(self.language_combo)
                return

    def _select_language_by_label(self, label: str) -> None:
        if not label:
            return

        for index in range(self.language_combo.count()):
            if self.language_combo.itemText(index) == label:
                self.language_combo.setCurrentIndex(index)
                self._sync_combo_tooltip(self.language_combo)
                return

        legacy_label = LEGACY_LANGUAGE_LABELS.get(label)
        if legacy_label:
            self._select_language_by_label(legacy_label)

    def _fill_system_output_devices(self) -> None:
        self.system_sound_combo.clear()
        devices = list_system_output_devices()

        if not devices:
            self._add_combo_item_with_tooltip(
                self.system_sound_combo,
                self.tr("settings.system_devices_not_found"),
                "",
                self.tr("settings.system_devices_not_found"),
            )
            return

        for device in devices:
            self._add_combo_item_with_tooltip(self.system_sound_combo, device.label, device.id, device.name)

        self.system_sound_combo.currentIndexChanged.connect(
            lambda _index: self._sync_combo_tooltip(self.system_sound_combo)
        )
        self._sync_combo_tooltip(self.system_sound_combo)

    def _fill_microphone_devices(self) -> None:
        self.microphone_combo.clear()
        devices = list_microphone_devices()

        if not devices:
            self._add_combo_item_with_tooltip(
                self.microphone_combo,
                self.tr("settings.microphones_not_found"),
                "",
                self.tr("settings.microphones_not_found"),
            )
            return

        for device in devices:
            self._add_combo_item_with_tooltip(self.microphone_combo, device.label, device.id, device.name)

        self.microphone_combo.currentIndexChanged.connect(
            lambda _index: self._sync_combo_tooltip(self.microphone_combo)
        )
        self._sync_combo_tooltip(self.microphone_combo)

    def _add_combo_item_with_tooltip(
        self,
        combo: CompactCombo,
        label: str,
        value: str,
        tooltip: str,
    ) -> None:
        combo.addItem(label, value)
        index = combo.count() - 1
        full_tooltip = tooltip.strip() or label
        combo.setItemData(index, full_tooltip, Qt.ItemDataRole.ToolTipRole)
        combo.setItemData(index, full_tooltip, Qt.ItemDataRole.AccessibleTextRole)

    def _sync_combo_tooltip(self, combo: CompactCombo) -> None:
        tooltip = combo.itemData(combo.currentIndex(), Qt.ItemDataRole.ToolTipRole)
        combo.setToolTip(str(tooltip or combo.currentText()))

    def _select_combo_by_data(self, combo: CompactCombo, value: str) -> None:
        if not value:
            return

        for index in range(combo.count()):
            if str(combo.itemData(index) or "") == value:
                combo.setCurrentIndex(index)
                self._sync_combo_tooltip(combo)
                return

    def _on_ui_language_changed(self, _index: int) -> None:
        if self._loading:
            return

        self.translator.set_language(self.ui_language_value(), mark_selected=True)
        self.save_to_store()

        if self.settings:
            self.settings.save()

        self.parent_window.context.signals.language_changed.emit(self.translator.language_code())

    def _on_video_mode_toggled(self, checked: bool) -> None:
        if checked and hasattr(self, "system_silence_pause"):
            self.system_silence_pause.setValue(600)

        if hasattr(self.parent_window, "set_video_translation_mode"):
            self.parent_window.set_video_translation_mode(bool(checked))

        if checked and hasattr(self.parent_window, "append_log"):
            self.parent_window.append_log(
                self.tr("main.log.video_enabled"),
                "system",
            )

    def _on_voice_hotkey_changed(self, hotkey: str) -> None:
        if hasattr(self.parent_window, "append_log"):
            self.parent_window.append_log(self.tr("main.log.hotkey_selected", hotkey=hotkey.upper()), "system")

        if hasattr(self.parent_window, "apply_voice_hotkey_from_settings"):
            self.parent_window.apply_voice_hotkey_from_settings()

    def _on_obs_link_copied(self, url: str) -> None:
        self.obs_copy_status.setText(self.tr("settings.obs_copied"))
        self.obs_copy_status.setVisible(True)
        self.obs_widget_url.setToolTip(self.tr("settings.obs_copied"))

        QTimer.singleShot(2200, self._hide_obs_copy_status)

        if hasattr(self.parent_window, "append_log"):
            self.parent_window.append_log(self.tr("settings.obs_copied_log", url=url), "system")

    def _hide_obs_copy_status(self) -> None:
        self.obs_copy_status.setVisible(False)
        self.obs_widget_url.setToolTip(self.tr("settings.obs_tooltip"))

    def _add_page(self, nav_layout: QVBoxLayout, translation_key: str, page: QWidget) -> None:
        index = self.stack.addWidget(page)
        button = SettingsNavButton(self.tr(translation_key))
        button.clicked.connect(lambda checked=False, i=index: self._select_page(i))
        self.nav_buttons.append(button)
        self.nav_entries.append((button, translation_key))
        nav_layout.addWidget(button)

    def _select_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)