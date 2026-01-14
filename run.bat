@echo off
REM TCO Automation - Quick Run Script
REM Activates virtual environment and runs Python commands

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run install_dependencies.bat first
    pause
    exit /b 1
)

REM Run Python command with venv
venv\Scripts\python %*
