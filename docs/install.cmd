@chcp 65001
@echo off
setlocal enabledelayedexpansion
set "PYTHONUTF8=1" 

REM --- Script directory ---
pushd "%~dp0"

REM --- Virtual environment ---
set "VENV_DIR=%~dp0stp_server_editor_venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    python -m venv "%VENV_DIR%"
)
call "%VENV_DIR%\Scripts\activate"

echo Installing requirements...
python -m pip install  --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.org:443 --trusted-host files.pythonhosted.org:443 --upgrade pip setuptools wheel
echo.

echo Checking pip status...
python -m pip check
echo.

echo Clearing pip cache...
python -m pip cache purge
echo.

echo Installing project dependencies...
pip install  --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.org:443 --trusted-host files.pythonhosted.org:443 -r requirements.txt
echo.

echo Final pip check...
python -m pip check
echo.

echo Clearing pip cache after installation...
python -m pip cache purge
echo.

echo Final verification...
python -m pip check

echo Done.
pause