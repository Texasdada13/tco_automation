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

# =============================================================================
# AI EXTRACTION SETTINGS (Anthropic Claude API)
# =============================================================================

# Claude API Configuration
AI_CONFIG = {
    'model': 'claude-sonnet-4-20250514',  # Recommended model
    'max_tokens': 8192,
    'temperature': 0.0,  # Deterministic output for extraction
    'max_retries': 3,
    'retry_delay_seconds': 2,
}

# Default contract parameters
CONTRACT_DEFAULTS = {
    'term_years': 7,
    'annual_increase_rate': 0.03,  # 3% CPI
    'volume_growth_rate': 0.0,     # No growth by default
}

# =============================================================================
# CONFIDENCE & QUALITY ASSURANCE SETTINGS
# =============================================================================

# Confidence thresholds for two-bucket routing
CONFIDENCE_THRESHOLDS = {
    'auto_accept': 0.90,      # >= 90%: Auto-populate to Excel (Bucket 1)
    'manual_review': 0.70,    # 70-89%: Flag for quick review
    'reject': 0.50,           # < 50%: Likely incorrect, needs human input
}

# Quality assurance layer settings
QA_CONFIG = {
    # Layer 1: Confidence scoring
    'enable_confidence_check': True,
    'min_field_confidence': 0.85,     # Per-field minimum
    'min_item_confidence': 0.90,       # Per-item minimum for auto-accept

    # Layer 2: Cross-validation
    'enable_cross_validation': True,
    'sum_tolerance_percent': 0.02,     # 2% tolerance for sum checks
    'rate_tolerance_percent': 0.01,    # 1% tolerance for rate calculations

    # Layer 3: Business rules
    'enable_business_rules': True,
    'allow_zero_required_items': False,  # Required items cannot be $0
    'max_monthly_fee': 500000,           # Sanity check upper limit
    'max_one_time_fee': 5000000,         # Sanity check upper limit

    # Layer 4: Source traceability
    'enable_traceability': True,
    'require_source_context': True,      # Each extraction must cite source
}

# =============================================================================
# VENDOR CONTEXT CACHING
# =============================================================================

CACHE_CONFIG = {
    'enabled': True,
    'cache_directory': 'vendor_cache',
    'cache_expiry_days': 90,            # Cache entries expire after 90 days
    'min_confidence_to_cache': 0.70,    # Only cache if extraction >= 70%
    'max_cache_entries_per_vendor': 100,
}

# What gets cached per vendor
CACHE_COMPONENTS = {
    'vendor_profile': True,       # Vendor name, doc types, product lines
    'terminology_map': True,      # Vendor terms -> standard terms
    'document_patterns': True,    # Table layouts, column mappings
    'extraction_templates': True, # Successful extraction patterns
    'correction_history': True,   # Manual corrections for learning
}

# =============================================================================
# FALLBACK SETTINGS
# =============================================================================

FALLBACK_CONFIG = {
    'enable_rule_based_fallback': True,  # Use FIS/JH extractors if API fails
    'enable_cross_validation': True,     # Compare AI vs rule-based results
    'prefer_ai_on_conflict': True,       # Trust AI when results differ
    'max_api_failures_before_fallback': 3,
}

# =============================================================================
# OUTPUT SETTINGS
# =============================================================================

OUTPUT_CONFIG = {
    # Bucket 1: Auto-populated Excel
    'excel_output_enabled': True,

    # Bucket 2: Manual review report
    'review_report_enabled': True,
    'review_report_format': 'docx',  # 'docx' or 'xlsx'
    'include_source_context': True,
    'include_suggested_actions': True,

    # Audit trail
    'save_extraction_json': True,    # Save raw extraction results
    'save_qa_results': True,         # Save QA check results
}

# =============================================================================
# LOGGING
# =============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_api_calls': True,
    'log_confidence_scores': True,
    'log_qa_failures': True,
}
