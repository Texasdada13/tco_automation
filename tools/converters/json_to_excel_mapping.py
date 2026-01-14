"""
JSON to Excel Mapping Configuration

This module defines how extracted JSON data maps to WORKBOOK2.xlsx TCO template.
"""

# =============================================================================
# COLUMN MAPPING: JSON Field -> Excel Column (FIS Section)
# =============================================================================

FIS_COLUMN_MAP = {
    # Input columns (data we write)
    'fee_type': 'B',           # "Monthly F", "Monthly V", "Annual", "One-Time"
    'proposal_qty': 'C',       # Usually 1
    'solution_name': 'O',      # Service/product name
    'category': 'P',           # Category description
    'per_unit_rate': 'Q',      # Monthly rate or one-time fee amount

    # Formula columns (auto-calculated, DO NOT WRITE)
    # 'avg_monthly_qty': 'D',  # FORMULA
    # 'year_1_qty': 'E',       # FORMULA
    # ... years 2-10 qty      # FORMULA
    # 'year_1_monthly': 'R',   # FORMULA
    # 'year_1_cost': 'S',      # FORMULA
    # ... years 2-10 cost     # FORMULA
    # 'total_term_cost': 'AN', # FORMULA
}

# =============================================================================
# ROW MAPPING: JSON Category -> Excel Row Ranges
# =============================================================================

FIS_ROW_SECTIONS = {
    'Bundle': {
        'start_row': 7,
        'end_row': 20,
        'description': 'Bundle FIS Products (Years 1-7 core processing)',
        'notes': 'One row per year of bundle pricing'
    },
    'Non-Bundle Required': {
        'start_row': 22,
        'end_row': 54,
        'description': 'Non-Bundle Required FIS Products',
        'notes': 'Required FIS products not in bundle'
    },
    'Non-Bundle Required Third-Party': {
        'start_row': 55,
        'end_row': 85,
        'description': 'Non-Bundle Required Third Parties',
        'notes': 'Required third-party integrations'
    },
    'One-Time': {
        'start_row': 86,
        'end_row': 109,
        'description': 'Implementation Credits and One-time Fees',
        'notes': 'Credits are negative, fees are positive'
    },
    'One-Time Third-Party': {
        'start_row': 110,
        'end_row': 120,
        'description': 'Third-Party Implementation Fees',
        'notes': 'Third-party one-time fees'
    },
    'Non-Bundle Optional': {
        'start_row': 121,
        'end_row': 129,
        'description': 'Optional FIS Solutions',
        'notes': 'Optional FIS add-ons'
    },
    'Non-Bundle Optional Third-Party': {
        'start_row': 130,
        'end_row': 164,
        'description': 'Optional Third-Party Solutions',
        'notes': 'Optional third-party products'
    }
}

# =============================================================================
# FEE TYPE MAPPING: JSON fee_type -> Excel fee_type
# =============================================================================

FEE_TYPE_MAP = {
    'Monthly F': 'Monthly F',      # Fixed monthly
    'Monthly V': 'Monthly V',      # Variable monthly
    'Annual': 'Annual',            # Annual billing
    'One-Time': 'One-Time',        # One-time fee
}

# =============================================================================
# CATEGORY ROUTING: Determines which Excel section based on JSON attributes
# =============================================================================

def get_excel_section(json_item):
    """
    Determine which Excel row section a JSON item belongs to.

    Args:
        json_item: Dictionary with keys: category, optional, third_party, fee_type

    Returns:
        tuple: (section_name, section_config)
    """
    category = json_item.get('category', '')
    is_optional = json_item.get('optional', False)
    is_third_party = json_item.get('third_party', False)
    fee_type = json_item.get('fee_type', '')

    # One-Time items
    if fee_type == 'One-Time' or 'One-Time' in category:
        if is_third_party:
            return 'One-Time Third-Party', FIS_ROW_SECTIONS['One-Time Third-Party']
        return 'One-Time', FIS_ROW_SECTIONS['One-Time']

    # Bundle items
    if category == 'Bundle' or 'Bundle' in category:
        return 'Bundle', FIS_ROW_SECTIONS['Bundle']

    # Optional items
    if is_optional or 'Optional' in category:
        if is_third_party:
            return 'Non-Bundle Optional Third-Party', FIS_ROW_SECTIONS['Non-Bundle Optional Third-Party']
        return 'Non-Bundle Optional', FIS_ROW_SECTIONS['Non-Bundle Optional']

    # Required items (default)
    if is_third_party:
        return 'Non-Bundle Required Third-Party', FIS_ROW_SECTIONS['Non-Bundle Required Third-Party']
    return 'Non-Bundle Required', FIS_ROW_SECTIONS['Non-Bundle Required']


# =============================================================================
# SAMPLE MAPPING DEMONSTRATION
# =============================================================================

def demonstrate_mapping():
    """Show how JSON items map to Excel cells."""

    # Sample JSON items (from liberty_extraction_ai.json)
    sample_items = [
        {
            "solution_name": "Core: HORIZON",
            "fee_type": "Monthly F",
            "category": "Existing Service - Core",
            "monthly_fee": 16792.0,
            "one_time_fee": 0.0,
            "optional": False,
            "third_party": False
        },
        {
            "solution_name": "Digital: Zelle",
            "fee_type": "Monthly F",
            "category": "Existing Service - Digital",
            "monthly_fee": 641.0,
            "optional": False,
            "third_party": False
        },
        {
            "solution_name": "Accounts Payable: Avid Ascend",
            "fee_type": "Monthly F",
            "category": "Existing Service - Other",
            "monthly_fee": 807.0,
            "optional": False,
            "third_party": True
        },
        {
            "solution_name": "Treasury: eWire (Consumer)",
            "fee_type": "Monthly V",
            "category": "New Solution",
            "monthly_fee": 0.0,
            "per_unit_rate": 5.0,
            "unit_description": "per wire",
            "one_time_fee": 1000.0,
            "optional": False,
            "third_party": False
        }
    ]

    print("=" * 100)
    print("JSON TO EXCEL MAPPING DEMONSTRATION")
    print("=" * 100)

    for item in sample_items:
        section_name, section_config = get_excel_section(item)

        print(f"\n{'-' * 100}")
        print(f"JSON Item: {item['solution_name']}")
        print(f"{'-' * 100}")

        print(f"\n  SOURCE (JSON):")
        print(f"    solution_name: {item['solution_name']}")
        print(f"    fee_type: {item['fee_type']}")
        print(f"    category: {item.get('category', 'N/A')}")
        print(f"    monthly_fee: ${item.get('monthly_fee', 0):,.2f}")
        print(f"    one_time_fee: ${item.get('one_time_fee', 0):,.2f}")
        print(f"    optional: {item.get('optional', False)}")
        print(f"    third_party: {item.get('third_party', False)}")

        print(f"\n  TARGET (Excel):")
        print(f"    Section: {section_name}")
        print(f"    Row Range: {section_config['start_row']} - {section_config['end_row']}")

        # Determine rate to use
        rate = item.get('monthly_fee', 0) or item.get('per_unit_rate', 0) or item.get('one_time_fee', 0)

        print(f"\n  CELL MAPPING:")
        print(f"    B[row] = '{item['fee_type']}'")
        print(f"    C[row] = 1")
        print(f"    O[row] = '{item['solution_name']}'")
        print(f"    P[row] = '{item.get('category', '')}'")
        print(f"    Q[row] = {rate}")

        print(f"\n  AUTO-CALCULATED (formulas will compute):")
        print(f"    S[row] = Year 1 Cost (Q × 12 for monthly)")
        print(f"    AN[row] = Total Term Cost")


if __name__ == "__main__":
    demonstrate_mapping()
