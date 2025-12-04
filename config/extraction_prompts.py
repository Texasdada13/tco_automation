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


# =============================================================================
# NEW 4-STAGE AI EXTRACTION PROMPTS (Vendor-Agnostic)
# =============================================================================

# Stage 1: Context Analysis - Understand document before extraction
CONTEXT_ANALYSIS_PROMPT = """Analyze this vendor proposal document to understand its structure and terminology.

DOCUMENT TEXT:
{document_text}

TABLES FOUND:
{tables}

Provide a comprehensive analysis:

1. **VENDOR IDENTIFICATION**
   - Vendor name (e.g., FIS, Jack Henry, Fiserv, or identify new vendor)
   - Document type (Proposal, Deal Sheet, Quote, Contract, Amendment)

2. **CONTRACT TERMS**
   - Contract duration (in years)
   - Annual price increase rate (CPI percentage)
   - Start date (if mentioned)
   - Any minimum commitments or volume requirements

3. **PRICING STRUCTURE ANALYSIS**
   - How is pricing organized? (by product, by category, bundled, tiered)
   - What fee types are present? (monthly, annual, one-time, per-transaction)
   - Are there multiple scenarios/options?
   - Are there credits or discounts?

4. **TERMINOLOGY MAPPING**
   Create a mapping of vendor-specific terms to standard TCO terms:
   - Example: "Maintenance Fee" -> "Monthly Fee"
   - Example: "License" -> "One-Time Fee"
   - Example: "Support" -> "Annual Fee"

5. **TABLE ANALYSIS**
   For each table that contains pricing data:
   - Table index/identifier
   - Purpose (pricing, summary, terms, products)
   - Key columns identified

6. **EXTRACTION GUIDANCE**
   - Which sections contain pricing data?
   - Any special formatting or structure notes?
   - Potential challenges or ambiguities?

Return as JSON:
{{
    "vendor_name": "...",
    "document_type": "...",
    "contract_term_years": N,
    "annual_increase_rate": 0.XX,
    "pricing_structure": "description",
    "has_multiple_scenarios": true/false,
    "terminology_map": {{
        "vendor_term": "standard_term",
        ...
    }},
    "fee_types_found": ["Monthly", "One-Time", ...],
    "tables_with_pricing": [
        {{"index": N, "purpose": "...", "key_columns": [...]}}
    ],
    "extraction_notes": ["any important observations"],
    "confidence": 0.0-1.0
}}"""


# Stage 2: Line Item Extraction - Extract all pricing with confidence
LINE_ITEM_EXTRACTION_PROMPT = """Extract ALL pricing line items from this document.

DOCUMENT CONTEXT:
{context}

DOCUMENT TEXT:
{document_text}

TABLES:
{tables}

For EACH product, service, or fee, extract a complete line item.

REQUIRED FIELDS FOR EACH ITEM:
1. **solution_name**: Clear product/service name (as it appears in document)
2. **fee_type**: Classify as one of:
   - "Monthly F" (fixed monthly fee)
   - "Monthly V" (variable/per-unit monthly)
   - "Annual" (yearly fee)
   - "One-Time" (implementation, license, setup)
3. **category**: Classify as one of:
   - "Bundle" (core processing in main package)
   - "Non-Bundle Required" (required add-ons)
   - "Non-Bundle Optional" (optional add-ons)
   - "Third-Party Required" (required 3rd party)
   - "Third-Party Optional" (optional 3rd party)
   - "One-Time Credit" (discounts - use NEGATIVE amount)
   - "One-Time Fee" (implementation, conversion)
4. **per_unit_rate**: The base rate/price per unit
5. **monthly_fee**: Monthly amount (0 if not monthly)
6. **annual_fee**: Annual amount (calculated or stated)
7. **one_time_fee**: One-time amount (0 if recurring)
8. **optional**: true/false
9. **third_party**: true/false

CONFIDENCE SCORING (per field):
For each field, provide confidence 0.0-1.0:
- 1.0: Exact value clearly stated in document
- 0.9: Value clearly stated, minor interpretation
- 0.8: Value derived from clear context
- 0.7: Value requires some inference
- 0.6: Moderate uncertainty
- <0.6: Significant uncertainty

SOURCE TRACEABILITY:
For each item, include:
- **source_location**: Where in document (table X row Y, page N, section)
- **source_text**: The exact text this was extracted from (max 200 chars)

EXTRACTION RULES:
- Extract EVERY line item, even if $0
- Credits/discounts must be NEGATIVE numbers
- Don't calculate - extract actual values shown
- If unclear, extract best interpretation and note in warnings
- Include ALL products from ALL sections/scenarios

Return as JSON:
{{
    "line_items": [
        {{
            "solution_name": "...",
            "fee_type": "Monthly F|Monthly V|Annual|One-Time",
            "category": "Bundle|Non-Bundle Required|...",
            "per_unit_rate": 0.00,
            "monthly_fee": 0.00,
            "annual_fee": 0.00,
            "one_time_fee": 0.00,
            "optional": false,
            "third_party": false,
            "field_confidence": {{
                "solution_name": 0.95,
                "fee_type": 0.90,
                "category": 0.85,
                "amounts": 0.95
            }},
            "overall_confidence": 0.90,
            "source_location": "Table 3, Row 5",
            "source_text": "Digital Banking - $2,500/mo"
        }}
    ],
    "total_items_extracted": N,
    "extraction_warnings": ["any issues encountered"],
    "stated_totals": {{
        "monthly_total": 0.00,
        "annual_total": 0.00,
        "one_time_total": 0.00
    }}
}}"""


# Stage 3: Calculation Engine - Compute multi-year projections
CALCULATION_ENGINE_PROMPT = """Calculate multi-year TCO projections for these extracted line items.

LINE ITEMS:
{line_items}

CONTRACT PARAMETERS:
- Contract term: {contract_term} years
- Annual price increase (CPI): {annual_increase}%
- Volume growth rate: {growth_rate}%

CALCULATION RULES:

1. **QUANTITIES BY YEAR**
   For each line item, calculate quantities for years 1 through {contract_term}:
   - Monthly Fixed/Variable fees: 12 months per year
   - Annual fees: 1 per year
   - One-Time fees: 1 in year 1, 0 thereafter
   - Apply volume growth rate to variable fees if applicable

2. **COSTS BY YEAR**
   For each line item and year:
   - Year 1: base_rate * quantity
   - Year 2+: previous_year_rate * (1 + annual_increase) * quantity
   - One-time fees: full amount in year 1 only

3. **TOTALS**
   Calculate:
   - Total by year (sum of all items)
   - Total by category (Bundle, Non-Bundle, etc.)
   - Grand total (sum of all years)
   - Average annual cost

Return as JSON:
{{
    "calculated_items": [
        {{
            "solution_name": "...",
            "quantities_by_year": {{
                "year_1": 12,
                "year_2": 12,
                ...
            }},
            "costs_by_year": {{
                "year_1": 30000.00,
                "year_2": 30900.00,
                ...
            }},
            "total_contract_cost": 0.00
        }}
    ],
    "summary": {{
        "total_monthly_year1": 0.00,
        "total_annual_year1": 0.00,
        "total_one_time": 0.00,
        "total_contract_value": 0.00,
        "average_annual_cost": 0.00,
        "year_by_year_totals": {{
            "year_1": 0.00,
            "year_2": 0.00,
            ...
        }},
        "category_totals": {{
            "Bundle": 0.00,
            "Non-Bundle Required": 0.00,
            "Non-Bundle Optional": 0.00,
            "One-Time": 0.00
        }}
    }},
    "calculation_notes": ["any assumptions made"]
}}"""


# Stage 4: Quality Assurance - Validate extraction accuracy
QA_VALIDATION_PROMPT = """Validate the extracted TCO data for accuracy and completeness.

EXTRACTED LINE ITEMS:
{line_items}

CALCULATED TOTALS:
{calculated_totals}

DOCUMENT STATED TOTALS (if available):
{stated_totals}

ORIGINAL DOCUMENT CONTEXT:
{document_context}

Perform these validation checks:

**LAYER 1: SUM VERIFICATION**
- Do line items sum to stated document totals?
- Calculate: sum(monthly_fees) vs stated_monthly_total
- Calculate: sum(one_time_fees) vs stated_one_time_total
- Flag any discrepancy > 2%

**LAYER 2: RATE CONSISTENCY**
- Does monthly_fee * 12 = annual_fee (where applicable)?
- Does per_unit_rate match the extracted fees?
- Are calculations mathematically correct?

**LAYER 3: BUSINESS RULES**
- No required items with $0 pricing (unless explicitly free)
- No negative prices (except credits)
- Amounts within reasonable ranges
- All required fields present (name, fee_type, category, amount)

**LAYER 4: LOGICAL CONSISTENCY**
- No duplicate entries (same name, same category, same amounts)
- Categories make sense for the items
- Fee types match the pricing pattern

For each check that FAILS, create an entry with:
- Which item failed
- What check failed
- Expected vs actual values
- Suggested correction

Return as JSON:
{{
    "validation_passed": true/false,
    "checks_performed": [
        {{
            "check_name": "Sum Verification - Monthly",
            "passed": true/false,
            "expected": "value or description",
            "actual": "value found",
            "discrepancy": "description if failed"
        }}
    ],
    "failed_items": [
        {{
            "solution_name": "...",
            "failure_reason": "...",
            "failed_checks": ["check1", "check2"],
            "suggested_action": "...",
            "original_confidence": 0.XX,
            "adjusted_confidence": 0.XX
        }}
    ],
    "passed_items_count": N,
    "failed_items_count": N,
    "overall_confidence": 0.XX,
    "validation_summary": "brief summary of validation results"
}}"""


# Ambiguity resolution prompt
AMBIGUITY_RESOLUTION_PROMPT = """Resolve ambiguity in extracted field.

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
        # Original prompts
        'tco_system': TCO_SYSTEM_PROMPT,
        'fis_extraction': FIS_EXTRACTION_PROMPT,
        'jh_extraction': JACK_HENRY_EXTRACTION_PROMPT,
        'category': CATEGORY_CLASSIFICATION_PROMPT,
        'fee_type': FEE_TYPE_CLASSIFICATION_PROMPT,
        'table': TABLE_EXTRACTION_PROMPT,
        'projection': COST_PROJECTION_PROMPT,
        'validation': VALIDATION_PROMPT,
        'comparison': VENDOR_COMPARISON_PROMPT,
        'ambiguity': AMBIGUITY_RESOLUTION_PROMPT,
        # New 4-stage AI extraction prompts
        'context_analysis': CONTEXT_ANALYSIS_PROMPT,
        'line_item_extraction': LINE_ITEM_EXTRACTION_PROMPT,
        'calculation_engine': CALCULATION_ENGINE_PROMPT,
        'qa_validation': QA_VALIDATION_PROMPT,
    }

    prompt = prompts.get(prompt_type, '')
    if kwargs:
        prompt = prompt.format(**kwargs)

    return prompt
