"""
Jack Henry Excel Extractor
Extracts pricing data from Jack Henry deal sheet Excel files
"""

from openpyxl import load_workbook
import pandas as pd
from typing import Dict, List, Any


class JackHenryExtractor:
    """Extract structured data from Jack Henry Excel proposals"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.wb = load_workbook(filepath, data_only=True)
        self.extracted_data = {
            'vendor': 'Jack Henry',
            'summary': {},
            'products': [],
            'term_options': None,
            'scenarios': []
        }
    
    def extract(self) -> Dict[str, Any]:
        """Main extraction method"""
        print(f"Extracting data from Jack Henry proposal: {self.filepath}")
        print(f"Available sheets: {self.wb.sheetnames}")
        
        # Extract from Summary sheet
        self._extract_summary()
        
        # Extract from Proposal sheets
        for sheet_name in ['Proposal_1', 'Proposal_2', 'Proposal_3']:
            if sheet_name in self.wb.sheetnames:
                self._extract_proposal(sheet_name)
        
        return self.extracted_data
    
    def _extract_summary(self):
        """Extract high-level summary data"""
        if 'Summary' not in self.wb.sheetnames:
            print("Warning: Summary sheet not found")
            return
        
        print("\nExtracting Summary sheet...")
        sheet = self.wb['Summary']
        
        # Extract key summary metrics
        summary = {}
        
        # Look for bank name, assets, etc. in first ~20 rows
        for row_idx in range(1, 20):
            row = sheet[row_idx]
            for cell in row[:5]:
                if cell.value and isinstance(cell.value, str):
                    if ': Bank Name' in cell.value or 'Bank Name' in cell.value:
                        summary['bank_name'] = row[0].value if row[0].value else 'Unknown'
                    elif ': Assets' in cell.value or 'Asset Size' in cell.value:
                        summary['assets'] = row[1].value if len(row) > 1 else 0
                    elif ': JHA Core Product' in cell.value:
                        summary['core_product'] = row[1].value if len(row) > 1 else 'Unknown'
        
        # Extract monthly fees summary (around rows 28-32)
        for row_idx in range(25, 35):
            row = sheet[row_idx]
            cell_value = str(row[0].value) if row[0].value else ''
            
            if 'Monthly Fees' in cell_value:
                summary['total_monthly_list'] = row[1].value if len(row) > 1 else 0
            elif 'Net Monthly Fees' in cell_value:
                summary['total_monthly_net'] = row[1].value if len(row) > 1 else 0
            elif 'Annualized List Price' in cell_value:
                summary['annualized_list'] = row[1].value if len(row) > 1 else 0
            elif 'Annualized Net Price' in cell_value:
                summary['annualized_net'] = row[1].value if len(row) > 1 else 0
        
        self.extracted_data['summary'] = summary
        print(f"Summary extracted: {summary}")
    
    def _extract_proposal(self, sheet_name: str):
        """Extract detailed product pricing from proposal sheet"""
        print(f"\nExtracting {sheet_name}...")
        sheet = self.wb[sheet_name]
        
        # Find the header row (usually around row 11-13)
        header_row_idx = None
        for row_idx in range(1, 20):
            row = sheet[row_idx]
            if any('Product Description' in str(cell.value) for cell in row[:10] if cell.value):
                header_row_idx = row_idx
                break
        
        if not header_row_idx:
            print(f"Warning: Could not find header row in {sheet_name}")
            return
        
        print(f"Found header row at index {header_row_idx}")
        
        # Get column indices
        header_row = sheet[header_row_idx]
        col_indices = self._get_column_indices(header_row)
        
        # Extract products starting from row after header
        products = []
        for row_idx in range(header_row_idx + 1, sheet.max_row + 1):
            row = sheet[row_idx]
            
            # Get product description from column B (index 1)
            product_desc = row[1].value if len(row) > 1 else None
            
            # Skip empty rows or section headers
            if not product_desc or product_desc == 'Product Description':
                continue
            
            # Skip if it looks like a header or summary row
            if isinstance(product_desc, str) and any(x in product_desc.lower() for x in ['total', 'summary', 'subtotal']):
                continue
            
            # Extract product data
            product_data = self._extract_product_row(row, col_indices)
            if product_data:
                products.append(product_data)
        
        print(f"Extracted {len(products)} products from {sheet_name}")
        
        # Store in extracted_data
        self.extracted_data['scenarios'].append({
            'scenario_name': sheet_name,
            'products': products,
            'product_count': len(products)
        })
    
    def _get_column_indices(self, header_row) -> Dict[str, int]:
        """Map column names to indices"""
        col_map = {}
        
        for idx, cell in enumerate(header_row):
            if cell.value:
                value = str(cell.value).strip()
                
                if 'Product Description' in value:
                    col_map['product_description'] = idx
                elif 'Order Type' in value:
                    col_map['order_type'] = idx
                elif 'Delivery' in value:
                    col_map['delivery'] = idx
                elif 'Optional' in value:
                    col_map['optional'] = idx
                elif 'Category' in value:
                    col_map['category'] = idx
                elif 'Product Family' in value:
                    col_map['product_family'] = idx
                elif 'Quantity' in value:
                    col_map['quantity'] = idx
                elif 'License List' in value:
                    col_map['license_list'] = idx
                elif 'License Net' in value:
                    col_map['license_net'] = idx
                elif 'Install List' in value:
                    col_map['install_list'] = idx
                elif 'Install Net' in value:
                    col_map['install_net'] = idx
                elif 'Maintenance List' in value:
                    col_map['maintenance_list'] = idx
                elif 'Maintenance Net' in value:
                    col_map['maintenance_net'] = idx
                elif 'New Monthly List' in value:
                    col_map['monthly_list'] = idx
                elif 'New Monthly Net' in value:
                    col_map['monthly_net'] = idx
        
        return col_map
    
    def _extract_product_row(self, row, col_indices: Dict[str, int]) -> Dict[str, Any]:
        """Extract data from a single product row"""
        try:
            product_desc = row[col_indices.get('product_description', 1)].value
            if not product_desc:
                return None
            
            product = {
                'product_description': str(product_desc),
                'order_type': self._get_cell_value(row, col_indices, 'order_type', ''),
                'delivery': self._get_cell_value(row, col_indices, 'delivery', ''),
                'optional': self._get_cell_value(row, col_indices, 'optional', 0),
                'category': self._get_cell_value(row, col_indices, 'category', ''),
                'product_family': self._get_cell_value(row, col_indices, 'product_family', ''),
                'quantity': self._get_cell_value(row, col_indices, 'quantity', 0, numeric=True),
                'license_list': self._get_cell_value(row, col_indices, 'license_list', 0, numeric=True),
                'license_net': self._get_cell_value(row, col_indices, 'license_net', 0, numeric=True),
                'install_list': self._get_cell_value(row, col_indices, 'install_list', 0, numeric=True),
                'install_net': self._get_cell_value(row, col_indices, 'install_net', 0, numeric=True),
                'maintenance_list': self._get_cell_value(row, col_indices, 'maintenance_list', 0, numeric=True),
                'maintenance_net': self._get_cell_value(row, col_indices, 'maintenance_net', 0, numeric=True),
                'monthly_list': self._get_cell_value(row, col_indices, 'monthly_list', 0, numeric=True),
                'monthly_net': self._get_cell_value(row, col_indices, 'monthly_net', 0, numeric=True)
            }
            
            return product
        
        except Exception as e:
            print(f"Error extracting product row: {e}")
            return None
    
    def _get_cell_value(self, row, col_indices: Dict[str, int], key: str, default, numeric: bool = False):
        """Safely get cell value with default"""
        try:
            idx = col_indices.get(key)
            if idx is None or idx >= len(row):
                return default
            
            value = row[idx].value
            
            if value is None:
                return default
            
            if numeric:
                return float(value) if value else 0.0
            
            return value
        except:
            return default
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of extracted data"""
        total_products = sum(scenario['product_count'] for scenario in self.extracted_data['scenarios'])
        
        return {
            'vendor': self.extracted_data['vendor'],
            'bank_name': self.extracted_data['summary'].get('bank_name', 'Unknown'),
            'core_product': self.extracted_data['summary'].get('core_product', 'Unknown'),
            'scenarios_count': len(self.extracted_data['scenarios']),
            'total_products': total_products,
            'monthly_net': self.extracted_data['summary'].get('total_monthly_net', 0)
        }


def extract_jack_henry_proposal(filepath: str) -> Dict[str, Any]:
    """Convenience function to extract Jack Henry proposal data"""
    extractor = JackHenryExtractor(filepath)
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
        filepath = "../data/Updated_With_all_products__Deal_Sheet_Clearwater__FL_-_Echelon_Bank__InOrg__-_New_Core_SilverLake_OL_PAP_08_27_25.xlsx"
    
    data = extract_jack_henry_proposal(filepath)
    
    # Print sample products
    if data['scenarios']:
        print(f"\nSample products from {data['scenarios'][0]['scenario_name']}:")
        for product in data['scenarios'][0]['products'][:5]:
            print(f"  - {product['product_description']}: ${product['monthly_net']}/month")
