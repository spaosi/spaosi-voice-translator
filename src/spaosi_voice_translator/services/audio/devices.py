from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioDevice:
    id: str
    name: str

    @property
    def label(self) -> str:
        return self.name.strip() or self.id


def list_system_output_devices() -> list[AudioDevice]:
    try:
        import soundcard as sc
    except ImportError:
        return []

    devices: list[AudioDevice] = []

    for speaker in sc.all_speakers():
        device_id = str(getattr(speaker, "id", "") or "")
        name = str(getattr(speaker, "name", "") or device_id)

        if device_id:
            devices.append(AudioDevice(id=device_id, name=name))

    return devices


def list_microphone_devices() -> list[AudioDevice]:
    try:
        import soundcard as sc
    except ImportError:
        return []

    devices: list[AudioDevice] = []

    for microphone in sc.all_microphones(include_loopback=False):
        device_id = str(getattr(microphone, "id", "") or "")
        name = str(getattr(microphone, "name", "") or device_id)

        if device_id:
            devices.append(AudioDevice(id=device_id, name=name))

    return devices


def default_system_output_id() -> str:
    try:
        import soundcard as sc
    except ImportError:
        return ""

    try:
        return str(sc.default_speaker().id or "")
    except Exception:
        return ""


def default_microphone_id() -> str:
    try:
        import soundcard as sc
    except ImportError:
        return ""

    try:
        return str(sc.default_microphone().id or "")
    except Exception:
        return ""
