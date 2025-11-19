"""
FIS Word Document Extractor
Extracts pricing data from FIS proposal Word documents
"""

from docx import Document
from typing import Dict, List, Any
import re


class FISExtractor:
    """Extract structured data from FIS Word proposals"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.doc = Document(filepath)
        self.extracted_data = {
            'vendor': 'FIS',
            'bundle_pricing': {},
            'one_time_credits': {},
            'monthly_fees': [],
            'optional_fees': [],
            'terms_and_conditions': {}
        }
    
    def extract(self) -> Dict[str, Any]:
        """Main extraction method"""
        print(f"Extracting data from FIS proposal: {self.filepath}")
        
        # Extract all tables
        tables = self.doc.tables
        print(f"Found {len(tables)} tables in document")
        
        for idx, table in enumerate(tables):
            print(f"\nProcessing table {idx + 1}...")
            self._process_table(table, idx)
        
        return self.extracted_data
    
    def _process_table(self, table, table_idx: int):
        """Process individual table based on its content"""
        # Get first row to identify table type
        first_row_text = ' '.join([cell.text.strip() for cell in table.rows[0].cells])
        
        # Identify table type
        if 'Signing Bonus' in first_row_text or 'One-Time Credit' in first_row_text:
            self._extract_one_time_credits(table, table_idx)
        elif 'Monthly Bundle Investment' in first_row_text:
            self._extract_bundle_pricing(table, table_idx)
        elif 'Solution' in first_row_text and 'Monthly Fee' in first_row_text:
            self._extract_monthly_fees(table, table_idx, optional=False)
        elif 'Annual Increase' in first_row_text or 'Liquidated Damages' in first_row_text:
            self._extract_terms_conditions(table, table_idx)
        else:
            print(f"  Table {table_idx + 1}: Unknown table type, skipping")
    
    def _extract_one_time_credits(self, table, table_idx: int):
        """Extract one-time credits/fees"""
        print(f"  Table {table_idx + 1}: One-time credits")
        
        for row_idx, row in enumerate(table.rows[1:], start=1):  # Skip header
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) >= 4 and cells[0]:
                description = cells[0]
                # Extract values for different terms (5/7/10 year)
                values = []
                for cell in cells[2:5]:  # Columns for 5-year, 7-year, 10-year
                    value = self._parse_currency(cell)
                    values.append(value)
                
                if any(values):  # Only add if there are non-zero values
                    self.extracted_data['one_time_credits'][description] = {
                        '5_year': values[0] if len(values) > 0 else 0,
                        '7_year': values[1] if len(values) > 1 else 0,
                        '10_year': values[2] if len(values) > 2 else 0
                    }
    
    def _extract_bundle_pricing(self, table, table_idx: int):
        """Extract monthly bundle pricing by year"""
        print(f"  Table {table_idx + 1}: Bundle pricing")
        
        for row_idx, row in enumerate(table.rows[1:], start=1):  # Skip header
            cells = [cell.text.strip() for cell in row.cells]
            if len(cells) >= 2 and cells[0] and 'Year' in cells[0]:
                year = cells[0].strip()
                
                # Extract values for different terms
                term_5_year = self._parse_currency(cells[1]) if len(cells) > 1 else None
                term_7_year = self._parse_currency(cells[2]) if len(cells) > 2 else None
                term_10_year = self._parse_currency(cells[3]) if len(cells) > 3 else None
                
                self.extracted_data['bundle_pricing'][year] = {
                    '5_year': term_5_year,
                    '7_year': term_7_year,
                    '10_year': term_10_year
                }
    
    def _extract_monthly_fees(self, table, table_idx: int, optional: bool = False):
        """Extract monthly fees for additional solutions"""
        category = "optional" if optional else "required"
        print(f"  Table {table_idx + 1}: Monthly fees ({category})")
        
        for row_idx, row in enumerate(table.rows[1:], start=1):  # Skip header
            cells = [cell.text.strip() for cell in row.cells]
            
            if len(cells) >= 3 and cells[0] and cells[0] != 'Solution':
                solution_name = cells[0]
                monthly_fee = self._parse_currency(cells[1]) if len(cells) > 1 else 0
                one_time_fee = self._parse_currency(cells[2]) if len(cells) > 2 else 0
                
                # Determine if FIS or Third-Party
                is_third_party = 'Third-Party' in solution_name or row_idx > 10
                
                fee_data = {
                    'solution_name': solution_name,
                    'monthly_fee': monthly_fee,
                    'one_time_fee': one_time_fee,
                    'optional': optional,
                    'third_party': is_third_party,
                    'calculation': cells[3] if len(cells) > 3 else ''
                }
                
                if optional:
                    self.extracted_data['optional_fees'].append(fee_data)
                else:
                    self.extracted_data['monthly_fees'].append(fee_data)
    
    def _extract_terms_conditions(self, table, table_idx: int):
        """Extract terms and conditions"""
        print(f"  Table {table_idx + 1}: Terms and conditions")
        
        for row_idx, row in enumerate(table.rows[1:], start=1):  # Skip header
            cells = [cell.text.strip() for cell in row.cells]
            
            if len(cells) >= 2 and cells[0]:
                term_name = cells[0]
                
                # Extract term details
                if 'Annual Increase' in term_name:
                    # Extract percentage values for different terms
                    values = []
                    for cell in cells[2:5]:
                        if '%' in cell:
                            try:
                                pct = float(cell.replace('%', '').strip()) / 100
                                values.append(pct)
                            except:
                                values.append(None)
                    
                    self.extracted_data['terms_and_conditions']['annual_increase'] = {
                        '5_year': values[0] if len(values) > 0 else None,
                        '7_year': values[1] if len(values) > 1 else None,
                        '10_year': values[2] if len(values) > 2 else None
                    }
                else:
                    self.extracted_data['terms_and_conditions'][term_name] = cells[1] if len(cells) > 1 else ''
    
    def _parse_currency(self, text: str) -> float:
        """Parse currency string to float"""
        if not text or text == 'N/A':
            return 0.0
        
        # Remove currency symbols, commas, parentheses
        cleaned = text.replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of extracted data"""
        return {
            'vendor': self.extracted_data['vendor'],
            'bundle_years_found': list(self.extracted_data['bundle_pricing'].keys()),
            'one_time_credits_count': len(self.extracted_data['one_time_credits']),
            'monthly_fees_count': len(self.extracted_data['monthly_fees']),
            'optional_fees_count': len(self.extracted_data['optional_fees']),
            'terms_conditions_count': len(self.extracted_data['terms_and_conditions'])
        }


def extract_fis_proposal(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract FIS proposal data"""
    extractor = FISExtractor(filepath)
    data = extractor.extract()
    summary = extractor.get_summary()
    
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("="*70)
    
    return data


if __name__ == "__main__":
    # Test extraction
    import sys
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "../data/Echelon_FIS_Proposal_10_29_25.docx"
    
    data = extract_fis_proposal(filepath)
    
    # Print some extracted data
    print("\nBundle Pricing:")
    for year, prices in data['bundle_pricing'].items():
        print(f"  {year}: {prices}")
