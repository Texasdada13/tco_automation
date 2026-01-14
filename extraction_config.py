"""
Extraction Configuration

Centralized configuration for data extraction pipeline.
All extraction outputs should follow these paths.

HARDCODED RULES:
1. All extraction JSON files → "Extracted JSON/" folder
2. All TCO Excel outputs → "TCO Output/" folder
"""

import os
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).parent

# Output directories
EXTRACTED_JSON_DIR = BASE_DIR / "Extracted JSON"
TCO_OUTPUT_DIR = BASE_DIR / "TCO Output"

# Ensure directories exist
EXTRACTED_JSON_DIR.mkdir(exist_ok=True)
TCO_OUTPUT_DIR.mkdir(exist_ok=True)


def get_extraction_output_path(vendor_name, extraction_type='raw'):
    """
    Get the standardized output path for extraction files.

    Args:
        vendor_name: Name of vendor (e.g., 'fis', 'liberty', 'csi', 'jh')
        extraction_type: Type of extraction - 'raw' or 'ai'

    Returns:
        Path object for the output file

    Example:
        >>> get_extraction_output_path('csi', 'raw')
        Path('Extracted JSON/csi_raw_extraction.json')
    """
    vendor_name = vendor_name.lower().replace(' ', '_')

    if extraction_type == 'raw':
        filename = f"{vendor_name}_raw_extraction.json"
    elif extraction_type == 'ai':
        filename = f"{vendor_name}_extraction_ai.json"
    else:
        filename = f"{vendor_name}_extraction_{extraction_type}.json"

    return EXTRACTED_JSON_DIR / filename


def get_all_extracted_files():
    """
    Get list of all extracted JSON files.

    Returns:
        List of Path objects
    """
    if not EXTRACTED_JSON_DIR.exists():
        return []

    return list(EXTRACTED_JSON_DIR.glob("*.json"))


def list_extractions():
    """Print all available extraction files."""
    files = get_all_extracted_files()

    if not files:
        print("No extraction files found.")
        return

    print(f"\nExtracted JSON files in '{EXTRACTED_JSON_DIR}':")
    print("=" * 60)

    for file_path in sorted(files):
        file_size = file_path.stat().st_size
        print(f"  {file_path.name:<40} ({file_size:>8,} bytes)")

    print("=" * 60)
    print(f"Total files: {len(files)}")


def get_tco_output_path(vendor_name, version='v1', add_timestamp=False):
    """
    Get the standardized output path for TCO Excel files.

    Args:
        vendor_name: Name of vendor (e.g., 'fis', 'liberty', 'csi', 'jh')
        version: Version identifier (e.g., 'v1', 'v2', 'final')
        add_timestamp: If True, add timestamp to filename

    Returns:
        Path object for the output file

    Example:
        >>> get_tco_output_path('csi', 'v1')
        Path('TCO Output/CSI_TCO_Output_v1.xlsx')
    """
    vendor_name_clean = vendor_name.replace(' ', '_').title()

    if add_timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{vendor_name_clean}_TCO_Output_{version}_{timestamp}.xlsx"
    else:
        filename = f"{vendor_name_clean}_TCO_Output_{version}.xlsx"

    return TCO_OUTPUT_DIR / filename


def get_all_tco_outputs():
    """
    Get list of all TCO output Excel files.

    Returns:
        List of Path objects
    """
    if not TCO_OUTPUT_DIR.exists():
        return []

    return list(TCO_OUTPUT_DIR.glob("*.xlsx"))


def list_tco_outputs():
    """Print all available TCO output files."""
    files = get_all_tco_outputs()

    if not files:
        print("No TCO output files found.")
        return

    print(f"\nTCO Output Excel files in '{TCO_OUTPUT_DIR}':")
    print("=" * 60)

    for file_path in sorted(files):
        file_size = file_path.stat().st_size
        modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f"  {file_path.name:<40} ({file_size:>8,} bytes) - {modified.strftime('%Y-%m-%d %H:%M')}")

    print("=" * 60)
    print(f"Total files: {len(files)}")


# HARDCODED RULES:
# 1. All extraction JSON files MUST be saved to EXTRACTED_JSON_DIR
#    - Raw extractions (vendor_raw_extraction.json)
#    - AI-enhanced extractions (vendor_extraction_ai.json)
#    - Any intermediate extraction files
#
# 2. All TCO Excel output files MUST be saved to TCO_OUTPUT_DIR
#    - Format: {Vendor}_TCO_Output_{version}.xlsx
#    - Example: CSI_TCO_Output_v1.xlsx


if __name__ == "__main__":
    # Test the configuration
    print("Extraction & Output Configuration")
    print("=" * 60)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Extracted JSON Directory: {EXTRACTED_JSON_DIR}")
    print(f"TCO Output Directory: {TCO_OUTPUT_DIR}")
    print(f"Directories exist: JSON={EXTRACTED_JSON_DIR.exists()}, Excel={TCO_OUTPUT_DIR.exists()}")
    print()

    # Example JSON extraction paths
    print("Example JSON extraction paths:")
    print(f"  CSI raw: {get_extraction_output_path('csi', 'raw')}")
    print(f"  CSI AI: {get_extraction_output_path('csi', 'ai')}")
    print(f"  Liberty raw: {get_extraction_output_path('liberty', 'raw')}")
    print(f"  Liberty AI: {get_extraction_output_path('liberty', 'ai')}")
    print()

    # Example TCO output paths
    print("Example TCO output paths:")
    print(f"  CSI v1: {get_tco_output_path('csi', 'v1')}")
    print(f"  Liberty v1: {get_tco_output_path('liberty', 'v1')}")
    print(f"  FIS final: {get_tco_output_path('fis', 'final')}")
    print()

    # List all files
    list_extractions()
    print()
    list_tco_outputs()
