#!/usr/bin/env python3
"""
Repair Extraction JSON Files

Uses the centralized extraction_validator to fix common issues:
- null contract_term -> default to 7 years
- null client -> derive from filename
- null numeric fields -> default to 0
- invalid fee types -> normalize
- missing confidence scores -> default to 0.5

Usage:
    python scripts/repair_extractions.py [--dry-run] [--validate-only]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.vendor_config import extract_client_from_filename
from core.extraction_validator import validate_extraction, get_validation_summary

# Configuration
EXTRACTED_JSON_DIR = Path(__file__).parent.parent / "Extracted JSON"


def repair_extraction(filepath: Path, dry_run: bool = False, validate_only: bool = False) -> dict:
    """
    Repair a single extraction file using centralized validator.

    Returns dict with repair info.
    """
    repairs = {
        'file': filepath.name,
        'changes': [],
        'warnings': [],
        'success': False
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_data = json.dumps(data)

        # Fix client name before validation (needs filename context)
        client = data.get('client')
        if client is None or client in ['Not specified', 'Unknown']:
            new_client = extract_client_from_filename(filepath.name)
            data['client'] = new_client
            repairs['changes'].append(f'client: {client} -> {new_client}')

        # Use centralized validator with auto-fix
        result = validate_extraction(data, auto_fix=not validate_only, strict=False)

        # Collect changes from validator
        repairs['changes'].extend(result.auto_fixed)
        repairs['warnings'].extend(result.warnings)

        if not result.is_valid:
            repairs['error'] = '; '.join(result.errors)
            return repairs

        # Only write if changes were made
        if repairs['changes']:
            if not dry_run and not validate_only:
                # Backup original
                backup_path = filepath.with_suffix('.json.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_data)

                # Write repaired file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                repairs['backup'] = str(backup_path)

            repairs['success'] = True
        else:
            repairs['success'] = True
            repairs['changes'].append('No repairs needed')

        return repairs

    except Exception as e:
        repairs['error'] = str(e)
        return repairs


def main():
    dry_run = '--dry-run' in sys.argv
    validate_only = '--validate-only' in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No files will be modified")
        print("=" * 60)
    elif validate_only:
        print("=" * 60)
        print("VALIDATE ONLY - Checking files without modifications")
        print("=" * 60)

    print(f"\nScanning {EXTRACTED_JSON_DIR}...\n")

    if not EXTRACTED_JSON_DIR.exists():
        print(f"ERROR: Directory not found: {EXTRACTED_JSON_DIR}")
        sys.exit(1)

    files = list(EXTRACTED_JSON_DIR.glob("*_extraction_ai.json"))
    print(f"Found {len(files)} extraction files\n")

    repaired = 0
    warnings_count = 0
    errors = 0

    for filepath in sorted(files):
        result = repair_extraction(filepath, dry_run, validate_only)

        if result.get('error'):
            print(f"ERROR: {result['file']}")
            print(f"       {result['error']}")
            errors += 1
        elif result['changes'] and result['changes'][0] != 'No repairs needed':
            print(f"REPAIRED: {result['file']}")
            for change in result['changes']:
                print(f"  - {change}")
            if result.get('warnings'):
                for warning in result['warnings']:
                    print(f"  WARNING: {warning}")
            if not dry_run and not validate_only and 'backup' in result:
                print(f"  Backup: {result['backup']}")
            repaired += 1
        else:
            if result.get('warnings'):
                print(f"OK (with warnings): {result['file']}")
                for warning in result['warnings']:
                    print(f"  WARNING: {warning}")
                warnings_count += 1
            else:
                print(f"OK: {result['file']}")

    print("\n" + "=" * 60)
    print(f"Summary: {repaired} repaired, {warnings_count} with warnings, {errors} errors, {len(files) - repaired - errors - warnings_count} clean")

    if (dry_run or validate_only) and repaired > 0:
        print("\nRun without --dry-run or --validate-only to apply repairs")


if __name__ == '__main__':
    main()
