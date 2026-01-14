"""
Single-Command TCO Pipeline
Runs complete extraction → Excel generation pipeline in one command

Usage:
    python run_tco_pipeline.py <input_file> <vendor_name>

Example:
    python run_tco_pipeline.py "proposal.pdf" "csi"
    python run_tco_pipeline.py "WORKBOOK1.xlsx" "liberty"
"""

import sys
import subprocess
from pathlib import Path


def run_pipeline(input_file: str, vendor_name: str):
    """
    Execute complete TCO pipeline:
    1. Extract proposal data to JSON
    2. Generate Excel TCO report from JSON
    """
    print("=" * 80)
    print("TCO AUTOMATION PIPELINE - SINGLE COMMAND MODE")
    print("=" * 80)
    print(f"Input file: {input_file}")
    print(f"Vendor: {vendor_name}")
    print()

    # Validate input file exists
    if not Path(input_file).exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Step 1: Extract proposal data
    print("STEP 1: Extracting proposal data...")
    print("-" * 80)

    extraction_cmd = [sys.executable, "extract_proposal.py", input_file, vendor_name]
    result = subprocess.run(extraction_cmd, capture_output=False)

    if result.returncode != 0:
        print(f"\nERROR: Extraction failed with exit code {result.returncode}")
        sys.exit(1)

    print()
    print("[OK] Extraction completed successfully")
    print()

    # Step 2: Generate Excel TCO report
    print("STEP 2: Generating Excel TCO report...")
    print("-" * 80)

    # Determine JSON file path (using AI-enhanced version)
    json_file = f"Extracted JSON/{vendor_name}_extraction_ai.json"

    if not Path(json_file).exists():
        # Try alternative naming convention
        json_file = f"Extracted JSON/{vendor_name.lower().replace(' ', '_')}_extraction_ai.json"

    if not Path(json_file).exists():
        print(f"\nERROR: Expected JSON file not found: {json_file}")
        print("Extraction may have failed or used different naming.")
        sys.exit(1)

    excel_cmd = [sys.executable, "scripts/json_to_excel_mapper.py", json_file]
    result = subprocess.run(excel_cmd, capture_output=False)

    if result.returncode != 0:
        print(f"\nERROR: Excel generation failed with exit code {result.returncode}")
        sys.exit(1)

    print()
    print("[OK] Excel generation completed successfully")
    print()

    # Summary
    print("=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Extracted JSON: {json_file}")
    print(f"TCO Excel: TCO Output/{vendor_name.upper()}_TCO_New_*.xlsx")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_tco_pipeline.py <input_file> <vendor_name>")
        print()
        print("Examples:")
        print("  python run_tco_pipeline.py 'proposal.pdf' 'csi'")
        print("  python run_tco_pipeline.py 'WORKBOOK1.xlsx' 'liberty'")
        print("  python run_tco_pipeline.py 'deal_sheet.xlsx' 'jh'")
        print()
        print("Vendor names: fis, jh, csi, liberty")
        sys.exit(1)

    input_file = sys.argv[1]
    vendor_name = sys.argv[2]

    run_pipeline(input_file, vendor_name)
