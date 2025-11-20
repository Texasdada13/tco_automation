"""
Utilities Module

Common utilities and helper functions for TCO Automation.
"""

from .logging_config import setup_logging, get_logger
from .validators import (
    validate_file_exists,
    validate_output_dir,
    validate_currency,
    validate_percentage,
    format_currency,
    format_percentage
)
from .helpers import (
    detect_vendor_from_file,
    generate_output_filename,
    calculate_contract_total,
    merge_extracted_data
)

__all__ = [
    # Logging
    'setup_logging',
    'get_logger',

    # Validators
    'validate_file_exists',
    'validate_output_dir',
    'validate_currency',
    'validate_percentage',
    'format_currency',
    'format_percentage',

    # Helpers
    'detect_vendor_from_file',
    'generate_output_filename',
    'calculate_contract_total',
    'merge_extracted_data'
]
