"""
Schema Mapper - Normalizes vendor-specific data to TCO template schema
"""

from typing import Dict, List, Any
import sys
sys.path.append('..')
from config import (
    FEE_TYPES, PRODUCT_CATEGORIES, FIS_BUNDLE_KEYWORDS,
    JH_PRODUCT_FAMILIES, DEFAULT_GROWTH_RATE
)


class SchemaMapper:
    """Maps and normalizes vendor data to TCO schema"""
    
    def __init__(self, growth_rate: float = DEFAULT_GROWTH_RATE):
        self.growth_rate = growth_rate
    
    def map_fis_data(self, fis_data: Dict[str, Any], term: str = '7_year') -> List[Dict[str, Any]]:
        """
        Map FIS extracted data to normalized TCO schema
        
        Args:
            fis_data: Extracted FIS data
            term: Which term to use ('5_year', '7_year', '10_year')
        
        Returns:
            List of normalized line items
        """
        print(f"\nMapping FIS data for {term} term...")
        line_items = []
        
        # 1. Map Bundle Pricing
        bundle_items = self._map_fis_bundle(fis_data, term)
        line_items.extend(bundle_items)
        
        # 2. Map Monthly Fees (Non-Bundle Required)
        monthly_items = self._map_fis_monthly_fees(fis_data, required=True)
        line_items.extend(monthly_items)
        
        # 3. Map Optional Fees
        optional_items = self._map_fis_monthly_fees(fis_data, required=False)
        line_items.extend(optional_items)
        
        # 4. Map One-Time Credits/Fees
        onetime_items = self._map_fis_one_time(fis_data, term)
        line_items.extend(onetime_items)
        
        print(f"Mapped {len(line_items)} line items from FIS data")
        return line_items
    
    def _map_fis_bundle(self, fis_data: Dict[str, Any], term: str) -> List[Dict[str, Any]]:
        """Map FIS bundle pricing"""
        line_items = []
        bundle_pricing = fis_data.get('bundle_pricing', {})
        
        # Determine number of years based on term
        num_years = {
            '5_year': 5,
            '7_year': 7,
            '10_year': 10
        }.get(term, 7)
        
        for year_key, prices in bundle_pricing.items():
            if term not in prices or prices[term] == 0:
                continue
            
            monthly_price = prices[term]
            
            # Create line item for this year's bundle pricing
            item = {
                'solution_name': f"{year_key} CORE PROCESSING (Bundle)",
                'fee_type': FEE_TYPES['monthly_fixed'],
                'category': PRODUCT_CATEGORIES['BUNDLE'],
                'vendor': 'FIS',
                'per_unit_rate': monthly_price,
                'avg_monthly_qty': 1,
                'monthly_fee': monthly_price,
                'annual_fee': monthly_price * 12,
                'one_time_fee': 0,
                'optional': False,
                'third_party': False,
                'quantities_by_year': self._create_year_quantities(year_key, num_years)
            }
            
            line_items.append(item)
        
        return line_items
    
    def _map_fis_monthly_fees(self, fis_data: Dict[str, Any], required: bool = True) -> List[Dict[str, Any]]:
        """Map FIS monthly fees (non-bundle)"""
        line_items = []
        
        fees = fis_data.get('monthly_fees' if required else 'optional_fees', [])
        
        for fee_data in fees:
            solution_name = fee_data['solution_name']
            monthly_fee = fee_data['monthly_fee']
            one_time_fee = fee_data['one_time_fee']
            third_party = fee_data.get('third_party', False)
            
            # Determine category
            if required:
                category = PRODUCT_CATEGORIES['THIRD_PARTY_REQUIRED'] if third_party else PRODUCT_CATEGORIES['NON_BUNDLE_REQUIRED']
            else:
                category = PRODUCT_CATEGORIES['THIRD_PARTY_OPTIONAL'] if third_party else PRODUCT_CATEGORIES['NON_BUNDLE_OPTIONAL']
            
            # Determine fee type (fixed vs variable based on calculation field)
            calculation = fee_data.get('calculation', '')
            fee_type = FEE_TYPES['monthly_variable'] if 'x' in calculation.lower() or 'per' in calculation.lower() else FEE_TYPES['monthly_fixed']
            
            item = {
                'solution_name': solution_name,
                'fee_type': fee_type,
                'category': category,
                'vendor': 'FIS',
                'per_unit_rate': monthly_fee,
                'avg_monthly_qty': 1,
                'monthly_fee': monthly_fee,
                'annual_fee': monthly_fee * 12,
                'one_time_fee': one_time_fee,
                'optional': not required,
                'third_party': third_party,
                'quantities_by_year': self._create_standard_quantities(7)  # Default 7 years
            }
            
            line_items.append(item)
        
        return line_items
    
    def _map_fis_one_time(self, fis_data: Dict[str, Any], term: str) -> List[Dict[str, Any]]:
        """Map FIS one-time credits/fees"""
        line_items = []
        one_time_data = fis_data.get('one_time_credits', {})
        
        for description, values in one_time_data.items():
            amount = values.get(term, 0)
            
            if amount == 0:
                continue
            
            # Determine if it's a credit (negative) or fee (positive)
            is_credit = amount < 0
            
            item = {
                'solution_name': description,
                'fee_type': FEE_TYPES['one_time'],
                'category': 'One-Time Credit' if is_credit else 'One-Time Fee',
                'vendor': 'FIS',
                'per_unit_rate': abs(amount),
                'avg_monthly_qty': 0,
                'monthly_fee': 0,
                'annual_fee': 0,
                'one_time_fee': amount,
                'optional': False,
                'third_party': False,
                'quantities_by_year': {}
            }
            
            line_items.append(item)
        
        return line_items
    
    def _create_year_quantities(self, year_key: str, total_years: int) -> Dict[str, float]:
        """Create quantity distribution for bundle pricing based on year"""
        quantities = {}
        
        # Extract year number from key (e.g., "Year 1" -> 1)
        import re
        match = re.search(r'Year (\d+)', year_key)
        if not match:
            return {f'year_{i}': 0 for i in range(1, total_years + 1)}
        
        year_num = int(match.group(1))
        
        # Set quantity to 12 (months) for the specific year, 0 for others
        for i in range(1, total_years + 1):
            quantities[f'year_{i}'] = 12 if i == year_num else 0
        
        return quantities
    
    def _create_standard_quantities(self, total_years: int, with_growth: bool = True) -> Dict[str, float]:
        """Create standard quantity distribution with optional growth"""
        quantities = {}
        base_qty = 12  # 12 months
        
        for i in range(1, total_years + 1):
            if with_growth:
                # Apply compound growth
                quantities[f'year_{i}'] = base_qty * ((1 + self.growth_rate) ** (i - 1))
            else:
                quantities[f'year_{i}'] = base_qty
        
        return quantities
    
    def map_jh_data(self, jh_data: Dict[str, Any], scenario: str = 'Proposal_1') -> List[Dict[str, Any]]:
        """
        Map Jack Henry extracted data to normalized TCO schema
        
        Args:
            jh_data: Extracted Jack Henry data
            scenario: Which proposal scenario to use
        
        Returns:
            List of normalized line items
        """
        print(f"\nMapping Jack Henry data for {scenario}...")
        line_items = []
        
        # Find the specified scenario
        scenario_data = None
        for s in jh_data.get('scenarios', []):
            if s['scenario_name'] == scenario:
                scenario_data = s
                break
        
        if not scenario_data:
            print(f"Warning: Scenario {scenario} not found")
            return line_items
        
        products = scenario_data.get('products', [])
        
        for product in products:
            # Map each product to line items
            mapped_items = self._map_jh_product(product)
            line_items.extend(mapped_items)
        
        print(f"Mapped {len(line_items)} line items from Jack Henry data")
        return line_items
    
    def _map_jh_product(self, product: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map a single Jack Henry product to line item(s)"""
        line_items = []
        
        product_desc = product['product_description']
        product_family = product.get('product_family', '')
        category_flag = product.get('category', '')
        optional = product.get('optional', 0) == 1
        
        # Determine category based on product family and optional flag
        if product_family in ['SilverLake', 'Xperience']:
            category = PRODUCT_CATEGORIES['BUNDLE']
        elif optional:
            category = PRODUCT_CATEGORIES['NON_BUNDLE_OPTIONAL']
        else:
            category = PRODUCT_CATEGORIES['NON_BUNDLE_REQUIRED']
        
        # License fee (one-time)
        if product['license_net'] > 0:
            item = {
                'solution_name': f"{product_desc} - License",
                'fee_type': FEE_TYPES['one_time'],
                'category': category,
                'vendor': 'Jack Henry',
                'per_unit_rate': product['license_net'],
                'avg_monthly_qty': 0,
                'monthly_fee': 0,
                'annual_fee': 0,
                'one_time_fee': product['license_net'],
                'optional': optional,
                'third_party': False,
                'quantities_by_year': {}
            }
            line_items.append(item)
        
        # Installation fee (one-time)
        if product['install_net'] > 0:
            item = {
                'solution_name': f"{product_desc} - Installation",
                'fee_type': FEE_TYPES['one_time'],
                'category': category,
                'vendor': 'Jack Henry',
                'per_unit_rate': product['install_net'],
                'avg_monthly_qty': 0,
                'monthly_fee': 0,
                'annual_fee': 0,
                'one_time_fee': product['install_net'],
                'optional': optional,
                'third_party': False,
                'quantities_by_year': {}
            }
            line_items.append(item)
        
        # Monthly maintenance fee
        if product['maintenance_net'] > 0:
            item = {
                'solution_name': f"{product_desc} - Maintenance",
                'fee_type': FEE_TYPES['monthly_fixed'],
                'category': category,
                'vendor': 'Jack Henry',
                'per_unit_rate': product['maintenance_net'],
                'avg_monthly_qty': 1,
                'monthly_fee': product['maintenance_net'],
                'annual_fee': product['maintenance_net'] * 12,
                'one_time_fee': 0,
                'optional': optional,
                'third_party': False,
                'quantities_by_year': self._create_standard_quantities(7, with_growth=False)
            }
            line_items.append(item)
        
        # Monthly service fee
        if product['monthly_net'] > 0:
            item = {
                'solution_name': product_desc,
                'fee_type': FEE_TYPES['monthly_fixed'],
                'category': category,
                'vendor': 'Jack Henry',
                'per_unit_rate': product['monthly_net'],
                'avg_monthly_qty': 1,
                'monthly_fee': product['monthly_net'],
                'annual_fee': product['monthly_net'] * 12,
                'one_time_fee': 0,
                'optional': optional,
                'third_party': False,
                'quantities_by_year': self._create_standard_quantities(7, with_growth=False)
            }
            line_items.append(item)
        
        return line_items


def normalize_vendor_data(vendor_data: Dict[str, Any], vendor: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Convenience function to normalize vendor data
    
    Args:
        vendor_data: Extracted vendor data
        vendor: 'FIS' or 'Jack Henry'
        **kwargs: Additional arguments (term for FIS, scenario for JH)
    
    Returns:
        List of normalized line items
    """
    mapper = SchemaMapper()
    
    if vendor == 'FIS':
        term = kwargs.get('term', '7_year')
        return mapper.map_fis_data(vendor_data, term)
    elif vendor == 'Jack Henry':
        scenario = kwargs.get('scenario', 'Proposal_1')
        return mapper.map_jh_data(vendor_data, scenario)
    else:
        raise ValueError(f"Unknown vendor: {vendor}")


if __name__ == "__main__":
    # Test mapping
    import sys
    import os
    sys.path.append('..')
    from extractors import extract_fis_proposal, extract_jack_henry_proposal
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    print("="*70)
    print("Testing FIS Mapping")
    print("="*70)
    fis_file = os.path.join(data_dir, "Echelon_FIS_Proposal_10_29_25.docx")
    fis_data = extract_fis_proposal(fis_file)
    fis_normalized = normalize_vendor_data(fis_data, 'FIS', term='7_year')
    
    print(f"\nFirst 5 FIS line items:")
    for item in fis_normalized[:5]:
        print(f"  - {item['solution_name']}: ${item.get('monthly_fee', 0)}/mo, ${item.get('one_time_fee', 0)} one-time")
    
    print("\n" + "="*70)
    print("Testing Jack Henry Mapping")
    print("="*70)
    jh_file = os.path.join(data_dir, "Updated_With_all_products__Deal_Sheet_Clearwater__FL_-_Echelon_Bank__InOrg__-_New_Core_SilverLake_OL_PAP_08_27_25.xlsx")
    jh_data = extract_jack_henry_proposal(jh_file)
    jh_normalized = normalize_vendor_data(jh_data, 'Jack Henry', scenario='Proposal_1')
    
    print(f"\nFirst 5 Jack Henry line items:")
    for item in jh_normalized[:5]:
        print(f"  - {item['solution_name']}: ${item.get('monthly_fee', 0)}/mo, ${item.get('one_time_fee', 0)} one-time")
