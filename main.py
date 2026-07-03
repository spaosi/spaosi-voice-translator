from pathlib import Path
import sys

PROJECT_SRC = Path(__file__).resolve().parent / "src"
if PROJECT_SRC.exists():
    sys.path.insert(0, str(PROJECT_SRC))

from spaosi_voice_translator.app.bootstrap import run_app

if __name__ == "__main__":
    raise SystemExit(run_app())
