#!/usr/bin/env python3
"""
Test Data Generator for TCO Automation

Generates synthetic but realistic vendor proposals for testing the comparison system.
Reads from the product ontology to ensure generated products will match.

Usage:
    # Simple - generate 5 vendors for a test client
    python generate_test_data.py --client "acme_bank" --vendors FIS,JACK_HENRY,CSI,FISERV,FINASTRA

    # Custom - specify items per vendor and gap rate
    python generate_test_data.py --client "test_bank" --vendors FIS,CSI --items 30 --gap-rate 0.2

    # Quick test - 3 vendors with defaults
    python generate_test_data.py --client "demo_bank" --vendors FIS,JACK_HENRY,CSI

Output:
    Creates JSON files in "Extracted JSON/" folder:
    - {client}_{vendor}_extraction_ai.json for each vendor
"""

import argparse
import json
import random
from datetime import datetime
from pathlib import Path

import yaml


# Cost ranges by category type (7-year totals)
COST_RANGES = {
    # Core systems - high cost
    'core': (500000, 2000000),
    # Digital banking - medium-high
    'digital': (200000, 800000),
    # Processing services - medium
    'processing': (100000, 500000),
    # Compliance/reporting - medium-low
    'compliance': (50000, 200000),
    # Implementation - one-time heavy
    'implementation': (100000, 400000),
    # Add-ons/optional - low
    'addon': (20000, 100000),
}

# Map categories to cost types
CATEGORY_COST_TYPE = {
    'core_banking_platform': 'core',
    'digital_banking_platform': 'digital',
    'mobile_banking': 'digital',
    'bill_pay': 'digital',
    'estatements': 'processing',
    'ach_processing': 'processing',
    'wire_transfer_business': 'processing',
    'wire_transfer_consumer': 'processing',
    'item_processing_suite': 'processing',
    'eft_debit_processing': 'processing',
    'debit_card_production': 'processing',
    'debit_card_network': 'processing',
    'treasury_management_suite': 'processing',
    'positive_pay': 'processing',
    'remote_deposit': 'processing',
    'lockbox_services': 'processing',
    'zelle_p2p': 'digital',
    'fednow': 'processing',
    'rtp_receive': 'processing',
    'rtp_send': 'processing',
    'fraud_detection': 'compliance',
    'fraud_analytics': 'compliance',
    'regulatory_compliance': 'compliance',
    'cra_compliance': 'compliance',
    'irs_reporting': 'compliance',
    'security_compliance': 'compliance',
    'network_security': 'compliance',
    'core_implementation': 'implementation',
    'data_migration': 'implementation',
    'training_services': 'implementation',
    'project_management': 'implementation',
    'hosting_services': 'core',
    'disaster_recovery': 'addon',
    'analytics_reporting': 'addon',
    'document_management': 'addon',
    'api_services': 'addon',
}


def load_ontology():
    """Load the product ontology YAML file."""
    ontology_path = Path(__file__).parent / 'ontology' / 'product_ontology.yaml'
    with open(ontology_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_vendor_products(ontology: dict, vendor: str) -> list:
    """
    Get all products available for a vendor from the ontology.

    Returns list of tuples: (category_key, product_name, canonical_name)
    """
    products = []
    categories = ontology.get('categories', {})

    for cat_key, cat_data in categories.items():
        vendor_terms = cat_data.get('vendor_terms', {})
        canonical_name = cat_data.get('canonical_name', cat_key)

        if vendor in vendor_terms and vendor_terms[vendor]:
            # Pick the first (most canonical) term for this vendor
            product_name = vendor_terms[vendor][0]
            products.append((cat_key, product_name, canonical_name))

    return products


def generate_cost(category_key: str, variation: float = 0.3) -> dict:
    """
    Generate realistic costs for a category.

    Args:
        category_key: The category to generate costs for
        variation: Random variation factor (0.3 = +/- 30%)

    Returns:
        Dict with monthly_fee, one_time_fee, total_7_year
    """
    cost_type = CATEGORY_COST_TYPE.get(category_key, 'addon')
    min_cost, max_cost = COST_RANGES[cost_type]

    # Base 7-year cost
    base_cost = random.uniform(min_cost, max_cost)

    # Apply variation
    variation_factor = 1 + random.uniform(-variation, variation)
    total_7_year = base_cost * variation_factor

    # Split into monthly vs one-time (roughly 80/20 for recurring)
    if cost_type == 'implementation':
        # Implementation is mostly one-time
        one_time_pct = random.uniform(0.6, 0.9)
    else:
        # Recurring services are mostly monthly
        one_time_pct = random.uniform(0.05, 0.25)

    one_time_fee = total_7_year * one_time_pct
    monthly_total = total_7_year - one_time_fee
    monthly_fee = monthly_total / 84  # 7 years * 12 months

    return {
        'monthly_fee': round(monthly_fee, 2),
        'one_time_fee': round(one_time_fee, 2),
        'total_7_year': round(total_7_year, 2)
    }


def generate_line_item(category_key: str, product_name: str, canonical_name: str) -> dict:
    """Generate a single line item for the extraction JSON."""
    costs = generate_cost(category_key)

    # Determine fee type based on costs
    if costs['one_time_fee'] > costs['monthly_fee'] * 12:
        fee_type = "One-Time"
    else:
        fee_type = "Monthly F"

    # Map to level 1 bucket
    bucket_mapping = {
        'core': 'Core Platform',
        'digital': 'Digital Banking',
        'processing': 'Processing Services',
        'compliance': 'Risk & Compliance',
        'implementation': 'Implementation',
        'addon': 'Optional Services',
    }
    cost_type = CATEGORY_COST_TYPE.get(category_key, 'addon')
    level_1_bucket = bucket_mapping.get(cost_type, 'Other')

    return {
        'solution_name': product_name,
        'fee_type': fee_type,
        'category': canonical_name,
        'monthly_fee': costs['monthly_fee'],
        'one_time_fee': costs['one_time_fee'],
        'per_unit_rate': 0.0,
        'unit_description': None,
        'optional': random.random() < 0.15,  # 15% chance of optional
        'third_party': random.random() < 0.1,  # 10% chance of third party
        'overall_confidence': round(random.uniform(0.88, 0.98), 2),
        'extraction_notes': f"Generated test data for {canonical_name}",
        'level_1_bucket': level_1_bucket,
        'total_7_year_cost': costs['total_7_year']
    }


def generate_vendor_extraction(
    client_name: str,
    vendor: str,
    ontology: dict,
    num_items: int = None,
    gap_rate: float = 0.1
) -> dict:
    """
    Generate a complete extraction JSON for a vendor.

    Args:
        client_name: Name of the client
        vendor: Vendor name (FIS, JACK_HENRY, etc.)
        ontology: Loaded ontology dict
        num_items: Number of items to generate (None = all available)
        gap_rate: Probability of skipping a category (creates gaps)

    Returns:
        Complete extraction JSON structure
    """
    # Get all available products for this vendor
    all_products = get_vendor_products(ontology, vendor)

    if num_items and num_items < len(all_products):
        # Randomly select subset
        products = random.sample(all_products, num_items)
    else:
        products = all_products

    # Apply gap rate - skip some categories randomly
    if gap_rate > 0:
        products = [p for p in products if random.random() > gap_rate]

    # Generate line items
    line_items = []
    for cat_key, product_name, canonical_name in products:
        item = generate_line_item(cat_key, product_name, canonical_name)
        line_items.append(item)

    # Calculate summary
    total_monthly_required = sum(
        item['monthly_fee'] for item in line_items if not item['optional']
    )
    total_monthly_optional = sum(
        item['monthly_fee'] for item in line_items if item['optional']
    )
    total_one_time = sum(item['one_time_fee'] for item in line_items)

    return {
        'vendor': vendor,
        'client': client_name.replace('_', ' ').title(),
        'proposal_type': 'Generated Test Proposal',
        'document_date': datetime.now().strftime('%Y-%m-%d'),
        'contract_term': 7,
        'line_items': line_items,
        'summary': {
            'total_monthly_required': round(total_monthly_required, 2),
            'total_monthly_optional': round(total_monthly_optional, 2),
            'total_one_time_fees': round(total_one_time, 2),
            'total_one_time_credits': 0,
            'items_extracted': len(line_items),
            'average_confidence': 0.93
        },
        'extraction_metadata': {
            'model': 'test_data_generator',
            'extraction_method': 'synthetic',
            'generated_at': datetime.now().isoformat(),
            'source_tables_processed': 0
        }
    }


def save_extraction(extraction: dict, client_name: str, vendor: str, output_dir: str = 'Extracted JSON'):
    """Save extraction to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    filename = f"{client_name.lower()}_{vendor.lower()}_extraction_ai.json"
    filepath = output_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(extraction, f, indent=2)

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic vendor proposals for testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 5-vendor comparison for Acme Bank
  python generate_test_data.py --client acme_bank --vendors FIS,JACK_HENRY,CSI,FISERV,FINASTRA

  # Quick 3-vendor test
  python generate_test_data.py --client demo_bank --vendors FIS,CSI,JACK_HENRY

  # Custom with 25 items per vendor and 20% gaps
  python generate_test_data.py --client test_bank --vendors FIS,CSI --items 25 --gap-rate 0.2
        """
    )

    parser.add_argument(
        '--client', '-c',
        required=True,
        help='Client name (e.g., acme_bank)'
    )
    parser.add_argument(
        '--vendors', '-v',
        required=True,
        help='Comma-separated vendor list (e.g., FIS,JACK_HENRY,CSI)'
    )
    parser.add_argument(
        '--items', '-i',
        type=int,
        default=None,
        help='Number of items per vendor (default: all available)'
    )
    parser.add_argument(
        '--gap-rate', '-g',
        type=float,
        default=0.1,
        help='Probability of gaps per category (default: 0.1)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='Extracted JSON',
        help='Output directory (default: "Extracted JSON")'
    )
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=None,
        help='Random seed for reproducibility'
    )

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)

    # Parse vendors
    vendors = [v.strip().upper() for v in args.vendors.split(',')]
    valid_vendors = ['FIS', 'JACK_HENRY', 'CSI', 'FISERV', 'FINASTRA']

    for vendor in vendors:
        if vendor not in valid_vendors:
            print(f"Warning: '{vendor}' not in valid vendors: {valid_vendors}")
            print("Continuing anyway...")

    # Load ontology
    print("Loading product ontology...")
    ontology = load_ontology()

    print()
    print("=" * 70)
    print("TEST DATA GENERATOR")
    print("=" * 70)
    print(f"Client: {args.client}")
    print(f"Vendors: {', '.join(vendors)}")
    print(f"Items per vendor: {args.items or 'all available'}")
    print(f"Gap rate: {args.gap_rate:.0%}")
    print()

    # Generate extractions
    generated_files = []

    for vendor in vendors:
        print(f"Generating {vendor} proposal...")

        extraction = generate_vendor_extraction(
            client_name=args.client,
            vendor=vendor,
            ontology=ontology,
            num_items=args.items,
            gap_rate=args.gap_rate
        )

        filepath = save_extraction(
            extraction=extraction,
            client_name=args.client,
            vendor=vendor,
            output_dir=args.output_dir
        )

        generated_files.append(filepath)

        # Summary
        num_items = len(extraction['line_items'])
        total_7yr = sum(item.get('total_7_year_cost', 0) for item in extraction['line_items'])
        print(f"  -> {filepath.name}: {num_items} items, ${total_7yr:,.0f} total")

    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"Generated {len(generated_files)} extraction files")
    print()
    print("To run comparison:")
    print(f"  python generate_comparison.py {args.client}")
    print()


if __name__ == '__main__':
    main()
