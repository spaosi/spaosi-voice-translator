from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from spaosi_voice_translator.core.constants import DEFAULT_SETTINGS_FILE


@dataclass
class SettingsStore:
    path: Path = field(default_factory=lambda: Path(DEFAULT_SETTINGS_FILE))
    _data: dict[str, Any] = field(default_factory=dict)

    def load(self) -> None:
        if not self.path.exists():
            self._data = {}
            return

        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._data = {}

    def save(self) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
