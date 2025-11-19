"""
Configuration file for TCO Automation System
Contains mapping rules, categories, and system settings
"""

# Fee type mappings
FEE_TYPES = {
    'monthly_fixed': 'Monthly F',
    'monthly_variable': 'Monthly V',
    'annual': 'Annual',
    'one_time': 'One-Time'
}

# Vendor identifiers
VENDORS = {
    'FIS': 'FIS',
    'JACK_HENRY': 'Jack Henry',
    'OTHER': 'Other'
}

# Product categories
PRODUCT_CATEGORIES = {
    'BUNDLE': 'Bundle',
    'NON_BUNDLE_REQUIRED': 'Non-Bundle Required',
    'NON_BUNDLE_OPTIONAL': 'Non-Bundle Optional',
    'THIRD_PARTY_REQUIRED': 'Third-Party Required',
    'THIRD_PARTY_OPTIONAL': 'Third-Party Optional'
}

# FIS specific mappings
FIS_BUNDLE_KEYWORDS = [
    'HORIZON',
    'core processing',
    'bundle',
    'Digital One',
    'Payments One',
    'ImageCentre'
]

# Jack Henry specific mappings
JH_PRODUCT_FAMILIES = {
    'SilverLake': 'BUNDLE',
    'Xperience': 'BUNDLE',
    'OnBoard': 'NON_BUNDLE',
    'Teller': 'NON_BUNDLE',
    'Banno': 'NON_BUNDLE',
    'Synapsys': 'NON_BUNDLE'
}

# TCO Template column mappings
TCO_COLUMNS = {
    'FIS': {
        'fee_type': 'B',
        'proposal': 'C',
        'avg_monthly_qty': 'D',
        'year_1_qty': 'E',
        'year_2_qty': 'F',
        'year_3_qty': 'G',
        'year_4_qty': 'H',
        'year_5_qty': 'I',
        'year_6_qty': 'J',
        'year_7_qty': 'K',
        'solution_name': 'O',
        'category': 'P',
        'per_unit_rate': 'Q',
        'year_1_cost': 'S',
        'year_2_cost': 'T',
        'year_3_cost': 'U',
        'year_4_cost': 'V',
        'year_5_cost': 'W',
        'year_6_cost': 'X',
        'year_7_cost': 'Y'
    },
    'JACK_HENRY': {
        'fee_type': 'AO',
        'proposal': 'AP',
        'avg_monthly_qty': 'AQ',
        'year_1_qty': 'AR',
        'year_2_qty': 'AS',
        'year_3_qty': 'AT',
        'year_4_qty': 'AU',
        'year_5_qty': 'AV',
        'year_6_qty': 'AW',
        'year_7_qty': 'AX',
        'solution_name': 'BB',
        'category': 'BC',
        'per_unit_rate': 'BD',
        'year_1_cost': 'BF',
        'year_2_cost': 'BG',
        'year_3_cost': 'BH',
        'year_4_cost': 'BI',
        'year_5_cost': 'BJ',
        'year_6_cost': 'BK',
        'year_7_cost': 'BL'
    }
}

# Default growth rate
DEFAULT_GROWTH_RATE = 0.20  # 20% annual growth

# Default CPI rates
DEFAULT_CPI_BUNDLE = 0.06  # 6%
DEFAULT_CPI_NON_BUNDLE = 0.03  # 3%

# Line Items sheet starting rows for different categories
LINE_ITEM_START_ROWS = {
    'FIS_BUNDLE': 7,
    'FIS_NON_BUNDLE_REQUIRED': 22,
    'FIS_NON_BUNDLE_OPTIONAL': 100,
    'FIS_ONE_TIME': 150,
    'JH_BUNDLE': 7,
    'JH_NON_BUNDLE_REQUIRED': 50,
    'JH_NON_BUNDLE_OPTIONAL': 100,
    'JH_ONE_TIME': 150
}
