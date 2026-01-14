"""
Helper Functions

Common utility functions for TCO Automation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def detect_vendor_from_file(filepath: str) -> Optional[str]:
    """
    Auto-detect vendor from filename or content.

    Args:
        filepath: Path to file

    Returns:
        Vendor name or None if unable to detect
    """
    filename = os.path.basename(filepath).lower()
    ext = os.path.splitext(filepath)[1].lower()

    # Check filename patterns
    if 'fis' in filename:
        return 'FIS'
    elif any(x in filename for x in ['jack', 'jh', 'silverlake', 'xperience']):
        return 'Jack Henry'
    elif 'fiserv' in filename:
        return 'Fiserv'

    # Infer from extension
    if ext == '.docx':
        return 'FIS'  # FIS typically uses Word
    elif ext == '.xlsx':
        return 'Jack Henry'  # JH typically uses Excel

    return None


def generate_output_filename(
    vendor: str = None,
    term: str = None,
    prefix: str = 'tco_output',
    extension: str = '.xlsx'
) -> str:
    """
    Generate a standardized output filename.

    Args:
        vendor: Vendor name
        term: Contract term
        prefix: Filename prefix
        extension: File extension

    Returns:
        Generated filename
    """
    parts = [prefix]

    if vendor:
        parts.append(vendor.lower().replace(' ', '_'))

    if term:
        parts.append(term)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    parts.append(timestamp)

    filename = '_'.join(parts) + extension
    return filename


def calculate_contract_total(
    line_items: List[Dict[str, Any]],
    term_years: int = 5,
    include_one_time: bool = True
) -> Dict[str, float]:
    """
    Calculate total contract value from line items.

    Args:
        line_items: List of normalized line items
        term_years: Contract term in years
        include_one_time: Include one-time fees

    Returns:
        Dictionary with total calculations
    """
    totals = {
        'monthly_total': 0.0,
        'annual_total': 0.0,
        'one_time_total': 0.0,
        'contract_total': 0.0,
        'by_category': {},
        'by_fee_type': {}
    }

    for item in line_items:
        monthly = item.get('monthly_fee', 0) or 0
        annual = item.get('annual_fee', 0) or 0
        one_time = item.get('one_time_fee', 0) or 0
        category = item.get('category', 'Other')
        fee_type = item.get('fee_type', 'Other')

        totals['monthly_total'] += monthly
        totals['annual_total'] += annual
        totals['one_time_total'] += one_time

        # By category
        if category not in totals['by_category']:
            totals['by_category'][category] = 0.0
        totals['by_category'][category] += annual

        # By fee type
        if fee_type not in totals['by_fee_type']:
            totals['by_fee_type'][fee_type] = 0.0
        totals['by_fee_type'][fee_type] += monthly

    # Calculate contract total
    totals['contract_total'] = (totals['annual_total'] * term_years)
    if include_one_time:
        totals['contract_total'] += totals['one_time_total']

    return totals


def merge_extracted_data(
    data_list: List[Dict[str, Any]],
    merge_strategy: str = 'combine'
) -> Dict[str, Any]:
    """
    Merge multiple extracted data dictionaries.

    Args:
        data_list: List of extracted data dictionaries
        merge_strategy: 'combine' (merge lists), 'override' (last wins), 'first' (first wins)

    Returns:
        Merged dictionary
    """
    if not data_list:
        return {}

    if len(data_list) == 1:
        return data_list[0].copy()

    merged = {}

    for data in data_list:
        for key, value in data.items():
            if key not in merged:
                merged[key] = value
            elif merge_strategy == 'override':
                merged[key] = value
            elif merge_strategy == 'first':
                pass  # Keep first value
            elif merge_strategy == 'combine':
                # Combine lists, merge dicts
                if isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = {**merged[key], **value}
                else:
                    merged[key] = value

    return merged


def clean_solution_name(name: str) -> str:
    """
    Clean and standardize a solution/product name.

    Args:
        name: Raw solution name

    Returns:
        Cleaned name
    """
    if not name:
        return ""

    # Remove extra whitespace
    cleaned = ' '.join(name.split())

    # Remove common prefixes
    prefixes = ['FIS ', 'Jack Henry ', 'JH ']
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]

    # Remove trademark symbols
    cleaned = re.sub(r'[™®©]', '', cleaned)

    # Title case
    cleaned = cleaned.strip()

    return cleaned


def parse_year_from_string(text: str) -> Optional[int]:
    """
    Extract year number from text.

    Args:
        text: Text containing year (e.g., "Year 1", "Y2", "year_3")

    Returns:
        Year number or None
    """
    match = re.search(r'(?:year|y)[\s_-]*(\d+)', text.lower())
    if match:
        return int(match.group(1))
    return None


def calculate_growth_projection(
    base_value: float,
    growth_rate: float,
    years: int
) -> List[float]:
    """
    Calculate year-over-year growth projection.

    Args:
        base_value: Starting value
        growth_rate: Annual growth rate (e.g., 0.03 for 3%)
        years: Number of years

    Returns:
        List of values for each year
    """
    projections = []
    current = base_value

    for year in range(years):
        projections.append(round(current, 2))
        current = current * (1 + growth_rate)

    return projections


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_file_info(filepath: str) -> Dict[str, Any]:
    """
    Get information about a file.

    Args:
        filepath: Path to file

    Returns:
        Dictionary with file information
    """
    path = Path(filepath)

    if not path.exists():
        return {'exists': False}

    stat = path.stat()

    return {
        'exists': True,
        'name': path.name,
        'extension': path.suffix.lower(),
        'size_bytes': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
    }


def chunk_list(lst: list, chunk_size: int) -> List[list]:
    """
    Split a list into chunks.

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(data: dict, *keys, default=None):
    """
    Safely get nested dictionary values.

    Args:
        data: Dictionary
        *keys: Keys to traverse
        default: Default value if not found

    Returns:
        Value or default
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data
