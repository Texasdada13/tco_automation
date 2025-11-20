"""
Extraction Prompts Configuration

Contains specialized prompts for TCO field extraction using Claude API.
"""

# System prompt for TCO extraction
TCO_SYSTEM_PROMPT = """You are a specialized document extraction assistant for Total Cost of Ownership (TCO) analysis. Your task is to extract pricing and contract information from vendor proposals with high accuracy.

Key extraction rules:
1. Extract exact values as they appear - do not calculate or infer
2. Preserve currency formatting with $ signs
3. Note any ambiguities or multiple possible interpretations
4. Distinguish between monthly, annual, and one-time fees
5. Identify optional vs required services
6. Flag any pricing that seems inconsistent or unclear"""


# Vendor-specific extraction prompts
FIS_EXTRACTION_PROMPT = """Extract the following information from this FIS vendor proposal:

PRICING STRUCTURE:
- Bundle pricing (core processing fees by term: 5-year, 7-year, 10-year)
- Monthly fees for each solution/service
- One-time fees (implementation, conversion, training)
- Credits or discounts applied

TERMS & CONDITIONS:
- Contract term length
- Annual increase percentage (CPI)
- Early termination penalties
- Minimum commitments

FOR EACH LINE ITEM, EXTRACT:
- Solution/Product name
- Monthly fee amount
- One-time fee amount
- Whether it's third-party
- Whether it's optional or required
- Any calculation basis (per item, per user, etc.)

Return as structured JSON with these sections:
- bundle_pricing
- monthly_fees
- one_time_fees
- terms_conditions"""


JACK_HENRY_EXTRACTION_PROMPT = """Extract the following information from this Jack Henry proposal/deal sheet:

SUMMARY INFORMATION:
- Bank name
- Total assets
- Core product (SilverLake, etc.)
- Total monthly list/net prices
- Annualized totals

FOR EACH PRODUCT LINE:
- Product Description
- Order Type (Add/Existing/Remove)
- Delivery method
- Optional (Y/N)
- Category
- Product Family
- Quantity
- License fees (List and Net)
- Install fees (List and Net)
- Maintenance fees (List and Net)
- Monthly fees (List and Net)

IMPORTANT:
- Capture ALL products from ALL proposal sheets
- Note any hidden rows/columns
- Include formula references where pricing is calculated
- Flag any discrepancies between list and net prices

Return as structured JSON with:
- summary
- proposals (array of scenario objects)
- each scenario contains products array"""


# Category classification prompt
CATEGORY_CLASSIFICATION_PROMPT = """Classify the following product/service into one of these TCO categories:

CATEGORIES:
1. Bundle - Core processing components included in main package
2. Non-Bundle Required - Required add-ons not in core bundle
3. Non-Bundle Optional - Optional add-ons
4. Third-Party Required - Required third-party services
5. Third-Party Optional - Optional third-party services
6. One-Time Fee - Implementation, conversion, training
7. One-Time Credit - Discounts, signing bonuses

Product to classify: {product_name}
Context: {context}

Classification rules:
- SilverLake, Xperience = Bundle
- OnBoard, Teller, Banno = Non-Bundle
- FIS marked as "Third Party" = Third-Party
- Items with $0 monthly but one-time = One-Time
- Negative amounts = Credits

Return JSON: {{"category": "<category>", "confidence": 0.0-1.0, "reasoning": "<brief explanation>"}}"""


# Fee type classification prompt
FEE_TYPE_CLASSIFICATION_PROMPT = """Classify the fee type for this pricing item:

FEE TYPES:
1. Monthly F - Fixed monthly fee (same amount each month)
2. Monthly V - Variable monthly fee (based on usage/volume)
3. Annual - Annual fee (paid yearly)
4. One-Time - One-time charge (implementation, setup, etc.)

Item: {item_name}
Amount: {amount}
Frequency indicator: {frequency}

Classification rules:
- "/mo" or "monthly" = Monthly
- "per item", "per transaction" = Monthly V
- "flat", "fixed" = Monthly F
- "/yr", "annual" = Annual
- "implementation", "conversion", "setup" = One-Time

Return JSON: {{"fee_type": "<type>", "confidence": 0.0-1.0}}"""


# Table extraction prompt
TABLE_EXTRACTION_PROMPT = """Extract all tabular data from this text. Identify:

1. Table headers/column names
2. Row data with values aligned to columns
3. Any totals or summary rows
4. Merged cells or spanning headers

For pricing tables specifically:
- Identify the product/service column
- Identify all price columns (monthly, annual, one-time)
- Note currency values and their context
- Flag any calculated fields

Return as JSON array of tables, each with:
- table_type: "pricing", "summary", "terms", "other"
- headers: [column names]
- rows: [[row values]]
- notes: any special observations"""


# Multi-year cost projection prompt
COST_PROJECTION_PROMPT = """Calculate the multi-year cost projection for this pricing:

BASE DATA:
{pricing_data}

PARAMETERS:
- Contract term: {term} years
- Annual increase: {annual_increase}%
- Growth rate for quantities: {growth_rate}%

CALCULATE:
1. Year-by-year costs for each line item
2. Apply annual increases to fees
3. Apply growth rates to quantities where applicable
4. Sum totals by year and category

Return JSON with:
- yearly_totals: {{year_1: amount, year_2: amount, ...}}
- category_totals: {{bundle: {{year_1: amount, ...}}, non_bundle: ...}}
- grand_total: total contract value
- average_annual: average annual cost"""


# Validation prompt
VALIDATION_PROMPT = """Validate the extracted data for consistency and completeness:

EXTRACTED DATA:
{extracted_data}

CHECK FOR:
1. Missing required fields
2. Inconsistent totals (sum of parts vs stated total)
3. Unusual values (negative prices, 0 for required fees)
4. Date/term inconsistencies
5. Category mismatches
6. Duplicate entries

Return JSON with:
- is_valid: boolean
- errors: [list of critical issues]
- warnings: [list of potential issues]
- suggestions: [recommended fixes]
- confidence: 0.0-1.0 overall confidence in extraction"""


# Comparison prompt
VENDOR_COMPARISON_PROMPT = """Compare the extracted data from multiple vendors:

VENDOR 1 ({vendor1_name}):
{vendor1_data}

VENDOR 2 ({vendor2_name}):
{vendor2_data}

ANALYZE:
1. Total cost comparison over {term} years
2. Category-by-category comparison
3. Feature/product differences
4. Terms and conditions differences
5. Risk factors for each vendor

Return JSON with:
- cost_comparison: {{vendor1: total, vendor2: total, difference: amount, percentage: %}}
- category_comparison: detailed breakdown
- feature_gaps: what one vendor offers that other doesn't
- risk_analysis: potential concerns
- recommendation: brief summary"""


# Ambiguity resolution prompt
AMBIGUITY_RESOLUTION_PROMPT = """The following extracted value is ambiguous or unclear:

FIELD: {field_name}
EXTRACTED VALUE: {extracted_value}
CONTEXT: {context}

POSSIBLE INTERPRETATIONS:
{interpretations}

Based on:
1. The document context
2. Standard industry terminology
3. Logical consistency with other extracted fields

Determine the most likely correct interpretation.

Return JSON with:
- resolved_value: the best interpretation
- confidence: 0.0-1.0
- reasoning: why this interpretation is most likely
- alternative: second best option if confidence < 0.8"""


def get_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a formatted extraction prompt.

    Args:
        prompt_type: Type of prompt to retrieve
        **kwargs: Variables to format into the prompt

    Returns:
        Formatted prompt string
    """
    prompts = {
        'tco_system': TCO_SYSTEM_PROMPT,
        'fis_extraction': FIS_EXTRACTION_PROMPT,
        'jh_extraction': JACK_HENRY_EXTRACTION_PROMPT,
        'category': CATEGORY_CLASSIFICATION_PROMPT,
        'fee_type': FEE_TYPE_CLASSIFICATION_PROMPT,
        'table': TABLE_EXTRACTION_PROMPT,
        'projection': COST_PROJECTION_PROMPT,
        'validation': VALIDATION_PROMPT,
        'comparison': VENDOR_COMPARISON_PROMPT,
        'ambiguity': AMBIGUITY_RESOLUTION_PROMPT
    }

    prompt = prompts.get(prompt_type, '')
    if kwargs:
        prompt = prompt.format(**kwargs)

    return prompt
