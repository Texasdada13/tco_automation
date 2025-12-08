"""
Unified Proposal Extraction Script

This script enforces the rule that all extraction JSON files are saved to the "Extracted JSON" folder.

Usage:
    python extract_proposal.py <pdf_file> <vendor_name>

Example:
    python extract_proposal.py "proposal.pdf" "csi"
"""

import sys
import json
from pathlib import Path
from anthropic import Anthropic

from extractors.document_loader import load_document
from extraction_config import get_extraction_output_path, EXTRACTED_JSON_DIR


# HARDCODED API KEY (as per user request from previous sessions)
ANTHROPIC_API_KEY = 'your_anthropic_api_key_here'

def extract_raw_data(pdf_file, vendor_name):
    """
    Extract raw table data from PDF.

    Args:
        pdf_file: Path to PDF file
        vendor_name: Name of vendor (e.g., 'csi', 'fis', 'liberty', 'jh')

    Returns:
        Path to saved raw extraction file
    """
    print('='*80)
    print(f'EXTRACTING RAW DATA: {vendor_name.upper()}')
    print('='*80)
    print(f'Source: {pdf_file}')
    print()

    # Load document
    doc = load_document(pdf_file, apply_ocr=False)

    # Extract tables
    raw_data = {
        'vendor': vendor_name.upper(),
        'source_file': str(pdf_file),
        'document_type': doc.document_type.value,
        'total_pages': doc.page_count,
        'tables': []
    }

    for page_idx, page in enumerate(doc.pages):
        for table_idx, table in enumerate(page.tables):
            table_data = {
                'page_number': page.page_number,
                'table_index': table_idx + 1,
                'rows': len(table),
                'columns': len(table[0]) if table else 0,
                'data': table
            }
            raw_data['tables'].append(table_data)

    # Save to Extracted JSON folder
    output_path = get_extraction_output_path(vendor_name, 'raw')
    with open(output_path, 'w') as f:
        json.dump(raw_data, f, indent=2)

    print(f'Pages: {doc.page_count}')
    print(f'Tables extracted: {len(raw_data["tables"])}')
    print()
    print(f'Saved to: {output_path}')
    print('='*80)

    return output_path


def enhance_with_ai(raw_file_path, vendor_name):
    """
    Enhance raw extraction with Claude AI.

    Args:
        raw_file_path: Path to raw extraction JSON
        vendor_name: Name of vendor

    Returns:
        Path to saved AI-enhanced extraction file
    """
    print()
    print('='*80)
    print(f'ENHANCING WITH AI: {vendor_name.upper()}')
    print('='*80)

    # Load raw data
    with open(raw_file_path, 'r') as f:
        raw_data = json.load(f)

    # Prepare AI prompt
    prompt = f'''You are a financial data extraction expert. Analyze the following raw extracted tables from a {vendor_name.upper()} vendor proposal and transform it into a structured JSON format.

## RAW EXTRACTED DATA:
```json
{json.dumps(raw_data, indent=2)}
```

## YOUR TASK:
Transform this data into a clean, structured JSON with the following requirements:

1. **Identify pricing tables** - Look for tables with pricing information (monthly fees, one-time fees, per-unit rates)
2. **Extract line items** for each service/solution:
   - Solution name
   - Fee type (Monthly F, Monthly V, Annual, One-Time)
   - Monthly fee or per-unit rate
   - One-time implementation fees
   - Category/grouping
   - Whether it's required or optional
   - Whether it's third-party or vendor

3. **Parse per-unit pricing** from any calculation details
4. **Identify contract terms** (contract length in years)
5. **Assign realistic confidence scores** (0.0-1.0) based on clarity
6. **Extract one-time fees/credits** separately

## OUTPUT FORMAT:
Return ONLY valid JSON in this exact structure:
{{
  "vendor": "{vendor_name.upper()}",
  "client": "Extracted client name",
  "proposal_type": "Proposal type",
  "document_date": "Extracted date",
  "contract_term": 7,
  "line_items": [
    {{
      "solution_name": "Clean name",
      "fee_type": "Monthly F" or "Monthly V" or "Annual" or "One-Time",
      "category": "Category name",
      "monthly_fee": 0.0,
      "one_time_fee": 0.0,
      "per_unit_rate": 0.0,
      "unit_description": "per transaction" etc or null,
      "optional": false,
      "third_party": false,
      "overall_confidence": 0.95,
      "extraction_notes": "Any relevant notes"
    }}
  ],
  "summary": {{
    "total_monthly_required": 0.0,
    "total_monthly_optional": 0.0,
    "total_one_time_fees": 0.0,
    "total_one_time_credits": 0.0,
    "items_extracted": 0,
    "average_confidence": 0.0
  }},
  "extraction_metadata": {{
    "model": "claude-sonnet-4-20250514",
    "extraction_method": "ai_enhanced",
    "source_tables_processed": {len(raw_data.get('tables', []))}
  }}
}}

Return ONLY the JSON, no additional text.'''

    # Call Claude API
    print('Sending to Claude API...')
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=16000,
        temperature=0.0,
        messages=[{'role': 'user', 'content': prompt}]
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
        output_path = get_extraction_output_path(vendor_name, 'ai')
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print()
        print('AI EXTRACTION COMPLETE')
        print('-'*80)
        print(f'Vendor: {result.get("vendor", "Unknown")}')
        print(f'Client: {result.get("client", "Unknown")}')
        print(f'Line items: {len(result.get("line_items", []))}')
        print(f'Tokens used: {response.usage.input_tokens + response.usage.output_tokens}')
        print()
        print(f'Saved to: {output_path}')
        print('='*80)

        return output_path

    except json.JSONDecodeError as e:
        print(f'ERROR: JSON parse error: {e}')
        print(f'Response preview: {response_text[:500]}...')
        return None


def extract_proposal(pdf_file, vendor_name):
    """
    Complete extraction pipeline: raw extraction + AI enhancement.

    Args:
        pdf_file: Path to PDF file
        vendor_name: Name of vendor

    Returns:
        Tuple of (raw_path, ai_path)
    """
    # Step 1: Extract raw data
    raw_path = extract_raw_data(pdf_file, vendor_name)

    # Step 2: Enhance with AI
    ai_path = enhance_with_ai(raw_path, vendor_name)

    print()
    print('='*80)
    print('EXTRACTION COMPLETE')
    print('='*80)
    print(f'Raw extraction: {raw_path}')
    print(f'AI extraction: {ai_path}')
    print()
    print(f'All files saved to: {EXTRACTED_JSON_DIR}')
    print('='*80)

    return raw_path, ai_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_proposal.py <pdf_file> <vendor_name>")
        print()
        print("Example:")
        print("  python extract_proposal.py 'proposal.pdf' 'csi'")
        print()
        print("Vendor names: fis, csi, jh, liberty, etc.")
        sys.exit(1)

    pdf_file = sys.argv[1]
    vendor_name = sys.argv[2]

    if not Path(pdf_file).exists():
        print(f"ERROR: File not found: {pdf_file}")
        sys.exit(1)

    extract_proposal(pdf_file, vendor_name)
