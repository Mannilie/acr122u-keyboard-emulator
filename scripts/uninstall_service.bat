@echo off
echo Uninstalling ACR122U Keyboard Emulator scheduled task...

:: Check for admin rights
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

:: Remove the scheduled task if it exists
echo Removing scheduled task...
schtasks /query /tn "ACR122U Keyboard Emulator" >nul 2>&1
if %errorLevel% equ 0 (
    schtasks /delete /tn "ACR122U Keyboard Emulator" /f
) else (
    echo Scheduled task not found.
)

:: Remove startup shortcut
echo Removing startup shortcut...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if exist "%STARTUP_FOLDER%\ACR122U Keyboard Emulator.lnk" (
    del "%STARTUP_FOLDER%\ACR122U Keyboard Emulator.lnk"
)

:: Kill any running instances
echo Stopping any running instances...
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq ACR122U Keyboard Emulator" >nul 2>&1

echo.
echo Please restart for the changes to take effect.
echo.

pause