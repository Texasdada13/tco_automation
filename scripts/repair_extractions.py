#!/usr/bin/env python3
"""
Repair Extraction JSON Files

Fixes common issues in extraction JSON files:
- null contract_term -> default to 7 years
- null client -> derive from filename
- null numeric fields -> default to 0

Usage:
    python scripts/repair_extractions.py [--dry-run]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.vendor_config import extract_client_from_filename

# Configuration
DEFAULT_CONTRACT_TERM = 7
EXTRACTED_JSON_DIR = Path(__file__).parent.parent / "Extracted JSON"


def repair_extraction(filepath: Path, dry_run: bool = False) -> dict:
    """
    Repair a single extraction file.

    Returns dict with repair info.
    """
    repairs = {
        'file': filepath.name,
        'changes': [],
        'success': False
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_data = json.dumps(data)

        # Fix contract_term
        if data.get('contract_term') is None:
            data['contract_term'] = DEFAULT_CONTRACT_TERM
            repairs['changes'].append(f'contract_term: null -> {DEFAULT_CONTRACT_TERM}')

        # Fix client name
        client = data.get('client')
        if client is None or client == 'Not specified' or client == 'Unknown':
            new_client = extract_client_from_filename(filepath.name)
            data['client'] = new_client
            repairs['changes'].append(f'client: {client} -> {new_client}')

        # Fix line items with null values
        for i, item in enumerate(data.get('line_items', [])):
            # Fix numeric fields
            for field in ['monthly_fee', 'one_time_fee', 'per_unit_rate']:
                if item.get(field) is None:
                    item[field] = 0.0
                    repairs['changes'].append(f'line_items[{i}].{field}: null -> 0.0')

            # Fix confidence score
            if item.get('overall_confidence') is None:
                item['overall_confidence'] = 0.5
                repairs['changes'].append(f'line_items[{i}].overall_confidence: null -> 0.5')

        # Only write if changes were made
        if repairs['changes']:
            if not dry_run:
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

    if dry_run:
        print("=" * 60)
        print("DRY RUN - No files will be modified")
        print("=" * 60)

    print(f"\nScanning {EXTRACTED_JSON_DIR}...\n")

    if not EXTRACTED_JSON_DIR.exists():
        print(f"ERROR: Directory not found: {EXTRACTED_JSON_DIR}")
        sys.exit(1)

    files = list(EXTRACTED_JSON_DIR.glob("*_extraction_ai.json"))
    print(f"Found {len(files)} extraction files\n")

    repaired = 0
    errors = 0

    for filepath in sorted(files):
        result = repair_extraction(filepath, dry_run)

        if result.get('error'):
            print(f"ERROR: {result['file']}")
            print(f"       {result['error']}")
            errors += 1
        elif result['changes'] and result['changes'][0] != 'No repairs needed':
            print(f"REPAIRED: {result['file']}")
            for change in result['changes']:
                print(f"  - {change}")
            if not dry_run and 'backup' in result:
                print(f"  Backup: {result['backup']}")
            repaired += 1
        else:
            print(f"OK: {result['file']}")

    print("\n" + "=" * 60)
    print(f"Summary: {repaired} repaired, {errors} errors, {len(files) - repaired - errors} unchanged")

    if dry_run and repaired > 0:
        print("\nRun without --dry-run to apply repairs")


if __name__ == '__main__':
    main()
