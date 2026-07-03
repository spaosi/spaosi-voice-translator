from __future__ import annotations

from dataclasses import dataclass, field

from spaosi_voice_translator.core.i18n import Translator
from spaosi_voice_translator.core.logger import AppLogger
from spaosi_voice_translator.core.settings import SettingsStore
from spaosi_voice_translator.core.signals import AppSignals


@dataclass
class AppContext:
    settings: SettingsStore = field(default_factory=SettingsStore)
    logger: AppLogger = field(default_factory=AppLogger)
    signals: AppSignals = field(default_factory=AppSignals)
    translator: Translator = field(init=False)

    def __post_init__(self) -> None:
        self.translator = Translator(self.settings)

    def initialize(self) -> None:
        self.settings.load()
        self.translator.reload_from_settings()
        self.logger.info(self.translator.t("app.settings_loaded"))
