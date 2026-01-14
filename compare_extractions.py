"""
Compare Extraction Results
Compares different extraction methods for the same proposal.

Usage:
    python compare_extractions.py <vendor_name>

Example:
    python compare_extractions.py fsb
"""

import sys
import json
from pathlib import Path
from extraction_config import EXTRACTED_JSON_DIR


def load_extraction(file_path):
    """Load extraction JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None


def analyze_extraction(data, method_name):
    """Analyze extraction quality."""
    if not data:
        return {
            'method': method_name,
            'status': 'NOT FOUND',
            'line_items': 0,
            'categories': 0,
            'total_monthly': 0,
            'total_onetime': 0,
            'avg_confidence': 0,
            'has_details': False
        }

    line_items = data.get('line_items', [])

    # Count unique categories
    categories = set()
    total_monthly = 0
    total_onetime = 0
    confidences = []
    has_per_unit_rates = 0
    has_graduated = 0

    for item in line_items:
        category = item.get('category', 'Unknown')
        categories.add(category)

        monthly = item.get('monthly_fee', 0) or item.get('proposed_monthly_fee', 0) or 0
        onetime = item.get('one_time_fee', 0) or 0

        total_monthly += monthly
        total_onetime += onetime

        if item.get('overall_confidence'):
            confidences.append(item['overall_confidence'])

        if item.get('per_unit_rate', 0) > 0:
            has_per_unit_rates += 1

        if item.get('graduated_pricing'):
            has_graduated += 1

    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    # Check for detailed extraction
    has_details = any([
        item.get('volume', 0) > 0,
        item.get('per_unit_rate', 0) > 0,
        item.get('graduated_pricing'),
        item.get('page_number'),
    ] for item in line_items)

    return {
        'method': method_name,
        'status': 'FOUND',
        'line_items': len(line_items),
        'categories': len(categories),
        'total_monthly': total_monthly,
        'total_onetime': total_onetime,
        'avg_confidence': avg_confidence,
        'has_details': has_details,
        'has_per_unit_rates': has_per_unit_rates,
        'has_graduated_pricing': has_graduated,
        'client': data.get('client', 'Unknown'),
        'vendor': data.get('vendor', 'Unknown')
    }


def compare_extractions(vendor_name):
    """Compare all extraction methods for a vendor."""

    print('='*80)
    print(f'EXTRACTION COMPARISON: {vendor_name.upper()}')
    print('='*80)
    print()

    # Find all extraction files for this vendor
    vendor_lower = vendor_name.lower().replace(' ', '_')

    extractions = {
        'Current (2-step AI)': EXTRACTED_JSON_DIR / f"{vendor_lower}_extraction_ai.json",
        'Current (Raw)': EXTRACTED_JSON_DIR / f"{vendor_lower}_raw_extraction.json",
        'Direct PDF': EXTRACTED_JSON_DIR / f"{vendor_lower}_extraction_direct.json",
        'Hybrid (PDF+Vision)': EXTRACTED_JSON_DIR / f"{vendor_lower}_extraction_hybrid.json",
    }

    # Also check for files with full name prefix
    for file in EXTRACTED_JSON_DIR.glob("*.json"):
        if file.stem.startswith('_') and vendor_lower in file.stem.lower():
            extractions[f'Legacy: {file.stem}'] = file

    results = []

    for method_name, file_path in extractions.items():
        if file_path.exists():
            data = load_extraction(file_path)
            analysis = analyze_extraction(data, method_name)
            analysis['file'] = file_path.name
            results.append(analysis)

    if not results:
        print(f"❌ No extraction files found for vendor: {vendor_name}")
        print(f"\nSearched in: {EXTRACTED_JSON_DIR}")
        print(f"\nAvailable files:")
        for f in sorted(EXTRACTED_JSON_DIR.glob("*.json")):
            print(f"  - {f.name}")
        return

    # Print comparison table
    print("COMPARISON RESULTS")
    print("-" * 80)
    print()

    # Header
    print(f"{'Method':<25} {'Items':<8} {'Categories':<12} {'Monthly $':<15} {'One-Time $':<15} {'Details':<10}")
    print("-" * 80)

    # Sort by line items (descending)
    results.sort(key=lambda x: x['line_items'], reverse=True)

    for r in results:
        if r['status'] == 'FOUND':
            details = '✅' if r['has_details'] else '❌'
            print(f"{r['method']:<25} {r['line_items']:<8} {r['categories']:<12} ${r['total_monthly']:<14,.2f} ${r['total_onetime']:<14,.2f} {details:<10}")

    print("-" * 80)
    print()

    # Detailed analysis
    print("DETAILED ANALYSIS")
    print("-" * 80)

    for r in results:
        if r['status'] == 'FOUND':
            print(f"\n{r['method']}:")
            print(f"  File: {r['file']}")
            print(f"  Client: {r.get('client', 'Unknown')}")
            print(f"  Vendor: {r.get('vendor', 'Unknown')}")
            print(f"  Line Items: {r['line_items']}")
            print(f"  Categories: {r['categories']}")
            print(f"  Total Monthly: ${r['total_monthly']:,.2f}")
            print(f"  Total One-Time: ${r['total_onetime']:,.2f}")
            if r['avg_confidence'] > 0:
                print(f"  Avg Confidence: {r['avg_confidence']:.1%}")
            print(f"  Has Per-Unit Rates: {r['has_per_unit_rates']} items")
            print(f"  Has Graduated Pricing: {r['has_graduated_pricing']} items")
            print(f"  Has Detailed Data: {'✅ Yes' if r['has_details'] else '❌ No'}")

    print()
    print("-" * 80)

    # Recommendations
    print("\nRECOMMENDATIONS")
    print("-" * 80)

    best_method = max(results, key=lambda x: (x['line_items'], x['has_details']))

    print(f"\n🏆 Best Result: {best_method['method']}")
    print(f"   - {best_method['line_items']} line items extracted")
    print(f"   - {best_method['categories']} categories identified")
    print(f"   - {'Detailed' if best_method['has_details'] else 'Basic'} extraction")

    if best_method['line_items'] < 30:
        print("\n⚠️  WARNING: Low line item count detected!")
        print("   Consider trying:")
        print("   1. Direct PDF extraction (if not already tried)")
        print("   2. Hybrid PDF+Vision extraction for maximum accuracy")
        print("\n   Commands:")
        print(f"   python extract_proposal_direct.py <pdf_file> {vendor_name}")
        print(f"   python extract_proposal_hybrid.py <pdf_file> {vendor_name}")

    print()
    print('='*80)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python compare_extractions.py <vendor_name>")
        print()
        print("Example:")
        print("  python compare_extractions.py fsb")
        print("  python compare_extractions.py fis")
        print("  python compare_extractions.py csi")
        sys.exit(1)

    vendor_name = sys.argv[1]
    compare_extractions(vendor_name)
