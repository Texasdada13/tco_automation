#!/usr/bin/env python3
"""
QA Validator for TCO Automation System

This script validates the extraction and population process by:
1. Comparing source data to extracted data
2. Verifying TCO template population
3. Checking calculations and formulas
4. Generating detailed QA reports
"""

import sys
import json
from openpyxl import load_workbook
from docx import Document
from extractors import extract_fis_proposal, extract_jack_henry_proposal
from extractors.jh_extractor import JackHenryExtractor
from mappers import normalize_vendor_data
from config import TCO_COLUMNS
from cell_validator import CellByCellValidator


class TCOValidator:
    """Validates TCO automation output"""
    
    def __init__(self):
        self.validation_results = {
            'extraction': {},
            'mapping': {},
            'population': {},
            'calculations': {},
            'cell_validation': {},
            'coverage': {},
            'overall_pass': True
        }
    
    def validate_fis_extraction(self, proposal_path: str, expected_counts: dict = None):
        """
        Validate FIS extraction
        
        Args:
            proposal_path: Path to FIS proposal
            expected_counts: Optional dict with expected counts for validation
                            {'tables': 9, 'bundle_years': 7, 'monthly_fees': 30, 'one_time_credits': 7}
        """
        print("\n" + "="*70)
        print("QA CHECK: FIS EXTRACTION")
        print("="*70)
        
        results = {'pass': True, 'issues': []}
        
        try:
            # Extract data
            data = extract_fis_proposal(proposal_path)
            
            # Check bundle pricing
            bundle_years = len(data['bundle_pricing'])
            print(f"[OK] Bundle years extracted: {bundle_years}")
            
            if expected_counts and 'bundle_years' in expected_counts:
                if bundle_years != expected_counts['bundle_years']:
                    results['pass'] = False
                    results['issues'].append(
                        f"Expected {expected_counts['bundle_years']} bundle years, got {bundle_years}"
                    )
            
            # Check monthly fees
            monthly_count = len(data['monthly_fees'])
            print(f"[OK] Monthly fees extracted: {monthly_count}")
            
            if expected_counts and 'monthly_fees' in expected_counts:
                if monthly_count < expected_counts['monthly_fees'] * 0.8:  # Allow 20% variance
                    results['pass'] = False
                    results['issues'].append(
                        f"Expected ~{expected_counts['monthly_fees']} monthly fees, got {monthly_count}"
                    )
            
            # Check one-time credits
            credits_count = len(data['one_time_credits'])
            print(f"[OK] One-time credits extracted: {credits_count}")
            
            # Verify no empty/null critical fields
            for year, prices in data['bundle_pricing'].items():
                if not any(prices.values()):
                    results['pass'] = False
                    results['issues'].append(f"Bundle pricing for {year} is all zeros")
            
            # Check for reasonable values (bundle pricing should be > 0)
            bundle_values = []
            for year, prices in data['bundle_pricing'].items():
                for term, value in prices.items():
                    if value > 0:
                        bundle_values.append(value)
            
            if bundle_values:
                avg_bundle = sum(bundle_values) / len(bundle_values)
                print(f"[OK] Average bundle price: ${avg_bundle:,.2f}/month")
                
                if avg_bundle < 1000 or avg_bundle > 100000:
                    results['issues'].append(
                        f"Warning: Average bundle price ${avg_bundle:,.2f} seems unusual"
                    )
            
            results['extracted_data'] = {
                'bundle_years': bundle_years,
                'monthly_fees': monthly_count,
                'one_time_credits': credits_count
            }
            
        except Exception as e:
            results['pass'] = False
            results['issues'].append(f"Extraction failed: {str(e)}")
        
        self.validation_results['extraction']['FIS'] = results
        
        if results['pass']:
            print("\n[PASS] FIS extraction validation PASSED")
        else:
            print("\n[FAIL] FIS extraction validation FAILED")
            for issue in results['issues']:
                print(f"   - {issue}")
        
        return results['pass']
    
    def validate_jh_extraction(self, proposal_path: str, expected_counts: dict = None):
        """
        Validate Jack Henry extraction
        
        Args:
            proposal_path: Path to JH proposal
            expected_counts: Optional dict with expected counts
                            {'products': 170, 'scenarios': 3}
        """
        print("\n" + "="*70)
        print("QA CHECK: JACK HENRY EXTRACTION")
        print("="*70)
        
        results = {'pass': True, 'issues': []}
        
        try:
            # Extract data
            data = extract_jack_henry_proposal(proposal_path)
            
            # Check scenarios
            scenarios_count = len(data['scenarios'])
            print(f"[OK] Scenarios extracted: {scenarios_count}")
            
            if expected_counts and 'scenarios' in expected_counts:
                if scenarios_count != expected_counts['scenarios']:
                    results['pass'] = False
                    results['issues'].append(
                        f"Expected {expected_counts['scenarios']} scenarios, got {scenarios_count}"
                    )
            
            # Check products in each scenario
            for scenario in data['scenarios']:
                product_count = len(scenario['products'])
                print(f"[OK] {scenario['scenario_name']}: {product_count} products")
                
                if product_count == 0:
                    results['pass'] = False
                    results['issues'].append(f"{scenario['scenario_name']} has 0 products")
            
            # Verify product data integrity
            if data['scenarios']:
                sample_products = data['scenarios'][0]['products'][:5]
                for product in sample_products:
                    if not product.get('product_description'):
                        results['issues'].append("Found product with no description")
                    
                    # Check that at least one fee type exists
                    fees = [
                        product.get('license_net', 0),
                        product.get('install_net', 0),
                        product.get('maintenance_net', 0),
                        product.get('monthly_net', 0)
                    ]
                    if sum(fees) == 0:
                        results['issues'].append(
                            f"Product '{product.get('product_description', 'Unknown')}' has all zero fees"
                        )
            
            # Check summary data
            if 'summary' in data:
                monthly_net = data['summary'].get('total_monthly_net', 0)
                print(f"[OK] Total monthly net from summary: ${monthly_net:,.2f}")
            
            results['extracted_data'] = {
                'scenarios': scenarios_count,
                'total_products': sum(s['product_count'] for s in data['scenarios'])
            }
            
        except Exception as e:
            results['pass'] = False
            results['issues'].append(f"Extraction failed: {str(e)}")
        
        self.validation_results['extraction']['Jack Henry'] = results
        
        if results['pass']:
            print("\n[PASS] Jack Henry extraction validation PASSED")
        else:
            print("\n[FAIL] Jack Henry extraction validation FAILED")
            for issue in results['issues']:
                print(f"   - {issue}")
        
        return results['pass']
    
    def validate_mapping(self, extracted_data: dict, vendor: str):
        """Validate data normalization/mapping"""
        print("\n" + "="*70)
        print(f"QA CHECK: {vendor.upper()} DATA MAPPING")
        print("="*70)
        
        results = {'pass': True, 'issues': []}
        
        try:
            # Normalize data
            normalized = normalize_vendor_data(extracted_data, vendor)
            
            print(f"[OK] Mapped {len(normalized)} line items")
            
            # Check required fields
            required_fields = ['solution_name', 'fee_type', 'category', 'vendor']
            
            for idx, item in enumerate(normalized):
                for field in required_fields:
                    if field not in item or not item[field]:
                        results['pass'] = False
                        results['issues'].append(
                            f"Line item {idx+1} missing {field}"
                        )
                
                # Check fee types are valid
                if item['fee_type'] not in ['Monthly F', 'Monthly V', 'Annual', 'One-Time']:
                    results['pass'] = False
                    results['issues'].append(
                        f"Invalid fee type '{item['fee_type']}' for {item['solution_name']}"
                    )
                
                # Check categories are valid
                valid_categories = [
                    'Bundle', 'Non-Bundle Required', 'Non-Bundle Optional',
                    'Third-Party Required', 'Third-Party Optional',
                    'One-Time Credit', 'One-Time Fee'
                ]
                if item['category'] not in valid_categories:
                    results['issues'].append(
                        f"Warning: Unusual category '{item['category']}' for {item['solution_name']}"
                    )
            
            # Check for reasonable values
            monthly_fees = [item['monthly_fee'] for item in normalized if item.get('monthly_fee', 0) > 0]
            if monthly_fees:
                avg_monthly = sum(monthly_fees) / len(monthly_fees)
                print(f"[OK] Average monthly fee: ${avg_monthly:,.2f}")
            
            # Count by category
            categories = {}
            for item in normalized:
                cat = item['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\n[OK] Line items by category:")
            for cat, count in sorted(categories.items()):
                print(f"   - {cat}: {count}")
            
            results['mapped_data'] = {
                'total_items': len(normalized),
                'categories': categories
            }
            
        except Exception as e:
            results['pass'] = False
            results['issues'].append(f"Mapping failed: {str(e)}")
        
        self.validation_results['mapping'][vendor] = results
        
        if results['pass']:
            print(f"\n[PASS] {vendor} mapping validation PASSED")
        else:
            print(f"\n[FAIL] {vendor} mapping validation FAILED")
            for issue in results['issues']:
                print(f"   - {issue}")
        
        return results['pass']
    
    def validate_tco_population(self, tco_file: str, vendor: str, expected_items: int):
        """Validate TCO template population"""
        print("\n" + "="*70)
        print(f"QA CHECK: TCO TEMPLATE POPULATION ({vendor.upper()})")
        print("="*70)
        
        results = {'pass': True, 'issues': []}
        
        try:
            wb = load_workbook(tco_file, data_only=True)
            sheet = wb['Line Items']
            
            # Get column mapping
            if vendor == 'FIS':
                col_map = TCO_COLUMNS['FIS']
            else:
                col_map = TCO_COLUMNS['JACK_HENRY']
            
            # Count populated rows
            populated_rows = 0
            start_row = 7
            max_row = 200
            
            for row in range(start_row, max_row):
                solution_col = col_map['solution_name']
                cell_value = sheet[f"{solution_col}{row}"].value
                
                if cell_value and str(cell_value).strip():
                    populated_rows += 1
            
            print(f"[OK] Found {populated_rows} populated rows")
            
            # Check if matches expected
            if abs(populated_rows - expected_items) > 5:  # Allow 5 row variance
                results['issues'].append(
                    f"Expected ~{expected_items} rows, found {populated_rows}"
                )
            
            # Sample check: verify a few rows have all required data
            sample_rows = range(start_row, min(start_row + 5, start_row + populated_rows))
            
            for row in sample_rows:
                solution_name = sheet[f"{col_map['solution_name']}{row}"].value
                if solution_name:
                    fee_type = sheet[f"{col_map['fee_type']}{row}"].value
                    category = sheet[f"{col_map['category']}{row}"].value
                    
                    if not fee_type:
                        results['issues'].append(f"Row {row}: Missing fee type")
                    if not category:
                        results['issues'].append(f"Row {row}: Missing category")
                    
                    # Check at least one cost column has data
                    year_1_cost = sheet[f"{col_map['year_1_cost']}{row}"].value
                    if year_1_cost is None:
                        results['issues'].append(f"Row {row}: No Year 1 cost")
            
            print(f"[OK] Sample rows validated")
            
            results['population_data'] = {
                'populated_rows': populated_rows,
                'expected_rows': expected_items
            }
            
        except Exception as e:
            results['pass'] = False
            results['issues'].append(f"Population validation failed: {str(e)}")
        
        self.validation_results['population'][vendor] = results
        
        if results['pass']:
            print(f"\n[PASS] {vendor} TCO population validation PASSED")
        else:
            print(f"\n[FAIL] {vendor} TCO population validation FAILED")
            for issue in results['issues']:
                print(f"   - {issue}")
        
        return results['pass']

    def validate_extraction_coverage(self, proposal_path: str, vendor: str):
        """Validate comprehensive coverage of source data extraction"""
        print("\n" + "="*70)
        print(f"QA CHECK: {vendor.upper()} EXTRACTION COVERAGE")
        print("="*70)

        results = {'pass': True, 'issues': []}

        try:
            if vendor == 'Jack Henry':
                extractor = JackHenryExtractor(proposal_path)
                data = extractor.extract()
                coverage_report = extractor.get_validation_report()

                print(f"Coverage: {coverage_report['coverage_percentage']:.2f}%")
                print(f"Cells checked: {coverage_report['total_cells_checked']}")
                print(f"Cells with data: {coverage_report['cells_with_data']}")
                print(f"Cells extracted: {coverage_report['cells_extracted']}")
                print(f"Formulas found: {coverage_report['cells_with_formulas']}")
                print(f"Comments found: {coverage_report['cells_with_comments']}")
                print(f"Hidden rows: {coverage_report['hidden_rows_count']}")
                print(f"Hidden columns: {coverage_report['hidden_columns_count']}")

                # Check for issues
                if coverage_report['coverage_percentage'] < 95:
                    results['issues'].append(
                        f"Coverage {coverage_report['coverage_percentage']:.2f}% is below 95% threshold"
                    )
                    results['pass'] = False

                if coverage_report['hidden_rows_count'] > 0:
                    results['issues'].append(
                        f"Found {coverage_report['hidden_rows_count']} hidden rows with data"
                    )

                if coverage_report['hidden_columns_count'] > 0:
                    results['issues'].append(
                        f"Found {coverage_report['hidden_columns_count']} hidden columns with data"
                    )

                # Store comments and formulas for review
                if data.get('comments'):
                    print(f"\nSample comments (first 3):")
                    for idx, (cell_ref, comment_data) in enumerate(list(data['comments'].items())[:3]):
                        print(f"  {cell_ref}: {comment_data['comment'][:80]}...")

                results['coverage_data'] = coverage_report

        except Exception as e:
            results['pass'] = False
            results['issues'].append(f"Coverage validation failed: {str(e)}")

        self.validation_results['coverage'][vendor] = results

        if results['pass']:
            print(f"\nCoverage validation PASSED")
        else:
            print(f"\nCoverage validation FAILED")
            for issue in results['issues']:
                print(f"   - {issue}")

        return results['pass']

    def validate_cell_by_cell(self, source_file: str, tco_file: str, vendor: str, scenario: str = 'Proposal_1'):
        """Perform cell-by-cell validation"""
        print("\n" + "="*70)
        print(f"QA CHECK: {vendor.upper()} CELL-BY-CELL VALIDATION")
        print("="*70)

        results = {'pass': True, 'issues': []}

        try:
            validator = CellByCellValidator()

            if vendor == 'Jack Henry':
                validation_result = validator.validate_jack_henry_to_tco(
                    source_file, tco_file, scenario
                )

                results['pass'] = validation_result['success']
                results['accuracy'] = validation_result['accuracy_percentage']
                results['statistics'] = validation_result['statistics']

                if not validation_result['success']:
                    results['issues'].append(
                        f"Found {len(validation_result['discrepancies'])} discrepancies"
                    )

                    # Add sample discrepancies to issues
                    for disc in validation_result['discrepancies'][:5]:
                        results['issues'].append(
                            f"Row {disc['source_row']}: {disc['type']} - "
                            f"Expected: {disc['source_value']}, Found: {disc['tco_value']}"
                        )

        except Exception as e:
            results['pass'] = False
            results['issues'].append(f"Cell validation failed: {str(e)}")

        self.validation_results['cell_validation'][vendor] = results

        if results['pass']:
            print(f"\nCell-by-cell validation PASSED - 100% accuracy")
        else:
            print(f"\nCell-by-cell validation FAILED")
            for issue in results['issues']:
                print(f"   - {issue}")

        return results['pass']

    def generate_report(self, output_path: str = "qa_report.txt"):
        """Generate comprehensive QA report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("TCO AUTOMATION - QA VALIDATION REPORT\n")
            f.write("="*70 + "\n\n")
            
            # Overall status
            all_passed = all([
                all(v.get('pass', True) for v in self.validation_results['extraction'].values()),
                all(v.get('pass', True) for v in self.validation_results['mapping'].values()),
                all(v.get('pass', True) for v in self.validation_results['population'].values()),
                all(v.get('pass', True) for v in self.validation_results['coverage'].values()),
                all(v.get('pass', True) for v in self.validation_results['cell_validation'].values())
            ])
            
            if all_passed:
                f.write("[PASS] OVERALL STATUS: PASSED\n\n")
            else:
                f.write("[FAIL] OVERALL STATUS: FAILED\n\n")
            
            # Extraction results
            f.write("EXTRACTION VALIDATION\n")
            f.write("-" * 70 + "\n")
            for vendor, results in self.validation_results['extraction'].items():
                f.write(f"\n{vendor}:\n")
                f.write(f"  Status: {'PASS' if results['pass'] else 'FAIL'}\n")
                if 'extracted_data' in results:
                    for key, value in results['extracted_data'].items():
                        f.write(f"  {key}: {value}\n")
                if results['issues']:
                    f.write("  Issues:\n")
                    for issue in results['issues']:
                        f.write(f"    - {issue}\n")
            
            # Mapping results
            f.write("\n\nMAPPING VALIDATION\n")
            f.write("-" * 70 + "\n")
            for vendor, results in self.validation_results['mapping'].items():
                f.write(f"\n{vendor}:\n")
                f.write(f"  Status: {'PASS' if results['pass'] else 'FAIL'}\n")
                if 'mapped_data' in results:
                    for key, value in results['mapped_data'].items():
                        if key == 'categories':
                            f.write(f"  {key}:\n")
                            for cat, count in value.items():
                                f.write(f"    - {cat}: {count}\n")
                        else:
                            f.write(f"  {key}: {value}\n")
                if results['issues']:
                    f.write("  Issues:\n")
                    for issue in results['issues']:
                        f.write(f"    - {issue}\n")
            
            # Population results
            f.write("\n\nTCO POPULATION VALIDATION\n")
            f.write("-" * 70 + "\n")
            for vendor, results in self.validation_results['population'].items():
                f.write(f"\n{vendor}:\n")
                f.write(f"  Status: {'PASS' if results['pass'] else 'FAIL'}\n")
                if 'population_data' in results:
                    for key, value in results['population_data'].items():
                        f.write(f"  {key}: {value}\n")
                if results['issues']:
                    f.write("  Issues:\n")
                    for issue in results['issues']:
                        f.write(f"    - {issue}\n")

            # Coverage results
            f.write("\n\nEXTRACTION COVERAGE VALIDATION\n")
            f.write("-" * 70 + "\n")
            for vendor, results in self.validation_results['coverage'].items():
                f.write(f"\n{vendor}:\n")
                f.write(f"  Status: {'PASS' if results['pass'] else 'FAIL'}\n")
                if 'coverage_data' in results:
                    for key, value in results['coverage_data'].items():
                        f.write(f"  {key}: {value}\n")
                if results['issues']:
                    f.write("  Issues:\n")
                    for issue in results['issues']:
                        f.write(f"    - {issue}\n")

            # Cell-by-cell validation results
            f.write("\n\nCELL-BY-CELL VALIDATION\n")
            f.write("-" * 70 + "\n")
            for vendor, results in self.validation_results['cell_validation'].items():
                f.write(f"\n{vendor}:\n")
                f.write(f"  Status: {'PASS' if results['pass'] else 'FAIL'}\n")
                if 'accuracy' in results:
                    f.write(f"  Accuracy: {results['accuracy']:.2f}%\n")
                if 'statistics' in results:
                    f.write(f"  Statistics:\n")
                    for key, value in results['statistics'].items():
                        f.write(f"    {key}: {value}\n")
                if results['issues']:
                    f.write("  Issues:\n")
                    for issue in results['issues']:
                        f.write(f"    - {issue}\n")

            f.write("\n" + "="*70 + "\n")
        
        print(f"\nQA Report saved to: {output_path}")
        return output_path


def run_full_qa(fis_proposal: str = None, jh_proposal: str = None, 
                tco_output: str = None, report_path: str = "qa_report.txt"):
    """
    Run complete QA validation
    
    Args:
        fis_proposal: Path to FIS proposal
        jh_proposal: Path to Jack Henry proposal
        tco_output: Path to populated TCO file
        report_path: Path for QA report
    """
    validator = TCOValidator()
    
    print("\nStarting TCO Automation QA Validation...\n")
    
    # Validate FIS if provided
    if fis_proposal:
        fis_passed = validator.validate_fis_extraction(
            fis_proposal,
            expected_counts={'bundle_years': 7, 'monthly_fees': 25, 'one_time_credits': 5}
        )
        
        if fis_passed:
            fis_data = extract_fis_proposal(fis_proposal)
            validator.validate_mapping(fis_data, 'FIS')
            
            if tco_output:
                validator.validate_tco_population(tco_output, 'FIS', expected_items=42)
    
    # Validate Jack Henry if provided
    if jh_proposal:
        jh_passed = validator.validate_jh_extraction(
            jh_proposal,
            expected_counts={'products': 150, 'scenarios': 3}
        )
        
        if jh_passed:
            jh_data = extract_jack_henry_proposal(jh_proposal)
            validator.validate_mapping(jh_data, 'Jack Henry')
            
            if tco_output:
                validator.validate_tco_population(tco_output, 'Jack Henry', expected_items=134)
    
    # Generate report
    validator.generate_report(report_path)
    
    print("\n[DONE] QA Validation Complete!")
    print(f"See full report: {report_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='QA Validator for TCO Automation')
    parser.add_argument('--fis', type=str, help='Path to FIS proposal')
    parser.add_argument('--jh', type=str, help='Path to Jack Henry proposal')
    parser.add_argument('--tco', type=str, help='Path to populated TCO file')
    parser.add_argument('--report', type=str, default='qa_report.txt', help='Output report path')
    
    args = parser.parse_args()
    
    if not args.fis and not args.jh:
        print("Error: Provide at least --fis or --jh")
        sys.exit(1)
    
    run_full_qa(args.fis, args.jh, args.tco, args.report)
