@echo off
REM TCO Automation - Dependency Installation Script
REM This script installs all required Python packages for the TCO automation system

echo ================================================================================
echo TCO AUTOMATION - DEPENDENCY INSTALLATION
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo.
    pause
    exit /b 1
)

echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/4] Installing all dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo [4/4] Verifying installation...
echo.

python -c "import anthropic; print('✓ anthropic:', anthropic.__version__)"
python -c "import openpyxl; print('✓ openpyxl:', openpyxl.__version__)"
python -c "import pandas; print('✓ pandas:', pandas.__version__)"
python -c "import docx; print('✓ python-docx:', docx.__version__)"
python -c "import pdfplumber; print('✓ pdfplumber:', pdfplumber.__version__)"
python -c "import fitz; print('✓ PyMuPDF:', fitz.__version__)"
python -c "from PIL import Image; print('✓ Pillow: Installed')"

echo.
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo.
echo All dependencies have been successfully installed!
echo You can now run the TCO automation pipeline.
echo.
echo Quick Start:
echo   Step 1: python extract_proposal.py "input_file" "vendor_name"
echo   Step 2: python scripts/json_to_excel_mapper.py "Extracted JSON/vendor_extraction_ai.json"
echo.
echo Or use single command:
echo   python run_tco_pipeline.py "input_file" "vendor_name"
echo.
pause
