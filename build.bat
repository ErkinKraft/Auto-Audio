@echo off
cd /d "%~dp0"
echo === AutoAudio build ===
pip install pyinstaller --quiet
pyinstaller --clean AutoAudio.spec
if %ERRORLEVEL% NEQ 0 (
    echo BUILD FAILED
    pause
    exit /b 1
)
echo.
echo OK: dist\AutoAudio.exe
pause
