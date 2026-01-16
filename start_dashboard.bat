@echo off
echo Starting TCO Dashboard...
echo.

cd /d "%~dp0"

REM Start the Flask server in the background
start /B python web_dashboard\app.py

REM Wait a moment for the server to start
timeout /t 2 /nobreak >nul

REM Open the browser
start http://127.0.0.1:5847

echo Dashboard is running at http://127.0.0.1:5847
echo Press Ctrl+C to stop the server.
echo.

REM Keep the window open and show server output
python web_dashboard\app.py
