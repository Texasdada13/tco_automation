"""
Integrated TCO Extraction Pipeline

This is the main entry point for TCO proposal extraction with full automation:
1. Document loading and raw extraction
2. AI-enhanced extraction via Claude
3. QA validation with confidence scoring
4. Word format QA report generation
5. Cost normalization to 6-bucket taxonomy (apples-to-apples comparison)
6. Status tracking and history
7. Standardized output folder structure

Usage:
    python extract_pipeline.py <proposal_file> [vendor_name] [client_name]

Examples:
    python extract_pipeline.py "proposal.docx" "FIS" "First National Bank"
    python extract_pipeline.py "proposal.pdf"  # Auto-detect vendor

The pipeline produces:
    ./output/YYYY-MM-DD/{vendor}_{client}/
        ├── input/original_proposal.*
        ├── extraction/raw_extraction.json
        ├── extraction/ai_extraction.json
        ├── extraction/normalized_extraction.json  (NEW: 6-bucket normalized)
        ├── validation/qa_report.json
        ├── validation/qa_report.docx
        ├── output/TCO_Workbook.xlsx
        └── audit/traceability.json
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anthropic import Anthropic
from dotenv import load_dotenv

# Core modules
from core.output_manager import get_output_manager, ExtractionPaths
from core.vendor_config import get_vendor_manager
from core.status_tracker import get_status_tracker, ExtractionStatus
from core.qa_report_generator import QAReportGenerator, generate_qa_reports
from core.cost_normalizer import CostNormalizer, get_bucket_display_order
from core.normalized_excel_sheet import add_normalized_sheet

# Extractors
from extractors.document_loader import load_document

# TCO Workbook population
from populate_tco_workbook import populate_workbook
from extraction_config import TCO_OUTPUT_DIR

# Load environment
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedPipeline:
    """
    Full TCO extraction pipeline with QA and reporting.
    """

    def __init__(self, output_base_dir: str = None):
        """
        Initialize the pipeline.

        Args:
            output_base_dir: Base directory for outputs (default: ./output)
        """
        self.output_manager = get_output_manager(output_base_dir)
        self.vendor_manager = get_vendor_manager()
        self.status_tracker = get_status_tracker(output_base_dir)
        self.qa_generator = QAReportGenerator()
        self.cost_normalizer = CostNormalizer()  # 6-bucket normalization

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

        logger.info("IntegratedPipeline initialized")

    def process(
        self,
        source_file: str,
        vendor: str = None,
        client: str = None
    ) -> dict:
        """
        Process a proposal through the full pipeline.

        Args:
            source_file: Path to proposal file
            vendor: Vendor name (auto-detected if not provided)
            client: Client name (extracted from filename if not provided)

        Returns:
            Dict with extraction results and paths
        """
        source_path = Path(source_file)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")

        print("\n" + "=" * 70)
        print("TCO EXTRACTION PIPELINE")
        print("=" * 70)
        print(f"Source: {source_path.name}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # === STEP 1: Vendor Detection ===
        print("\n[1/8] Detecting vendor...")

        if not vendor:
            # Try to detect from filename
            detected_vendor, confidence = self.vendor_manager.detect_vendor(
                filename=source_path.name
            )
            if detected_vendor:
                vendor = detected_vendor
                print(f"  Detected: {vendor} (confidence: {confidence:.0%})")
            else:
                vendor = "Unknown"
                print(f"  Could not detect vendor, using: {vendor}")
        else:
            print(f"  Using provided vendor: {vendor}")

        # Get vendor config
        vendor_config = self.vendor_manager.get_vendor_config(vendor)

        # === STEP 2: Extract client name ===
        if not client:
            # Try to extract from filename
            client = self._extract_client_from_filename(source_path.name, vendor)
            print(f"  Client: {client}")

        # === STEP 3: Create output folder structure ===
        print("\n[2/8] Creating output structure...")

        paths = self.output_manager.create_extraction_folder(
            vendor=vendor,
            client=client,
            source_file=str(source_path)
        )
        print(f"  Output: {paths.extraction_dir}")

        # Start tracking
        record_id = self.status_tracker.start_extraction(
            file_name=source_path.name,
            vendor=vendor,
            client=client
        )

        try:
            # === STEP 4: Raw extraction ===
            print("\n[3/8] Extracting raw data...")

            raw_data = self._extract_raw_data(source_path, vendor)

            # Save raw extraction
            with open(paths.raw_extraction, 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, indent=2)
            print(f"  Tables found: {len(raw_data.get('tables', []))}")
            print(f"  Saved: {Path(paths.raw_extraction).name}")

            # === STEP 5: AI Enhancement ===
            print("\n[4/8] AI-enhanced extraction...")

            ai_data = self._enhance_with_ai(raw_data, vendor, client, vendor_config)

            # Save AI extraction
            with open(paths.ai_extraction, 'w', encoding='utf-8') as f:
                json.dump(ai_data, f, indent=2)

            items_count = len(ai_data.get('line_items', []))
            print(f"  Line items extracted: {items_count}")
            print(f"  Saved: {Path(paths.ai_extraction).name}")

            # === STEP 6: QA Validation ===
            print("\n[5/8] Running QA validation...")

            qa_metrics = self.qa_generator.analyze_extraction(ai_data, vendor)

            # Generate QA reports
            qa_paths = generate_qa_reports(
                extraction_data=ai_data,
                json_output_path=paths.qa_report_json,
                word_output_path=paths.qa_report_docx,
                vendor=vendor,
                client=client,
                source_file=source_path.name
            )

            print(f"  Average confidence: {qa_metrics.average_confidence:.1%}")
            print(f"  Auto-approved: {qa_metrics.items_auto_approved}")
            print(f"  Need review: {qa_metrics.items_need_review}")
            print(f"  QA Report: {Path(paths.qa_report_docx).name}")

            # === STEP 6.5: Cost Normalization (Apples-to-Apples) ===
            print("\n[6/8] Normalizing to 6-bucket taxonomy...")

            normalized_proposal = self.cost_normalizer.normalize_proposal(
                extraction_data=ai_data,
                source_file=str(source_path)
            )

            # Save normalized extraction
            normalized_path = Path(paths.extraction_subdir) / "normalized_extraction.json"
            self.cost_normalizer.export_to_json(normalized_proposal, str(normalized_path))

            # Print bucket summary
            print(f"  Normalized {len(normalized_proposal.line_items)} items to 6 buckets:")
            for bucket in get_bucket_display_order():
                bucket_data = normalized_proposal.bucket_totals.get(bucket.value, {})
                item_count = bucket_data.get("item_count", 0)
                total_7yr = bucket_data.get("total_7_year", 0)
                if item_count > 0:
                    print(f"    - {bucket.value}: {item_count} items, ${total_7yr:,.0f} (7yr)")

            # Print cost-per-unit metrics
            print(f"  Cost-per-unit metrics:")
            for metric_name, value in normalized_proposal.normalized_metrics.items():
                if value > 0:
                    print(f"    - {metric_name}: ${value:,.2f}")

            # === STEP 7: Generate TCO Excel Workbook ===
            print("\n[7/8] Generating TCO Excel workbook...")

            # Generate output filename: CLIENT_VENDOR_TCO_New_YYYYMMDD.xlsx
            date_str = datetime.now().strftime('%Y%m%d')
            client_clean = client.upper().replace(' ', '_')
            excel_filename = f"{client_clean}_{vendor.upper()}_TCO_New_{date_str}.xlsx"
            excel_path = TCO_OUTPUT_DIR / excel_filename

            # Use WORKBOOK2.xlsx template to create full TCO workbook
            template_path = Path(__file__).parent / "WORKBOOK2.xlsx"

            if template_path.exists():
                # Populate TCO workbook from template using AI extraction data
                print(f"  Using template: WORKBOOK2.xlsx")
                excel_path, mapping_report = populate_workbook(
                    json_file=paths.ai_extraction,
                    template_file=str(template_path),
                    output_file=str(excel_path)
                )
                print(f"  Populated {len(mapping_report)} line items to TCO workbook")
            else:
                # Fallback: create basic workbook if template not found
                print(f"  WARNING: Template WORKBOOK2.xlsx not found, creating basic workbook")
                from openpyxl import Workbook
                wb = Workbook()
                wb.save(str(excel_path))

            # Load the normalized data and add comparison sheet
            with open(str(normalized_path), 'r', encoding='utf-8') as f:
                normalized_json = json.load(f)

            # Add the normalized comparison sheet to the TCO workbook
            add_normalized_sheet(str(excel_path), normalized_json)
            print(f"  TCO Workbook: {excel_path}")
            print(f"  Added 'Normalized Comparison' sheet with 6-bucket analysis")

            # === STEP 8: Save audit trail ===
            print("\n[8/8] Saving audit trail...")

            audit_data = {
                'extraction_id': record_id,
                'source_file': str(source_path),
                'vendor': vendor,
                'client': client,
                'timestamp': datetime.now().isoformat(),
                'pipeline_version': '2.1',  # Updated for normalization support
                'stages': {
                    'raw_extraction': {
                        'tables_found': len(raw_data.get('tables', [])),
                        'pages': raw_data.get('total_pages', 0)
                    },
                    'ai_enhancement': {
                        'model': 'claude-sonnet-4-20250514',
                        'items_extracted': items_count
                    },
                    'qa_validation': {
                        'average_confidence': qa_metrics.average_confidence,
                        'items_auto_approved': qa_metrics.items_auto_approved,
                        'items_need_review': qa_metrics.items_need_review,
                        'validation_errors': len(qa_metrics.validation_errors),
                        'warnings': len(qa_metrics.warnings)
                    },
                    'cost_normalization': {
                        'taxonomy_version': '1.0',
                        'buckets_used': len([b for b in normalized_proposal.bucket_totals if normalized_proposal.bucket_totals[b].get('item_count', 0) > 0]),
                        'total_items_normalized': len(normalized_proposal.line_items),
                        'bucket_summary': {
                            bucket.value: {
                                'item_count': normalized_proposal.bucket_totals.get(bucket.value, {}).get('item_count', 0),
                                'total_7_year': normalized_proposal.bucket_totals.get(bucket.value, {}).get('total_7_year', 0)
                            }
                            for bucket in get_bucket_display_order()
                        },
                        'normalized_metrics': normalized_proposal.normalized_metrics
                    }
                },
                'outputs': {
                    'raw_extraction': paths.raw_extraction,
                    'ai_extraction': paths.ai_extraction,
                    'normalized_extraction': str(normalized_path),
                    'tco_excel_workbook': str(excel_path),
                    'qa_report_json': paths.qa_report_json,
                    'qa_report_docx': paths.qa_report_docx
                }
            }

            with open(paths.traceability_json, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2)
            print(f"  Audit trail saved")

            # === Update status tracker ===
            self.status_tracker.complete_extraction(
                record_id=record_id,
                success=True,
                confidence=qa_metrics.average_confidence,
                items_extracted=items_count,
                items_need_review=qa_metrics.items_need_review,
                output_path=paths.extraction_dir,
                qa_report_path=paths.qa_report_docx
            )

            # === Summary ===
            print("\n" + "=" * 70)
            print("EXTRACTION COMPLETE")
            print("=" * 70)

            status_icon = "[OK]" if qa_metrics.average_confidence >= 0.90 else "[REVIEW]" if qa_metrics.average_confidence >= 0.70 else "[FAIL]"
            print(f"{status_icon} Status: {'SUCCESS' if qa_metrics.average_confidence >= 0.70 else 'NEEDS REVIEW'}")
            print(f"  Confidence: {qa_metrics.average_confidence:.1%}")
            print(f"  Items: {items_count} total, {qa_metrics.items_need_review} need review")
            print()
            print("Output files:")
            print(f"  Raw extraction:       {paths.raw_extraction}")
            print(f"  AI extraction:        {paths.ai_extraction}")
            print(f"  Normalized (6-bucket): {normalized_path}")
            print(f"  TCO Excel Workbook:   {excel_path}")
            print(f"  QA Report (JSON):     {paths.qa_report_json}")
            print(f"  QA Report (Word):     {paths.qa_report_docx}")
            print("=" * 70)

            return {
                'success': True,
                'record_id': record_id,
                'vendor': vendor,
                'client': client,
                'paths': {
                    **paths.to_dict(),
                    'normalized_extraction': str(normalized_path)
                },
                'metrics': {
                    'items_extracted': items_count,
                    'average_confidence': qa_metrics.average_confidence,
                    'items_auto_approved': qa_metrics.items_auto_approved,
                    'items_need_review': qa_metrics.items_need_review
                },
                'normalization': {
                    'bucket_totals': {
                        bucket.value: normalized_proposal.bucket_totals.get(bucket.value, {})
                        for bucket in get_bucket_display_order()
                    },
                    'cost_per_unit_metrics': normalized_proposal.normalized_metrics
                }
            }

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")

            self.status_tracker.complete_extraction(
                record_id=record_id,
                success=False,
                confidence=0,
                items_extracted=0,
                items_need_review=0,
                error_message=str(e)
            )

            print(f"\n[FAIL] EXTRACTION FAILED: {e}")
            raise

    def _extract_client_from_filename(self, filename: str, vendor: str) -> str:
        """Extract client name from filename."""
        # Remove extension
        name = Path(filename).stem

        # Remove common patterns
        patterns_to_remove = [
            vendor.lower(), 'proposal', 'investment', 'summary',
            'renewal', 'quote', 'deal', 'sheet', '2025', '2024', '2026',
            '_', '-'
        ]

        clean_name = name.lower()
        for pattern in patterns_to_remove:
            clean_name = clean_name.replace(pattern.lower(), ' ')

        # Clean up whitespace
        clean_name = ' '.join(clean_name.split())

        if clean_name.strip():
            return clean_name.strip().title()
        else:
            return "Unknown Client"

    def _extract_raw_data(self, source_path: Path, vendor: str) -> dict:
        """Extract raw data from document."""
        doc = load_document(str(source_path), apply_ocr=False)

        raw_data = {
            'vendor': vendor.upper(),
            'source_file': str(source_path),
            'document_type': doc.document_type.value,
            'total_pages': doc.page_count,
            'extracted_at': datetime.now().isoformat(),
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

        return raw_data

    def _enhance_with_ai(
        self,
        raw_data: dict,
        vendor: str,
        client: str,
        vendor_config
    ) -> dict:
        """Enhance extraction with Claude AI."""
        prompt = f'''You are a financial data extraction expert. Analyze the following raw extracted tables from a {vendor.upper()} vendor proposal and transform it into a structured JSON format.

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

## CATEGORY CLASSIFICATION:
Use these standard categories:
- Core (core banking, primary platform)
- Digital (online, mobile banking)
- EFT (debit cards, ATM, electronic transfers)
- Treasury (wire, cash management)
- Lending (loan systems)
- Risk, Fraud & Compliance (security, compliance)
- Image Solutions (imaging, document management)
- Item Processing (check processing)
- ACH (ACH processing)
- Other (anything that doesn't fit above)

## OUTPUT FORMAT:
Return ONLY valid JSON in this exact structure:
{{
  "vendor": "{vendor.upper()}",
  "client": "{client}",
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

        response = self.client.messages.create(
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

        return json.loads(response_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='TCO Extraction Pipeline - Full automation with QA reporting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python extract_pipeline.py proposal.docx FIS "First National Bank"
  python extract_pipeline.py proposal.pdf  # Auto-detect vendor
  python extract_pipeline.py --status  # Show pipeline status
        '''
    )

    parser.add_argument('source_file', nargs='?', help='Path to proposal file')
    parser.add_argument('vendor', nargs='?', help='Vendor name (optional, auto-detected)')
    parser.add_argument('client', nargs='?', help='Client name (optional)')
    parser.add_argument('--status', action='store_true', help='Show pipeline status')
    parser.add_argument('--output-dir', default='./output', help='Base output directory')

    args = parser.parse_args()

    if args.status:
        from core.status_tracker import print_pipeline_status
        print_pipeline_status()
        return

    if not args.source_file:
        parser.print_help()
        print("\nError: source_file is required")
        sys.exit(1)

    # Run pipeline
    pipeline = IntegratedPipeline(output_base_dir=args.output_dir)

    try:
        result = pipeline.process(
            source_file=args.source_file,
            vendor=args.vendor,
            client=args.client
        )
        sys.exit(0 if result['success'] else 1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
