@echo off
setlocal
title SeCuReDmE LVFM Bootstrap

set "SCRIPT_DIR=%~dp0"
for %%i in ("%SCRIPT_DIR%..\") do set "REPO_ROOT=%%~fi"
set "LOG_DIR=%REPO_ROOT%output"
set "LOG_PATH=%LOG_DIR%\lvfm_bootstrap_watch.log"

if not exist "%REPO_ROOT%\scripts\lvfm_windows_bootstrap.py" (
    echo [SeCuReDmE LVFM] ERROR: launcher script missing at %REPO_ROOT%\scripts\lvfm_windows_bootstrap.py
    echo Press any key to close.
    pause
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
cd /d "%REPO_ROOT%"

set "PYTHON="
if defined PYTHON_HOME set "PYTHON=%PYTHON_HOME%\python.exe"
if not defined PYTHON if exist "%REPO_ROOT%venv\Scripts\python.exe" set "PYTHON=%REPO_ROOT%venv\Scripts\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if not defined PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
if not defined PYTHON set "PYTHON=python"

if "%PYTHON%"=="python" where python >nul 2>nul
if errorlevel 1 (
    echo [SeCuReDmE LVFM] ERROR: python not found.
    echo Press any key to close.
    pause
    exit /b 1
)

echo [SeCuReDmE LVFM] launcher=%~f0
echo [SeCuReDmE LVFM] repository=%REPO_ROOT%
echo [SeCuReDmE LVFM] logfile=%LOG_PATH%
echo.
"%PYTHON%" scripts\lvfm_windows_bootstrap.py --api-base http://127.0.0.1:8000 --publish-registry --output-path "%LOG_PATH%" --run-once
echo [SeCuReDmE LVFM] exit_code=%errorlevel%
pause
endlocal
