"""
Hybrid PDF Extraction - Text + Vision Analysis
Combines text extraction with Claude's vision capabilities for maximum accuracy.

Usage:
    python extract_proposal_hybrid.py <pdf_file> <vendor_name>
"""

import sys
import json
from pathlib import Path
from anthropic import Anthropic
import base64
import fitz  # PyMuPDF

from extraction_config import get_extraction_output_path

import os
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables or .env file")


def pdf_pages_to_images(pdf_path, dpi=150):
    """
    Convert PDF pages to images for vision analysis.

    Args:
        pdf_path: Path to PDF
        dpi: Resolution (150 is good balance between quality and token usage)

    Returns:
        List of base64-encoded PNG images
    """
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render page to image (2.0 zoom = ~150 DPI)
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PNG bytes
        img_bytes = pix.tobytes("png")
        img_base64 = base64.standard_b64encode(img_bytes).decode('utf-8')

        images.append({
            'page_number': page_num + 1,
            'image': img_base64
        })

    doc.close()
    return images


def extract_hybrid(pdf_file, vendor_name, max_pages=None):
    """
    Extract using both PDF document and page images.

    Args:
        pdf_file: Path to PDF file
        vendor_name: Name of vendor
        max_pages: Limit to first N pages for testing (None = all pages)

    Returns:
        Path to saved extraction file
    """
    print('='*80)
    print(f'HYBRID EXTRACTION (PDF + VISION): {vendor_name.upper()}')
    print('='*80)
    print(f'Source: {pdf_file}')
    print()

    # Read PDF as document
    with open(pdf_file, 'rb') as f:
        pdf_data = base64.standard_b64encode(f.read()).decode('utf-8')

    # Convert key pages to images (pages with pricing tables)
    print('Converting pricing pages to images...')
    all_images = pdf_pages_to_images(pdf_file)

    if max_pages:
        all_images = all_images[:max_pages]

    # Focus on pages 2-10 (typically where pricing tables are)
    pricing_images = all_images[1:min(10, len(all_images))]

    print(f'Extracted {len(pricing_images)} pricing table pages as images')

    # Build message content with PDF + images of key pages
    content = [
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
            'text': f"""You are analyzing a {vendor_name.upper()} vendor proposal. I'm providing:
1. The full PDF document
2. High-resolution images of the key pricing table pages

Please extract ALL pricing line items with complete details.

Focus on these pages which contain the detailed pricing tables:
Pages 2-10 (Executive Summary and detailed service breakdowns)

Extract every single line item with:
- Exact service name
- Category
- Current fee (if shown)
- Proposed fee
- One-time fees
- Per-unit rates and volumes
- Graduated pricing tiers
- Whether optional or required

Return comprehensive JSON with this structure:
{{
  "vendor": "{vendor_name.upper()}",
  "client": "Extract from page 1 or 2",
  "proposal_date": "Extract date",
  "contract_term": 7,
  "line_items": [
    {{
      "solution_name": "Exact name",
      "category": "Category",
      "fee_type": "Monthly F|Monthly V|Annual|One-Time",
      "current_monthly_fee": 0.0,
      "proposed_monthly_fee": 0.0,
      "one_time_fee": 0.0,
      "per_unit_rate": 0.0,
      "unit_description": "per X",
      "volume": 0,
      "graduated_pricing": [{{"tier": "0-1000", "rate": 0.50}}],
      "minimum_fee": 0.0,
      "optional": false,
      "third_party": false,
      "page_number": 2
    }}
  ],
  "summary": {{
    "total_current_monthly": 0.0,
    "total_proposed_monthly": 0.0,
    "total_one_time_fees": 0.0,
    "items_extracted": 0
  }}
}}

Extract EVERY line item - don't summarize or group. Return only valid JSON."""
        }
    ]

    # Add page images
    for img_data in pricing_images:
        content.append({
            'type': 'text',
            'text': f"\n--- Page {img_data['page_number']} (Image) ---"
        })
        content.append({
            'type': 'image',
            'source': {
                'type': 'base64',
                'media_type': 'image/png',
                'data': img_data['image']
            }
        })

    # Call Claude API
    print('Sending to Claude API (this may take a moment)...')
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=16000,
        temperature=0.0,
        messages=[{'role': 'user', 'content': content}]
    )

    response_text = response.content[0].text

    # Extract JSON
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

        # Save
        output_path = get_extraction_output_path(vendor_name, 'hybrid')
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print()
        print('HYBRID EXTRACTION COMPLETE')
        print('-'*80)
        print(f'Vendor: {result.get("vendor", "Unknown")}')
        print(f'Client: {result.get("client", "Unknown")}')
        print(f'Line items extracted: {len(result.get("line_items", []))}')
        print(f'Tokens used: {response.usage.input_tokens + response.usage.output_tokens}')
        print()
        print(f'Saved to: {output_path}')
        print('='*80)

        return output_path

    except json.JSONDecodeError as e:
        print(f'ERROR: JSON parse error: {e}')
        print(f'Response preview: {response_text[:500]}...')

        error_path = get_extraction_output_path(vendor_name, 'hybrid_error')
        with open(error_path, 'w') as f:
            f.write(response_text)
        print(f'Raw response saved to: {error_path}')

        return None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python extract_proposal_hybrid.py <pdf_file> <vendor_name> [max_pages]")
        print()
        print("Example:")
        print("  python extract_proposal_hybrid.py 'proposal.pdf' 'fis'")
        print("  python extract_proposal_hybrid.py 'proposal.pdf' 'fis' 5  # Test with first 5 pages")
        sys.exit(1)

    pdf_file = sys.argv[1]
    vendor_name = sys.argv[2]
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else None

    if not Path(pdf_file).exists():
        print(f"ERROR: File not found: {pdf_file}")
        sys.exit(1)

    extract_hybrid(pdf_file, vendor_name, max_pages)
