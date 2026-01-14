"""
Direct PDF to Claude API Extraction
Sends PDF directly to Claude without intermediate table parsing.
Works much better for complex layouts like FIS proposals.

Usage:
    python extract_proposal_direct.py <pdf_file> <vendor_name>

Example:
    python extract_proposal_direct.py "proposal.pdf" "fis"
"""

import sys
import json
from pathlib import Path
from anthropic import Anthropic
import base64

from extraction_config import get_extraction_output_path

import os
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables or .env file")


def extract_with_claude_direct(pdf_file, vendor_name):
    """
    Extract proposal data by sending PDF directly to Claude API.

    Args:
        pdf_file: Path to PDF file
        vendor_name: Name of vendor (e.g., 'csi', 'fis', 'liberty', 'jh')

    Returns:
        Path to saved extraction file
    """
    print('='*80)
    print(f'DIRECT EXTRACTION WITH CLAUDE: {vendor_name.upper()}')
    print('='*80)
    print(f'Source: {pdf_file}')
    print()

    # Read PDF file
    with open(pdf_file, 'rb') as f:
        pdf_data = base64.standard_b64encode(f.read()).decode('utf-8')

    # Prepare detailed extraction prompt
    prompt = f"""You are a financial data extraction expert. Analyze this {vendor_name.upper()} vendor proposal PDF and extract ALL pricing information into structured JSON.

## IMPORTANT INSTRUCTIONS:

1. **Extract EVERY line item** - Don't summarize or group items. Extract each individual service with its specific pricing.

2. **Preserve exact naming** - Use the exact service names from the proposal (e.g., "HORIZON Core Account Processing Service Bureau (SB)", "FIS EFT Processing - PaymentsOne", "SecurLOCK™ Processing")

3. **Capture all fee types:**
   - Monthly Fixed (Monthly F)
   - Monthly Variable (Monthly V)
   - Annual fees
   - One-Time/Implementation fees
   - Per-unit rates and volume tiers

4. **Extract detailed pricing:**
   - Base monthly fees
   - Per-transaction/per-account rates
   - Graduated/tiered pricing (e.g., "0-5,000: $0.39, 5,001-10,000: $0.43")
   - Volume information
   - Minimum fees

5. **Identify categories:**
   - Core Processing
   - e-Banking/Digital Banking
   - ATM/EFT Services
   - Item Processing
   - Risk/Fraud/Compliance
   - Card Services
   - Other Services

6. **Extract metadata:**
   - Client name
   - Proposal date
   - Contract term
   - Current vs Proposed pricing (if shown)
   - Monthly relationship credits
   - Implementation/migration fees

7. **Calculate totals:**
   - Total monthly required fees
   - Total monthly optional fees
   - Total one-time fees
   - Total credits/discounts

## OUTPUT FORMAT:

Return a comprehensive JSON with this structure:

```json
{{
  "vendor": "{vendor_name.upper()}",
  "client": "Extract client name",
  "proposal_date": "Extract date",
  "contract_term": 7,
  "line_items": [
    {{
      "solution_name": "Exact service name from proposal",
      "category": "Category name",
      "fee_type": "Monthly F|Monthly V|Annual|One-Time",
      "current_monthly_fee": 0.0,
      "proposed_monthly_fee": 0.0,
      "one_time_fee": 0.0,
      "per_unit_rate": 0.0,
      "unit_description": "per transaction|per account|etc",
      "volume": 0,
      "graduated_pricing": [
        {{"tier": "0-5000", "rate": 0.39}},
        {{"tier": "5001-10000", "rate": 0.43}}
      ],
      "minimum_fee": 0.0,
      "optional": false,
      "third_party": false,
      "description": "Additional notes",
      "page_number": 2
    }}
  ],
  "summary": {{
    "total_current_monthly": 0.0,
    "total_proposed_monthly": 0.0,
    "total_one_time_fees": 0.0,
    "total_credits": 0.0,
    "net_monthly_change": 0.0,
    "items_extracted": 0
  }},
  "implementation_fees": [
    {{
      "description": "Core Migration SOWs",
      "amount": 144600.0,
      "waived": true
    }}
  ],
  "credits_and_incentives": [
    {{
      "description": "Monthly Relationship Credit",
      "amount": -25000.0,
      "type": "Monthly"
    }}
  ],
  "extraction_metadata": {{
    "model": "claude-sonnet-4-20250514",
    "extraction_method": "direct_pdf",
    "total_pages": 0
  }}
}}
```

## CRITICAL RULES:
- Extract EVERY service line item, don't skip any
- Use exact names from the proposal
- Include both Current and Proposed fees where shown
- Capture graduated/tiered pricing structures
- Note which items are optional vs required
- Include page numbers for reference
- Be thorough - this proposal likely has 50-200+ line items

Return ONLY valid JSON, no additional text."""

    # Call Claude API with PDF
    print('Sending PDF to Claude API...')
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=16000,
        temperature=0.0,
        messages=[
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'document',
                        'source': {
                            'type': 'base64',
                            'media_type': 'application/pdf',
                            'data': pdf_data
                        }
                    },
                    {
                        'type': 'text',
                        'text': prompt
                    }
                ]
            }
        ]
    )

    response_text = response.content[0].text

    # Extract JSON from response
    if '```json' in response_text:
        start = response_text.find('```json') + 7
        end = response_text.find('```', start)
        response_text = response_text[start:end].strip()
    elif '```' in response_text:
        start = response_text.find('```') + 3
        end = response_text.find('```', start)
        response_text = response_text[start:end].strip()

    try:
        result = json.loads(response_text)

        # Save to Extracted JSON folder
        output_path = get_extraction_output_path(vendor_name, 'direct')
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print()
        print('DIRECT EXTRACTION COMPLETE')
        print('-'*80)
        print(f'Vendor: {result.get("vendor", "Unknown")}')
        print(f'Client: {result.get("client", "Unknown")}')
        print(f'Line items extracted: {len(result.get("line_items", []))}')
        print(f'Total pages: {result.get("extraction_metadata", {}).get("total_pages", "Unknown")}')
        print(f'Tokens used: {response.usage.input_tokens + response.usage.output_tokens}')
        print()
        print(f'Saved to: {output_path}')
        print('='*80)

        return output_path

    except json.JSONDecodeError as e:
        print(f'ERROR: JSON parse error: {e}')
        print(f'Response preview: {response_text[:500]}...')

        # Save raw response for debugging
        error_path = get_extraction_output_path(vendor_name, 'direct_error')
        with open(error_path, 'w') as f:
            f.write(response_text)
        print(f'Raw response saved to: {error_path}')

        return None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_proposal_direct.py <pdf_file> <vendor_name>")
        print()
        print("Example:")
        print("  python extract_proposal_direct.py 'proposal.pdf' 'fis'")
        print()
        print("Vendor names: fis, csi, jh, liberty, etc.")
        sys.exit(1)

    pdf_file = sys.argv[1]
    vendor_name = sys.argv[2]

    if not Path(pdf_file).exists():
        print(f"ERROR: File not found: {pdf_file}")
        sys.exit(1)

    extract_with_claude_direct(pdf_file, vendor_name)
