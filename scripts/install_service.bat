@echo off
echo ACR122U Keyboard Emulator Installation
echo =====================================

echo.
echo Installing as a Scheduled Task...
echo.

:: Check for admin rights (still needed for scheduled tasks)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Administrator privileges required.
    echo Please right-click on this script and select "Run as administrator".
    pause
    exit /b 1
)

:: Get the script directory
set SCRIPT_DIR=%~dp0
set PARENT_DIR=%SCRIPT_DIR%..
cd /d "%PARENT_DIR%"

echo Current directory: %CD%

:: Create a Python virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo Failed to create virtual environment. Make sure Python is installed correctly.
        pause
        exit /b 1
    )
)

:: Activate the virtual environment and install dependencies
echo Installing dependencies...
call "venv\Scripts\activate.bat"
pip install -r requirements.txt

:: Create logs directory
mkdir logs 2>nul

:: Create the run script
echo Creating startup script...
echo @echo off > run_emulator.bat
echo cd /d "%CD%" >> run_emulator.bat
echo venv\Scripts\pythonw.exe main.py >> run_emulator.bat

:: Get the current username
for /f "tokens=*" %%a in ('whoami') do set CURRENT_USER=%%a

:: Get full paths
set SCRIPT_PATH=%CD%\run_emulator.bat
set LOGS_PATH=%CD%\logs

echo Script path: %SCRIPT_PATH%
echo Logs path: %LOGS_PATH%
echo Current user: %CURRENT_USER%

:: Remove existing task if it exists
echo Checking for existing task...
schtasks /query /tn "ACR122U Keyboard Emulator" >nul 2>&1
if %errorLevel% equ 0 (
    echo Removing existing task...
    schtasks /delete /tn "ACR122U Keyboard Emulator" /f
)

:: Create the scheduled task
echo Creating scheduled task...
schtasks /create /tn "ACR122U Keyboard Emulator" /tr "\"%SCRIPT_PATH%\"" /sc onlogon /ru "%CURRENT_USER%" /rl highest /f
if %errorLevel% neq 0 (
    echo Failed to create scheduled task.
    pause
    exit /b 1
)

:: Also create a startup folder shortcut for redundancy
echo Creating startup folder shortcut...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if not exist "%STARTUP_FOLDER%" mkdir "%STARTUP_FOLDER%"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\ACR122U Keyboard Emulator.lnk'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Save()"

:: Run the emulator now
echo Starting the emulator...
start "" "%SCRIPT_PATH%"

echo.
echo ACR122U Keyboard Emulator has been installed as a scheduled task.
echo It will start automatically when you log in.
echo.
echo The emulator has also been started for the current session.
echo.
echo To uninstall, run: scripts\uninstall_task.bat
echo.

pause
exit /b 0