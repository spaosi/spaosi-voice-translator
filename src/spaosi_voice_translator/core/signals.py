from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    log_line = pyqtSignal(str)
    app_ready = pyqtSignal()
    request_quit = pyqtSignal()
    language_changed = pyqtSignal(str)
