@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"
title Spaosi Voice Translator - EXE build

if not exist logs mkdir logs
set "LOG=logs\build_exe.log"
set "TOTAL=9"

echo ================================================== > "%LOG%"
echo Spaosi Voice Translator EXE build >> "%LOG%"
echo Time: %DATE% %TIME% >> "%LOG%"
echo Project: %CD% >> "%LOG%"
echo ================================================== >> "%LOG%"
echo. >> "%LOG%"

cls
echo ==================================================
echo   Spaosi Voice Translator - EXE build
echo ==================================================
echo.
echo Project:
echo %CD%
echo.
echo Log:
echo %CD%\%LOG%
echo.

call :step 1 "Searching for Python 3.10+"
call :find_python
if "%PY_CMD%"=="" goto no_python

echo Found: %PY_CMD%
echo Found Python command: %PY_CMD% >> "%LOG%"
%PY_CMD% -c "import sys; print('Python version:', sys.version)"
%PY_CMD% -c "import sys; print('Python version:', sys.version)" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
echo.

call :step 2 "Creating build virtual environment"
if not exist ".venv-build\Scripts\python.exe" (
    echo Creating .venv-build...
    echo Creating .venv-build... >> "%LOG%"
    %PY_CMD% -m venv .venv-build
    if errorlevel 1 goto fail
) else (
    echo .venv-build already exists
    echo .venv-build already exists >> "%LOG%"
)
echo.

call :step 3 "Activating build environment"
call ".venv-build\Scripts\activate.bat"
if errorlevel 1 goto fail
python --version
python --version >> "%LOG%" 2>&1
echo.

call :step 4 "Upgrading pip"
echo Running: python -m pip install --upgrade pip
echo Running: python -m pip install --upgrade pip >> "%LOG%"
python -m pip install --upgrade pip
if errorlevel 1 goto fail
echo.

call :step 5 "Installing project dependencies"
echo Running: python -m pip install -e .
echo Running: python -m pip install -e . >> "%LOG%"
python -m pip install -e .
if errorlevel 1 goto fail

echo Running: python -m pip install pyinstaller
echo Running: python -m pip install pyinstaller >> "%LOG%"
python -m pip install pyinstaller
if errorlevel 1 goto fail
echo.

call :step 6 "Cleaning old build folders"
if exist build (
    echo Removing build\
    echo Removing build\ >> "%LOG%"
    rmdir /s /q build
)
if exist dist (
    echo Removing dist\
    echo Removing dist\ >> "%LOG%"
    rmdir /s /q dist
)
echo Clean done
echo Clean done >> "%LOG%"
echo.

call :step 7 "Preparing icon"
set "ICON_ARG="
if exist icon.ico (
    set "ICON_ARG=--icon icon.ico"
    echo Icon: icon.ico
    echo Icon: icon.ico >> "%LOG%"
) else if exist icon.png (
    set "ICON_ARG=--icon icon.png"
    echo Icon: icon.png
    echo Icon: icon.png >> "%LOG%"
) else (
    echo Icon: not found, building without custom icon
    echo Icon: not found, building without custom icon >> "%LOG%"
)
echo.

call :step 8 "Building EXE with PyInstaller"
if not exist main.py (
    echo ERROR: main.py does not exist.
    echo ERROR: main.py does not exist. >> "%LOG%"
    goto fail
)

echo PyInstaller output will be shown below.
echo.
echo --------------------------------------------------
echo.

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --log-level INFO ^
  --name "Spaosi Voice Translator" ^
  %ICON_ARG% ^
  main.py

set "BUILD_EXIT=%ERRORLEVEL%"
echo PyInstaller exit code: %BUILD_EXIT% >> "%LOG%"

if not "%BUILD_EXIT%"=="0" goto fail

echo.
echo --------------------------------------------------
echo.

call :step 9 "Checking final EXE"
set "EXE_PATH=%CD%\dist\Spaosi Voice Translator\Spaosi Voice Translator.exe"

if not exist "%EXE_PATH%" (
    echo ERROR: EXE was not created.
    echo ERROR: EXE was not created. >> "%LOG%"
    goto fail
)

echo EXE created successfully.
echo EXE created successfully. >> "%LOG%"
echo.
echo ==================================================
echo BUILD DONE
echo ==================================================
echo.
echo EXE file:
echo %EXE_PATH%
echo.
echo Folder to send/copy:
echo %CD%\dist\Spaosi Voice Translator
echo.
echo Important:
echo Send the whole folder, not only the exe file.
echo.
call :wait_close
exit /b 0

:step
echo --------------------------------------------------
echo [%~1/%TOTAL%] %~2
echo --------------------------------------------------
echo [%~1/%TOTAL%] %~2 >> "%LOG%"
exit /b 0

:find_python
set "PY_CMD="

for %%V in (3.13 3.12 3.11 3.10) do (
    if "!PY_CMD!"=="" (
        py -%%V -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
        if not errorlevel 1 (
            set "PY_CMD=py -%%V"
        )
    )
)

if not "%PY_CMD%"=="" exit /b 0

where python >nul 2>nul
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=python"
    )
)

exit /b 0

:no_python
echo ERROR: Python 3.10+ was not found.
echo ERROR: Python 3.10+ was not found. >> "%LOG%"
echo.
echo Installed Python launchers:
py -0p
echo.
echo Install Python 3.10+ and run this file again.
echo.
call :wait_close
exit /b 1

:fail
echo.
echo ==================================================
echo BUILD FAILED
echo ==================================================
echo.
echo Log file:
echo %CD%\%LOG%
echo.
echo Common checks:
echo - main.py exists
echo - pyproject.toml allows your Python version
echo - internet is available for pip install
echo - antivirus did not block PyInstaller
echo.
echo Last log lines:
echo --------------------------------------------------
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path '%LOG%') { Get-Content '%LOG%' -Tail 120 }"
echo --------------------------------------------------
echo.
call :wait_close
exit /b 1

:wait_close
echo.
set /p "_CLOSE_PROMPT=Press Enter to close this window..."
exit /b 0
