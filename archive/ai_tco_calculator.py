"""
AI-Enhanced TCO Calculator

Uses Claude API to analyze extracted FIS proposal data and calculate accurate TCO values.
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anthropic import Anthropic
from dotenv import load_dotenv
import openpyxl
from openpyxl.cell.cell import MergedCell

from extractors import extract_fis_proposal
from config import TCO_COLUMNS, LINE_ITEM_START_ROWS, FEE_TYPES

# Load environment
load_dotenv()


def get_ai_tco_calculations(fis_data: Dict[str, Any], term: str = '7_year', api_key: str = None) -> Dict[str, Any]:
    """
    Send extracted FIS data to Claude API for accurate TCO calculations.

    Args:
        fis_data: Raw extracted FIS proposal data
        term: Contract term ('5_year', '7_year', '10_year')
        api_key: Anthropic API key

    Returns:
        Dictionary with calculated TCO line items
    """
    client = Anthropic(api_key=api_key or os.environ.get('ANTHROPIC_API_KEY'))

    # Prepare data summary for Claude
    data_summary = {
        'vendor': fis_data.get('vendor', 'FIS'),
        'contract_term': term,
        'bundle_pricing': fis_data.get('bundle_pricing', {}),
        'monthly_fees': fis_data.get('monthly_fees', []),
        'one_time_credits': fis_data.get('one_time_credits', {}),
        'optional_fees': fis_data.get('optional_fees', []),
    }

    prompt = f"""You are a financial analyst expert in Total Cost of Ownership (TCO) calculations for banking software.

I have extracted the following data from an FIS vendor proposal. Please analyze this data and calculate accurate TCO values for a {term.replace('_', '-')} contract.

## EXTRACTED DATA:

### Bundle Pricing (Monthly amounts by year):
{json.dumps(data_summary['bundle_pricing'], indent=2)}

### Monthly Fees (Non-bundle services):
{json.dumps(data_summary['monthly_fees'], indent=2)}

### One-Time Credits and Fees:
{json.dumps(data_summary['one_time_credits'], indent=2)}

## CALCULATION REQUIREMENTS:

1. **Bundle Items** (CRITICAL - READ CAREFULLY):
   - The bundle pricing shows MONTHLY amounts that CHANGE each year
   - For {term}: Look at the "{term}" key in each year's data
   - Create ONE bundle line item called "FIS Core Processing Bundle"
   - Calculate each year's cost using THAT YEAR'S monthly rate × 12
   - Year 1: $15,000 × 12 = $180,000
   - Year 2: $17,500 × 12 = $210,000
   - Year 3: $22,500 × 12 = $270,000
   - Year 4: $28,000 × 12 = $336,000
   - Year 5: $35,000 × 12 = $420,000
   - Year 6: If $0 in data, apply 6.5% increase: $35,000 × 1.065 = $37,275 × 12 = $447,300
   - Year 7: Apply 6.5% increase: $37,275 × 1.065 = $39,698 × 12 = $476,375
   - TOTAL BUNDLE: $2,339,675

2. **Non-Bundle FIS Required Products** (ONLY include these 8 items):
   - NO ESCALATION - flat rate across all 7 years
   - Year cost = monthly_fee × 12 (same for all years)
   - ONLY include these EXACT 8 items from the FIS Solutions section:
     1. Paper and Envelopes ($29)
     2. Debit Card Production ($1,018)
     3. DirectLink Risk Review / DLRR ($233)
     4. Card Suite Pro ($425)
     5. Payments One Fraud Case Investigation ($500)
     6. Payments One Full-Service Fraud Disputes ($175)
     7. Tokenization / ApplePay ($337)
     8. NYCE Preferred Network ($152)
   - Monthly total: $2,869
   - Each year: $2,869 × 12 = $34,428
   - 7-year total: $34,428 × 7 = $240,996
   - DO NOT include: Subpoena Centre, Start Card, FedNOW, RTP, Zelle, WebConnect, Credit Insights, Collaboration Hub

3. **Non-Bundle Required Third Parties** (ONLY include these 4 items):
   - NO ESCALATION - flat rate across all 7 years
   - Year cost = monthly_fee × 12 (same for all years)
   - ONLY include these EXACT 4 items from the Third-Party Solutions section:
     1. Network Services ($2,088)
     2. SmartSign / eSignature ($478)
     3. TruStage ($1,158)
     4. IBM Cognos / HORIZON 360 ($1,172)
   - Monthly total: $4,896
   - Each year: $4,896 × 12 = $58,752
   - 7-year total: $58,752 × 7 = $411,264
   - DO NOT include: AvidAscend, or any "Total" rows

4. **One-Time Credits/Fees** (SEPARATE from recurring):
   - Use the "{term}" column values
   - Keep as separate line items, not added to yearly recurring totals
   - Negative values are CREDITS, positive values are FEES
   - Skip the "Total" row

5. **Output Format**:
   Return a JSON object with this structure:
   {{
     "summary": {{
       "bundle_total_7yr": 2339675,
       "non_bundle_fis_total_7yr": 240996,
       "third_party_total_7yr": 411264,
       "recurring_subtotal_7yr": 2991935,
       "total_one_time_fees": <sum of positive one-time values>,
       "total_one_time_credits": <sum of negative one-time values as positive>,
       "net_one_time": <fees minus credits>
     }},
     "bundle_items": [
       {{
         "solution_name": "FIS Core Processing Bundle",
         "fee_type": "Monthly F",
         "category": "Bundle",
         "per_unit_rate": 15000,
         "year_1_cost": 180000,
         "year_2_cost": 210000,
         "year_3_cost": 270000,
         "year_4_cost": 336000,
         "year_5_cost": 420000,
         "year_6_cost": 447300,
         "year_7_cost": 476375
       }}
     ],
     "fis_monthly_items": [
       {{
         "solution_name": "<service name - clean up newlines>",
         "fee_type": "Monthly F" or "Monthly V",
         "category": "Non-Bundle Required",
         "per_unit_rate": <monthly rate>,
         "year_1_cost": <monthly × 12>,
         "year_2_cost": <monthly × 12>,
         "year_3_cost": <monthly × 12>,
         "year_4_cost": <monthly × 12>,
         "year_5_cost": <monthly × 12>,
         "year_6_cost": <monthly × 12>,
         "year_7_cost": <monthly × 12>
       }}
     ],
     "third_party_items": [
       {{
         "solution_name": "<service name>",
         "fee_type": "Monthly F",
         "category": "Third-Party Required",
         "per_unit_rate": <monthly rate>,
         "year_1_cost": <monthly × 12>,
         "year_2_cost": <monthly × 12>,
         "year_3_cost": <monthly × 12>,
         "year_4_cost": <monthly × 12>,
         "year_5_cost": <monthly × 12>,
         "year_6_cost": <monthly × 12>,
         "year_7_cost": <monthly × 12>
       }}
     ],
     "one_time_items": [
       {{
         "solution_name": "<item name>",
         "fee_type": "One-Time",
         "category": "One-Time Fee" or "One-Time Credit",
         "amount": <value - negative for credits>,
         "year_1_cost": <same as amount>,
         "year_2_cost": 0,
         "year_3_cost": 0,
         "year_4_cost": 0,
         "year_5_cost": 0,
         "year_6_cost": 0,
         "year_7_cost": 0
       }}
     ]
   }}

6. **Important Notes**:
   - NO CPI escalation on non-bundle items - flat rate all 7 years
   - Bundle CPI is 6.5% for years 6 and 7
   - Exclude pass-through fees (Postage, Visa/Mastercard) marked as TBD
   - One-time fees are separate from recurring costs
   - Clean up solution names - remove newlines and extra whitespace
   - Do NOT include the "Total" rows from monthly_fees or one_time_credits

Please provide the complete TCO calculation as a valid JSON object only - no additional text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON from response
    response_text = response.content[0].text

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response text: {response_text[:500]}...")
        return None


def populate_tco_template(tco_data: Dict[str, Any], template_path: str, output_path: str) -> str:
    """
    Populate TCO template with AI-calculated values.

    Args:
        tco_data: Calculated TCO data from AI
        template_path: Path to TCO template
        output_path: Path for output file

    Returns:
        Path to saved file
    """
    wb = openpyxl.load_workbook(template_path)
    ws = wb['Line Items']
    col_map = TCO_COLUMNS['FIS']

    def safe_write(cell_ref, value):
        """Safely write to cell, skip merged cells."""
        try:
            cell = ws[cell_ref]
            if not isinstance(cell, MergedCell):
                cell.value = value
                return True
        except Exception:
            pass
        return False

    # Clear existing FIS values
    cols_to_clear = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
    for row in range(7, 165):
        for col_letter in cols_to_clear:
            safe_write(f'{col_letter}{row}', None)

    def write_item(item: Dict, row: int):
        """Write a single line item to the template."""
        safe_write(f"{col_map['fee_type']}{row}", item.get('fee_type', ''))
        safe_write(f"{col_map['solution_name']}{row}", item.get('solution_name', ''))
        safe_write(f"{col_map['category']}{row}", item.get('category', ''))

        # Per unit rate (monthly)
        rate = item.get('per_unit_rate', item.get('amount', 0))
        safe_write(f"{col_map['per_unit_rate']}{row}", rate)
        safe_write(f"{col_map['proposal']}{row}", rate)

        # Average monthly qty
        safe_write(f"{col_map['avg_monthly_qty']}{row}", 1)

        # Quantities by year
        is_one_time = item.get('fee_type') == 'One-Time'
        for year_num in range(1, 8):
            qty_col = col_map.get(f'year_{year_num}_qty')
            if qty_col:
                qty = 1 if (year_num == 1 or not is_one_time) else 0
                safe_write(f'{qty_col}{row}', qty if not is_one_time else (1 if year_num == 1 else 0))

        # Costs by year
        for year_num in range(1, 8):
            cost_col = col_map.get(f'year_{year_num}_cost')
            if cost_col:
                cost = item.get(f'year_{year_num}_cost', 0) or 0
                safe_write(f'{cost_col}{row}', cost)

    # Write bundle items
    current_row = LINE_ITEM_START_ROWS['FIS_BUNDLE']
    for item in tco_data.get('bundle_items', []):
        write_item(item, current_row)
        current_row += 1

    # Write FIS non-bundle items
    current_row = LINE_ITEM_START_ROWS['FIS_NON_BUNDLE_REQUIRED']
    for item in tco_data.get('fis_monthly_items', []):
        write_item(item, current_row)
        current_row += 1

    # Also check for legacy 'monthly_items' key
    for item in tco_data.get('monthly_items', []):
        if item.get('category') == 'Non-Bundle Required':
            write_item(item, current_row)
            current_row += 1

    # Write third-party items
    current_row = max(current_row + 1, 35)  # Start after FIS items
    for item in tco_data.get('third_party_items', []):
        write_item(item, current_row)
        current_row += 1

    # Also check for legacy 'monthly_items' with third-party category
    for item in tco_data.get('monthly_items', []):
        if item.get('category') == 'Third-Party Required':
            write_item(item, current_row)
            current_row += 1

    # Write one-time items
    current_row = LINE_ITEM_START_ROWS['FIS_ONE_TIME']
    for item in tco_data.get('one_time_items', []):
        write_item(item, current_row)
        current_row += 1

    # Save
    wb.save(output_path)
    return output_path


def main(api_key: str = None, term: str = '7_year'):
    """Main function to run AI-enhanced TCO calculation."""

    proposal_path = os.path.join(os.path.dirname(__file__), 'proposal1.docx')
    template_path = os.path.join(os.path.dirname(__file__), 'WORKBOOK2.xlsx')
    output_path = os.path.join(os.path.dirname(__file__), 'FIS_TCO_Final.xlsx')

    print("=" * 70)
    print("AI-ENHANCED TCO CALCULATOR")
    print("=" * 70)

    # Step 1: Extract FIS data
    print("\n[1/4] Extracting FIS proposal data...")
    fis_data = extract_fis_proposal(proposal_path)
    print(f"  - Bundle years: {len(fis_data.get('bundle_pricing', {}))}")
    print(f"  - Monthly fees: {len(fis_data.get('monthly_fees', []))}")
    print(f"  - One-time items: {len(fis_data.get('one_time_credits', {}))}")

    # Step 2: Send to Claude API for calculations
    print("\n[2/4] Sending to Claude API for TCO calculations...")
    tco_data = get_ai_tco_calculations(fis_data, term, api_key)

    if not tco_data:
        print("ERROR: Failed to get AI calculations")
        return None

    # Step 3: Display summary
    print("\n[3/4] TCO Calculation Summary:")
    summary = tco_data.get('summary', {})

    print("\n  RECURRING COSTS (7-Year):")
    print(f"    Bundle FIS Products:           ${summary.get('bundle_total_7yr', 0):>12,.0f}")
    print(f"    Non-Bundle FIS Required:       ${summary.get('non_bundle_fis_total_7yr', 0):>12,.0f}")
    print(f"    Third-Party Required:          ${summary.get('third_party_total_7yr', 0):>12,.0f}")
    print(f"    -----------------------------------------")
    print(f"    SUBTOTAL RECURRING:            ${summary.get('recurring_subtotal_7yr', 0):>12,.0f}")

    print("\n  ONE-TIME COSTS:")
    print(f"    One-Time Fees:                 ${summary.get('total_one_time_fees', 0):>12,.0f}")
    print(f"    One-Time Credits:             -${summary.get('total_one_time_credits', 0):>12,.0f}")
    print(f"    -----------------------------------------")
    print(f"    NET ONE-TIME:                  ${summary.get('net_one_time', 0):>12,.0f}")

    # Step 4: Populate template
    print("\n[4/4] Populating TCO template...")
    result_path = populate_tco_template(tco_data, template_path, output_path)

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"Output file: {result_path}")

    return tco_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='AI-Enhanced TCO Calculator')
    parser.add_argument('--api-key', type=str, help='Anthropic API key')
    parser.add_argument('--term', type=str, default='7_year',
                       choices=['5_year', '7_year', '10_year'],
                       help='Contract term (default: 7_year)')

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        print("ERROR: Please provide Anthropic API key via --api-key or ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    main(api_key=api_key, term=args.term)
