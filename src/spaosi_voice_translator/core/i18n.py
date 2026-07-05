from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spaosi_voice_translator.core.settings import SettingsStore


DEFAULT_UI_LANGUAGE = "ru"
FALLBACK_UI_LANGUAGE = "en"
UI_LANGUAGE_KEY = "ui_language"
UI_LANGUAGE_SELECTED_KEY = "ui_language_selected"


@dataclass(frozen=True)
class UiLanguage:
    code: str
    native_name: str
    english_name: str
    enabled: bool = True

    @property
    def label(self) -> str:
        if self.native_name == self.english_name:
            return self.native_name

        return f"{self.native_name} / {self.english_name}"


UI_LANGUAGES: tuple[UiLanguage, ...] = (
    UiLanguage("ru", "Русский", "Russian", True),
    UiLanguage("en", "English", "English", True),
    UiLanguage("es", "Español", "Spanish", True),
    UiLanguage("fr", "Français", "French", True),
    UiLanguage("de", "Deutsch", "German", True),
)


_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "app.settings_loaded": "Настройки загружены",
        "app.windows_created": "Окна интерфейса созданы",
        "app.ready": "Приложение готово",
        "app.obs_started": "OBS виджет запущен: {url}",
        "app.obs_error": "Ошибка OBS виджета: {error}",

        "language_dialog.title": "Выберите язык интерфейса",
        "language_dialog.subtitle": "Это можно будет изменить позже в настройках.",
        "language_dialog.footer": "Spaosi Voice Translator",

        "main.start": "ПУСК",
        "main.stop": "СТОП",
        "main.mode.realtime": "РЕЖИМ: REALTIME",
        "main.mode.video": "РЕЖИМ: ВИДЕО",
        "main.mode.realtime.tooltip": "Realtime: быстрый перевод с лимитом 14 слов",
        "main.mode.video.tooltip": "Видео перевода: пауза SYS 600 мс, фразы не режутся по лимиту слов",
        "main.mic.idle": "MIC: {hotkey}",
        "main.mic.recording": "MIC: ПИШЕТ",
        "main.mic.tooltip": "Хоткей микрофона: {hotkey}. Нажал — запись, нажал ещё раз — перевод.",
        "main.log.interface_loaded": "Интерфейс загружен",
        "main.log.sys_idle": "SYS не запущен: звук системы не слушается",
        "main.log.video_enabled": "Режим Видео перевода включён: пауза SYS 600 мс, лимит слов отключён",
        "main.log.hotkey_selected": "MIC хоткей выбран: {hotkey}",
        "main.log.hotkey_registered": "MIC хоткей зарегистрирован: {hotkey}",

        "settings.title": "НАСТРОЙКИ",
        "settings.nav.general": "Общее",
        "settings.nav.widgets": "Виджеты",
        "settings.nav.audio": "Аудио",
        "settings.nav.keys": "Ключи",
        "settings.section.general": "ОБЩЕЕ",
        "settings.section.widgets": "ВИДЖЕТЫ",
        "settings.section.audio": "АУДИО",
        "settings.section.keys": "КЛЮЧИ",
        "settings.row.ui_language": "Язык интерфейса",
        "settings.row.recognition_language": "Язык распознавания",
        "settings.row.translation_language": "Язык перевода",
        "settings.row.mode": "Режим",
        "settings.row.voice_hotkey": "Хоткей микрофона",
        "settings.row.external_voices": "Внешние голоса",
        "settings.row.microphone_translation": "Перевод микрофона",
        "settings.row.obs_widget": "OBS виджет",
        "settings.row.microphone": "Микрофон",
        "settings.row.microphone_pause": "Пауза микрофона",
        "settings.row.system_audio": "Звук системы",
        "settings.row.system_pause": "Пауза звука",
        "settings.row.deepgram": "Deepgram",
        "settings.row.gemini": "Gemini",
        "settings.row.gemini_proxy": "Gemini proxy",
        "settings.video_translation_mode": "Видео перевода",
        "settings.video_translation_mode.tooltip": "Для перевода видео: не режет длинные фразы и ставит паузу SYS 600 мс",
        "settings.external_voices": "Внешние голоса",
        "settings.microphone": "Микрофон",
        "settings.obs_copied": "Ссылка сохранена в буфер обмена",
        "settings.obs_tooltip": "Нажми, чтобы скопировать ссылку",
        "settings.obs_size_hint": "Размер источника OBS: 1920×1080",
        "settings.hotkey_tooltip": "Нажми кнопку, затем нажми клавишу или комбинацию",
        "settings.hotkey_capture": "НАЖМИ КЛАВИШУ...",
        "settings.hotkey_capture_tooltip": "Нажми нужную клавишу. Esc — отмена",
        "settings.hotkey_saved": "СОХРАНЕНО: ",
        "settings.deepgram_placeholder": "Deepgram API key",
        "settings.gemini_placeholder": "Gemini API key",
        "settings.gemini_proxy_placeholder": "Optional Gemini proxy URL",
        "settings.gemini_proxy_tooltip": "Необязательный Gemini proxy. Оставь пустым, чтобы использовать Gemini API напрямую.",
        "settings.system_devices_not_found": "Устройства системного звука не найдены",
        "settings.microphones_not_found": "Микрофоны не найдены",
        "settings.deepgram_tooltip": "{label} | Deepgram language={code}",
        "settings.translation_tooltip": "Переводить на: {language}",
        "settings.obs_copied_log": "OBS: ссылка скопирована в буфер: {url}",

        "audio.sys": "SYS",
        "audio.idle": "НЕ\nЗАПУЩЕНО",
        "audio.active": "СЛУШАЕТ",
        "audio.off": "OFF",
        "audio.tooltip_idle": "SYS: не запущено — звук системы не слушается",
        "audio.tooltip_active": "SYS: звук системы слушается",

        "logs.filter.incoming": "Входящий текст",
        "logs.filter.translation": "Перевод",
        "logs.filter.system": "Системные логи",
        "logs.filter.errors": "Ошибки",

        "overlays.game.title": "ПЕРЕВОД ВНЕШНИХ ГОЛОСОВ",
        "overlays.voice.title": "ПЕРЕВОД МИКРОФОНА",
        "voice.waiting": "Ожидание голоса",
        "voice.listening": "Слушаю",
        "voice.press_hotkey_again": "Нажми горячую кнопку ещё раз, чтобы перевести",
        "voice.translation_ready": "Перевод готов",
    },
    "en": {
        "app.settings_loaded": "Settings loaded",
        "app.windows_created": "Interface windows created",
        "app.ready": "Application ready",
        "app.obs_started": "OBS widget started: {url}",
        "app.obs_error": "OBS widget error: {error}",

        "language_dialog.title": "Choose interface language",
        "language_dialog.subtitle": "You can change it later in Settings.",
        "language_dialog.footer": "Spaosi Voice Translator",

        "main.start": "START",
        "main.stop": "STOP",
        "main.mode.realtime": "MODE: REALTIME",
        "main.mode.video": "MODE: VIDEO",
        "main.mode.realtime.tooltip": "Realtime: fast translation with a 14-word phrase limit",
        "main.mode.video.tooltip": "Video translation: 600 ms SYS pause and no word-limit splitting",
        "main.mic.idle": "MIC: {hotkey}",
        "main.mic.recording": "MIC: REC",
        "main.mic.tooltip": "Microphone hotkey: {hotkey}. Press once to record, press again to translate.",
        "main.log.interface_loaded": "Interface loaded",
        "main.log.sys_idle": "SYS is not running: system audio is not being captured",
        "main.log.video_enabled": "Video translation mode enabled: SYS pause 600 ms, word limit disabled",
        "main.log.hotkey_selected": "MIC hotkey selected: {hotkey}",
        "main.log.hotkey_registered": "MIC hotkey registered: {hotkey}",

        "settings.title": "SETTINGS",
        "settings.nav.general": "General",
        "settings.nav.widgets": "Widgets",
        "settings.nav.audio": "Audio",
        "settings.nav.keys": "Keys",
        "settings.section.general": "GENERAL",
        "settings.section.widgets": "WIDGETS",
        "settings.section.audio": "AUDIO",
        "settings.section.keys": "KEYS",
        "settings.row.ui_language": "Interface language",
        "settings.row.recognition_language": "Recognition language",
        "settings.row.translation_language": "Translation language",
        "settings.row.mode": "Mode",
        "settings.row.voice_hotkey": "Microphone hotkey",
        "settings.row.external_voices": "External voices",
        "settings.row.microphone_translation": "Microphone translation",
        "settings.row.obs_widget": "OBS widget",
        "settings.row.microphone": "Microphone",
        "settings.row.microphone_pause": "Microphone pause",
        "settings.row.system_audio": "System audio",
        "settings.row.system_pause": "Audio pause",
        "settings.row.deepgram": "Deepgram",
        "settings.row.gemini": "Gemini",
        "settings.row.gemini_proxy": "Gemini proxy",
        "settings.video_translation_mode": "Video translation",
        "settings.video_translation_mode.tooltip": "For video translation: keeps long phrases intact and sets SYS pause to 600 ms",
        "settings.external_voices": "External voices",
        "settings.microphone": "Microphone",
        "settings.obs_copied": "Link copied to clipboard",
        "settings.obs_tooltip": "Click to copy the link",
        "settings.obs_size_hint": "OBS source size: 1920×1080",
        "settings.hotkey_tooltip": "Click the button, then press a key or key combination",
        "settings.hotkey_capture": "PRESS A KEY...",
        "settings.hotkey_capture_tooltip": "Press the required key. Esc cancels.",
        "settings.hotkey_saved": "SAVED: ",
        "settings.deepgram_placeholder": "Deepgram API key",
        "settings.gemini_placeholder": "Gemini API key",
        "settings.gemini_proxy_placeholder": "Optional Gemini proxy URL",
        "settings.gemini_proxy_tooltip": "Optional Gemini proxy. Leave empty to use the Gemini API directly.",
        "settings.system_devices_not_found": "System audio devices not found",
        "settings.microphones_not_found": "Microphones not found",
        "settings.deepgram_tooltip": "{label} | Deepgram language={code}",
        "settings.translation_tooltip": "Translate to: {language}",
        "settings.obs_copied_log": "OBS: link copied to clipboard: {url}",

        "audio.sys": "SYS",
        "audio.idle": "NOT\nRUNNING",
        "audio.active": "CAPTURING",
        "audio.off": "OFF",
        "audio.tooltip_idle": "SYS: not running — system audio is not being captured",
        "audio.tooltip_active": "SYS: system audio is being captured",

        "logs.filter.incoming": "Incoming text",
        "logs.filter.translation": "Translation",
        "logs.filter.system": "System logs",
        "logs.filter.errors": "Errors",

        "overlays.game.title": "EXTERNAL VOICES TRANSLATION",
        "overlays.voice.title": "MICROPHONE TRANSLATION",
        "voice.waiting": "Waiting for voice",
        "voice.listening": "Listening",
        "voice.press_hotkey_again": "Press the hotkey again to translate",
        "voice.translation_ready": "Translation ready",
    },
    "es": {
        "app.settings_loaded": "Configuración cargada",
        "app.windows_created": "Ventanas de la interfaz creadas",
        "app.ready": "Aplicación lista",
        "app.obs_started": "Widget de OBS iniciado: {url}",
        "app.obs_error": "Error del widget de OBS: {error}",

        "language_dialog.title": "Elige el idioma de la interfaz",
        "language_dialog.subtitle": "Podrás cambiarlo más tarde en Ajustes.",
        "language_dialog.footer": "Spaosi Voice Translator",

        "main.start": "INICIAR",
        "main.stop": "DETENER",
        "main.mode.realtime": "MODO: REALTIME",
        "main.mode.video": "MODO: VÍDEO",
        "main.mode.realtime.tooltip": "Realtime: traducción rápida con límite de 14 palabras",
        "main.mode.video.tooltip": "Traducción de vídeo: pausa SYS de 600 ms y sin corte por límite de palabras",
        "main.mic.idle": "MIC: {hotkey}",
        "main.mic.recording": "MIC: REC",
        "main.mic.tooltip": "Atajo del micrófono: {hotkey}. Pulsa una vez para grabar y otra vez para traducir.",
        "main.log.interface_loaded": "Interfaz cargada",
        "main.log.sys_idle": "SYS no está iniciado: no se está capturando el audio del sistema",
        "main.log.video_enabled": "Modo de traducción de vídeo activado: pausa SYS de 600 ms, límite de palabras desactivado",
        "main.log.hotkey_selected": "Atajo MIC seleccionado: {hotkey}",
        "main.log.hotkey_registered": "Atajo MIC registrado: {hotkey}",

        "settings.title": "AJUSTES",
        "settings.nav.general": "General",
        "settings.nav.widgets": "Widgets",
        "settings.nav.audio": "Audio",
        "settings.nav.keys": "Claves",
        "settings.section.general": "GENERAL",
        "settings.section.widgets": "WIDGETS",
        "settings.section.audio": "AUDIO",
        "settings.section.keys": "CLAVES",
        "settings.row.ui_language": "Idioma de la interfaz",
        "settings.row.recognition_language": "Idioma de reconocimiento",
        "settings.row.translation_language": "Idioma de traducción",
        "settings.row.mode": "Modo",
        "settings.row.voice_hotkey": "Atajo del micrófono",
        "settings.row.external_voices": "Voces externas",
        "settings.row.microphone_translation": "Traducción del micrófono",
        "settings.row.obs_widget": "Widget de OBS",
        "settings.row.microphone": "Micrófono",
        "settings.row.microphone_pause": "Pausa del micrófono",
        "settings.row.system_audio": "Audio del sistema",
        "settings.row.system_pause": "Pausa de audio",
        "settings.row.deepgram": "Deepgram",
        "settings.row.gemini": "Gemini",
        "settings.row.gemini_proxy": "Gemini proxy",
        "settings.video_translation_mode": "Traducción de vídeo",
        "settings.video_translation_mode.tooltip": "Para traducción de vídeo: conserva frases largas y fija la pausa SYS en 600 ms",
        "settings.external_voices": "Voces externas",
        "settings.microphone": "Micrófono",
        "settings.obs_copied": "Enlace copiado al portapapeles",
        "settings.obs_tooltip": "Haz clic para copiar el enlace",
        "settings.obs_size_hint": "Tamaño de la fuente OBS: 1920×1080",
        "settings.hotkey_tooltip": "Haz clic en el botón y luego pulsa una tecla o combinación",
        "settings.hotkey_capture": "PULSA UNA TECLA...",
        "settings.hotkey_capture_tooltip": "Pulsa la tecla necesaria. Esc cancela.",
        "settings.hotkey_saved": "GUARDADO: ",
        "settings.deepgram_placeholder": "Clave API de Deepgram",
        "settings.gemini_placeholder": "Clave API de Gemini",
        "settings.gemini_proxy_placeholder": "URL opcional del proxy de Gemini",
        "settings.gemini_proxy_tooltip": "Proxy Gemini opcional. Déjalo vacío para usar la API de Gemini directamente.",
        "settings.system_devices_not_found": "No se encontraron dispositivos de audio del sistema",
        "settings.microphones_not_found": "No se encontraron micrófonos",
        "settings.deepgram_tooltip": "{label} | idioma Deepgram={code}",
        "settings.translation_tooltip": "Traducir a: {language}",
        "settings.obs_copied_log": "OBS: enlace copiado al portapapeles: {url}",

        "audio.sys": "SYS",
        "audio.idle": "NO\nINICIADO",
        "audio.active": "CAPTURANDO",
        "audio.off": "OFF",
        "audio.tooltip_idle": "SYS: no iniciado — no se captura el audio del sistema",
        "audio.tooltip_active": "SYS: se está capturando el audio del sistema",

        "logs.filter.incoming": "Texto entrante",
        "logs.filter.translation": "Traducción",
        "logs.filter.system": "Logs del sistema",
        "logs.filter.errors": "Errores",

        "overlays.game.title": "TRADUCCIÓN DE VOCES EXTERNAS",
        "overlays.voice.title": "TRADUCCIÓN DEL MICRÓFONO",
        "voice.waiting": "Esperando voz",
        "voice.listening": "Escuchando",
        "voice.press_hotkey_again": "Pulsa el atajo otra vez para traducir",
        "voice.translation_ready": "Traducción lista",
    },
    "fr": {
        "app.settings_loaded": "Paramètres chargés",
        "app.windows_created": "Fenêtres de l'interface créées",
        "app.ready": "Application prête",
        "app.obs_started": "Widget OBS lancé : {url}",
        "app.obs_error": "Erreur du widget OBS : {error}",

        "language_dialog.title": "Choisir la langue de l'interface",
        "language_dialog.subtitle": "Vous pourrez la modifier plus tard dans les paramètres.",
        "language_dialog.footer": "Spaosi Voice Translator",

        "main.start": "DÉMARRER",
        "main.stop": "ARRÊTER",
        "main.mode.realtime": "MODE : REALTIME",
        "main.mode.video": "MODE : VIDÉO",
        "main.mode.realtime.tooltip": "Realtime : traduction rapide avec une limite de 14 mots",
        "main.mode.video.tooltip": "Traduction vidéo : pause SYS de 600 ms et aucune coupure par limite de mots",
        "main.mic.idle": "MIC : {hotkey}",
        "main.mic.recording": "MIC : REC",
        "main.mic.tooltip": "Raccourci du microphone : {hotkey}. Appuyez une fois pour enregistrer, puis encore pour traduire.",
        "main.log.interface_loaded": "Interface chargée",
        "main.log.sys_idle": "SYS n'est pas lancé : l'audio système n'est pas capturé",
        "main.log.video_enabled": "Mode de traduction vidéo activé : pause SYS 600 ms, limite de mots désactivée",
        "main.log.hotkey_selected": "Raccourci MIC sélectionné : {hotkey}",
        "main.log.hotkey_registered": "Raccourci MIC enregistré : {hotkey}",

        "settings.title": "PARAMÈTRES",
        "settings.nav.general": "Général",
        "settings.nav.widgets": "Widgets",
        "settings.nav.audio": "Audio",
        "settings.nav.keys": "Clés",
        "settings.section.general": "GÉNÉRAL",
        "settings.section.widgets": "WIDGETS",
        "settings.section.audio": "AUDIO",
        "settings.section.keys": "CLÉS",
        "settings.row.ui_language": "Langue de l'interface",
        "settings.row.recognition_language": "Langue de reconnaissance",
        "settings.row.translation_language": "Langue de traduction",
        "settings.row.mode": "Mode",
        "settings.row.voice_hotkey": "Raccourci microphone",
        "settings.row.external_voices": "Voix externes",
        "settings.row.microphone_translation": "Traduction du microphone",
        "settings.row.obs_widget": "Widget OBS",
        "settings.row.microphone": "Microphone",
        "settings.row.microphone_pause": "Pause du microphone",
        "settings.row.system_audio": "Audio système",
        "settings.row.system_pause": "Pause audio",
        "settings.row.deepgram": "Deepgram",
        "settings.row.gemini": "Gemini",
        "settings.row.gemini_proxy": "Gemini proxy",
        "settings.video_translation_mode": "Traduction vidéo",
        "settings.video_translation_mode.tooltip": "Pour la traduction vidéo : conserve les phrases longues et règle la pause SYS sur 600 ms",
        "settings.external_voices": "Voix externes",
        "settings.microphone": "Microphone",
        "settings.obs_copied": "Lien copié dans le presse-papiers",
        "settings.obs_tooltip": "Cliquez pour copier le lien",
        "settings.obs_size_hint": "Taille de la source OBS : 1920×1080",
        "settings.hotkey_tooltip": "Cliquez sur le bouton, puis appuyez sur une touche ou une combinaison",
        "settings.hotkey_capture": "APPUYEZ SUR UNE TOUCHE...",
        "settings.hotkey_capture_tooltip": "Appuyez sur la touche voulue. Échap annule.",
        "settings.hotkey_saved": "ENREGISTRÉ : ",
        "settings.deepgram_placeholder": "Clé API Deepgram",
        "settings.gemini_placeholder": "Clé API Gemini",
        "settings.gemini_proxy_placeholder": "URL optionnelle du proxy Gemini",
        "settings.gemini_proxy_tooltip": "Proxy Gemini optionnel. Laissez vide pour utiliser directement l’API Gemini.",
        "settings.system_devices_not_found": "Aucun périphérique audio système trouvé",
        "settings.microphones_not_found": "Aucun microphone trouvé",
        "settings.deepgram_tooltip": "{label} | langue Deepgram={code}",
        "settings.translation_tooltip": "Traduire vers : {language}",
        "settings.obs_copied_log": "OBS : lien copié dans le presse-papiers : {url}",

        "audio.sys": "SYS",
        "audio.idle": "NON\nLANCÉ",
        "audio.active": "CAPTURE",
        "audio.off": "OFF",
        "audio.tooltip_idle": "SYS : non lancé — l'audio système n'est pas capturé",
        "audio.tooltip_active": "SYS : l'audio système est capturé",

        "logs.filter.incoming": "Texte entrant",
        "logs.filter.translation": "Traduction",
        "logs.filter.system": "Logs système",
        "logs.filter.errors": "Erreurs",

        "overlays.game.title": "TRADUCTION DES VOIX EXTERNES",
        "overlays.voice.title": "TRADUCTION DU MICROPHONE",
        "voice.waiting": "En attente de voix",
        "voice.listening": "Écoute",
        "voice.press_hotkey_again": "Appuyez à nouveau sur le raccourci pour traduire",
        "voice.translation_ready": "Traduction prête",
    },
    "de": {
        "app.settings_loaded": "Einstellungen geladen",
        "app.windows_created": "Interface-Fenster erstellt",
        "app.ready": "Anwendung bereit",
        "app.obs_started": "OBS-Widget gestartet: {url}",
        "app.obs_error": "OBS-Widget-Fehler: {error}",

        "language_dialog.title": "Sprache der Oberfläche wählen",
        "language_dialog.subtitle": "Du kannst sie später in den Einstellungen ändern.",
        "language_dialog.footer": "Spaosi Voice Translator",

        "main.start": "START",
        "main.stop": "STOPP",
        "main.mode.realtime": "MODUS: REALTIME",
        "main.mode.video": "MODUS: VIDEO",
        "main.mode.realtime.tooltip": "Realtime: schnelle Übersetzung mit 14-Wort-Phrasenlimit",
        "main.mode.video.tooltip": "Videoübersetzung: 600 ms SYS-Pause und keine Teilung nach Wortlimit",
        "main.mic.idle": "MIC: {hotkey}",
        "main.mic.recording": "MIC: REC",
        "main.mic.tooltip": "Mikrofon-Hotkey: {hotkey}. Einmal drücken zum Aufnehmen, erneut drücken zum Übersetzen.",
        "main.log.interface_loaded": "Interface geladen",
        "main.log.sys_idle": "SYS läuft nicht: Systemaudio wird nicht aufgenommen",
        "main.log.video_enabled": "Videoübersetzungsmodus aktiviert: SYS-Pause 600 ms, Wortlimit deaktiviert",
        "main.log.hotkey_selected": "MIC-Hotkey ausgewählt: {hotkey}",
        "main.log.hotkey_registered": "MIC-Hotkey registriert: {hotkey}",

        "settings.title": "EINSTELLUNGEN",
        "settings.nav.general": "Allgemein",
        "settings.nav.widgets": "Widgets",
        "settings.nav.audio": "Audio",
        "settings.nav.keys": "Schlüssel",
        "settings.section.general": "ALLGEMEIN",
        "settings.section.widgets": "WIDGETS",
        "settings.section.audio": "AUDIO",
        "settings.section.keys": "SCHLÜSSEL",
        "settings.row.ui_language": "Sprache der Oberfläche",
        "settings.row.recognition_language": "Erkennungssprache",
        "settings.row.translation_language": "Übersetzungssprache",
        "settings.row.mode": "Modus",
        "settings.row.voice_hotkey": "Mikrofon-Hotkey",
        "settings.row.external_voices": "Externe Stimmen",
        "settings.row.microphone_translation": "Mikrofonübersetzung",
        "settings.row.obs_widget": "OBS-Widget",
        "settings.row.microphone": "Mikrofon",
        "settings.row.microphone_pause": "Mikrofonpause",
        "settings.row.system_audio": "Systemaudio",
        "settings.row.system_pause": "Audiopause",
        "settings.row.deepgram": "Deepgram",
        "settings.row.gemini": "Gemini",
        "settings.row.gemini_proxy": "Gemini proxy",
        "settings.video_translation_mode": "Videoübersetzung",
        "settings.video_translation_mode.tooltip": "Für Videoübersetzung: lässt lange Phrasen vollständig und setzt SYS-Pause auf 600 ms",
        "settings.external_voices": "Externe Stimmen",
        "settings.microphone": "Mikrofon",
        "settings.obs_copied": "Link in die Zwischenablage kopiert",
        "settings.obs_tooltip": "Klicken, um den Link zu kopieren",
        "settings.obs_size_hint": "OBS-Quellgröße: 1920×1080",
        "settings.hotkey_tooltip": "Klicke auf die Schaltfläche und drücke dann eine Taste oder Kombination",
        "settings.hotkey_capture": "TASTE DRÜCKEN...",
        "settings.hotkey_capture_tooltip": "Drücke die gewünschte Taste. Esc bricht ab.",
        "settings.hotkey_saved": "GESPEICHERT: ",
        "settings.deepgram_placeholder": "Deepgram API key",
        "settings.gemini_placeholder": "Gemini API key",
        "settings.gemini_proxy_placeholder": "Optional Gemini proxy URL",
        "settings.gemini_proxy_tooltip": "Optionaler Gemini-Proxy. Leer lassen, um die Gemini API direkt zu verwenden.",
        "settings.system_devices_not_found": "Keine Systemaudio-Geräte gefunden",
        "settings.microphones_not_found": "Keine Mikrofone gefunden",
        "settings.deepgram_tooltip": "{label} | Deepgram-Sprache={code}",
        "settings.translation_tooltip": "Übersetzen nach: {language}",
        "settings.obs_copied_log": "OBS: Link in die Zwischenablage kopiert: {url}",

        "audio.sys": "SYS",
        "audio.idle": "NICHT\nAKTIV",
        "audio.active": "AUFNAHME",
        "audio.off": "OFF",
        "audio.tooltip_idle": "SYS: nicht aktiv — Systemaudio wird nicht aufgenommen",
        "audio.tooltip_active": "SYS: Systemaudio wird aufgenommen",

        "logs.filter.incoming": "Eingehender Text",
        "logs.filter.translation": "Übersetzung",
        "logs.filter.system": "Systemlogs",
        "logs.filter.errors": "Fehler",

        "overlays.game.title": "ÜBERSETZUNG EXTERNER STIMMEN",
        "overlays.voice.title": "MIKROFONÜBERSETZUNG",
        "voice.waiting": "Warte auf Stimme",
        "voice.listening": "Höre zu",
        "voice.press_hotkey_again": "Drücke den Hotkey erneut zum Übersetzen",
        "voice.translation_ready": "Übersetzung bereit",
    },
}


class Translator:
    def __init__(self, settings: SettingsStore):
        self.settings = settings
        self._language_code = DEFAULT_UI_LANGUAGE

    def reload_from_settings(self) -> None:
        self._language_code = self._normalize_language(
            str(self.settings.get(UI_LANGUAGE_KEY, DEFAULT_UI_LANGUAGE) or DEFAULT_UI_LANGUAGE)
        )

    def language_code(self) -> str:
        return self._language_code

    def is_language_selected(self) -> bool:
        return bool(self.settings.get(UI_LANGUAGE_SELECTED_KEY, False))

    def set_language(self, language_code: str, *, mark_selected: bool = True) -> None:
        self._language_code = self._normalize_language(language_code)
        self.settings.set(UI_LANGUAGE_KEY, self._language_code)
        if mark_selected:
            self.settings.set(UI_LANGUAGE_SELECTED_KEY, True)

    def language_options(self) -> tuple[UiLanguage, ...]:
        return UI_LANGUAGES

    def t(self, key: str, **kwargs: Any) -> str:
        text = self._translation_table().get(key)
        if text is None:
            text = _TRANSLATIONS[FALLBACK_UI_LANGUAGE].get(key, key)

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text

        return text

    def _translation_table(self) -> dict[str, str]:
        if self._language_code in _TRANSLATIONS:
            return _TRANSLATIONS[self._language_code]

        return _TRANSLATIONS[FALLBACK_UI_LANGUAGE]

    def _normalize_language(self, language_code: str) -> str:
        clean = str(language_code or "").strip().lower()
        known = {language.code for language in UI_LANGUAGES}

        if clean in _TRANSLATIONS and clean in known:
            return clean

        return DEFAULT_UI_LANGUAGE
