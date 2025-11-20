"""
Validators Module

Data validation and formatting utilities for TCO Automation.
"""

import os
import re
from pathlib import Path
from typing import Any, Optional, Tuple, Union


def validate_file_exists(filepath: str, allowed_extensions: list = None) -> Tuple[bool, str]:
    """
    Validate that a file exists and has allowed extension.

    Args:
        filepath: Path to file
        allowed_extensions: List of allowed extensions (e.g., ['.docx', '.xlsx'])

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filepath:
        return False, "File path is empty"

    path = Path(filepath)

    if not path.exists():
        return False, f"File not found: {filepath}"

    if not path.is_file():
        return False, f"Path is not a file: {filepath}"

    if allowed_extensions:
        ext = path.suffix.lower()
        if ext not in [e.lower() for e in allowed_extensions]:
            return False, f"Invalid file extension '{ext}'. Allowed: {allowed_extensions}"

    return True, ""


def validate_output_dir(dirpath: str, create: bool = True) -> Tuple[bool, str]:
    """
    Validate output directory exists or can be created.

    Args:
        dirpath: Path to directory
        create: Whether to create if it doesn't exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not dirpath:
        return False, "Directory path is empty"

    path = Path(dirpath)

    if path.exists():
        if not path.is_dir():
            return False, f"Path exists but is not a directory: {dirpath}"
        if not os.access(dirpath, os.W_OK):
            return False, f"Directory is not writable: {dirpath}"
        return True, ""

    if create:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True, ""
        except Exception as e:
            return False, f"Failed to create directory: {e}"

    return False, f"Directory does not exist: {dirpath}"


def validate_currency(value: Any) -> Tuple[bool, Optional[float], str]:
    """
    Validate and parse a currency value.

    Args:
        value: Value to validate (string, int, or float)

    Returns:
        Tuple of (is_valid, parsed_value, error_message)
    """
    if value is None:
        return True, None, ""

    if isinstance(value, (int, float)):
        return True, float(value), ""

    if isinstance(value, str):
        # Remove currency symbols and whitespace
        cleaned = value.strip()
        cleaned = re.sub(r'[\$,\s]', '', cleaned)

        # Handle parentheses for negative values
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]

        try:
            parsed = float(cleaned)
            return True, parsed, ""
        except ValueError:
            return False, None, f"Invalid currency value: {value}"

    return False, None, f"Unexpected type for currency: {type(value)}"


def validate_percentage(value: Any) -> Tuple[bool, Optional[float], str]:
    """
    Validate and parse a percentage value.

    Args:
        value: Value to validate

    Returns:
        Tuple of (is_valid, parsed_value, error_message)
    """
    if value is None:
        return True, None, ""

    if isinstance(value, (int, float)):
        # Assume already in percentage form (e.g., 5.0 = 5%)
        return True, float(value), ""

    if isinstance(value, str):
        cleaned = value.strip().replace('%', '')

        try:
            parsed = float(cleaned)
            # Check reasonable range
            if parsed < 0 or parsed > 100:
                return False, parsed, f"Percentage out of range: {parsed}%"
            return True, parsed, ""
        except ValueError:
            return False, None, f"Invalid percentage value: {value}"

    return False, None, f"Unexpected type for percentage: {type(value)}"


def format_currency(value: Union[int, float], include_sign: bool = True, decimal_places: int = 2) -> str:
    """
    Format a number as currency.

    Args:
        value: Numeric value
        include_sign: Include $ sign
        decimal_places: Number of decimal places

    Returns:
        Formatted currency string
    """
    if value is None:
        return ""

    # Handle negative values
    negative = value < 0
    abs_value = abs(value)

    # Format with commas
    formatted = f"{abs_value:,.{decimal_places}f}"

    # Add sign
    if include_sign:
        formatted = f"${formatted}"

    # Handle negative
    if negative:
        formatted = f"-{formatted}"

    return formatted


def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format a number as percentage.

    Args:
        value: Numeric value (e.g., 5.0 for 5%)
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if value is None:
        return ""

    return f"{value:.{decimal_places}f}%"


def validate_date(value: str, formats: list = None) -> Tuple[bool, Optional[str], str]:
    """
    Validate and normalize a date string.

    Args:
        value: Date string
        formats: List of expected formats

    Returns:
        Tuple of (is_valid, normalized_date, error_message)
    """
    from datetime import datetime

    if not value:
        return True, None, ""

    if not formats:
        formats = ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d-%m-%Y']

    for fmt in formats:
        try:
            parsed = datetime.strptime(value.strip(), fmt)
            # Return in standard format
            return True, parsed.strftime('%Y-%m-%d'), ""
        except ValueError:
            continue

    return False, None, f"Invalid date format: {value}"


def validate_term(value: str) -> Tuple[bool, str, str]:
    """
    Validate contract term.

    Args:
        value: Term string (e.g., '5_year', '7-year', '10 year')

    Returns:
        Tuple of (is_valid, normalized_term, error_message)
    """
    if not value:
        return False, "", "Term is empty"

    # Normalize
    normalized = value.lower().strip()
    normalized = re.sub(r'[\s-]', '_', normalized)

    # Valid terms
    valid_terms = {'5_year', '7_year', '10_year'}

    if normalized in valid_terms:
        return True, normalized, ""

    # Try to extract number
    match = re.search(r'(\d+)', normalized)
    if match:
        num = int(match.group(1))
        if num in [5, 7, 10]:
            return True, f"{num}_year", ""

    return False, "", f"Invalid term: {value}. Expected: 5_year, 7_year, or 10_year"


def validate_vendor(value: str) -> Tuple[bool, str, str]:
    """
    Validate vendor name.

    Args:
        value: Vendor string

    Returns:
        Tuple of (is_valid, normalized_vendor, error_message)
    """
    if not value:
        return False, "", "Vendor is empty"

    normalized = value.strip().lower()

    # Vendor mappings
    vendor_map = {
        'fis': 'FIS',
        'jack henry': 'Jack Henry',
        'jackhenry': 'Jack Henry',
        'jh': 'Jack Henry',
        'fiserv': 'Fiserv'
    }

    if normalized in vendor_map:
        return True, vendor_map[normalized], ""

    return False, "", f"Unknown vendor: {value}. Expected: FIS, Jack Henry, or Fiserv"
