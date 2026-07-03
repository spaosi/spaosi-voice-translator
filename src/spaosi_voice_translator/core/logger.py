from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AppLogger:
    records: list[str] = field(default_factory=list)

    def info(self, message: str) -> str:
        return self._write(message)

    def warning(self, message: str) -> str:
        return self._write(message)

    def error(self, message: str) -> str:
        return self._write(message)

    def _write(self, message: str) -> str:
        line = f"{datetime.now().strftime('%H:%M:%S')}: {message}"
        self.records.append(line)
        return line
