"""
Config Module

Configuration files for TCO Automation.
"""

from .extraction_prompts import get_prompt, TCO_SYSTEM_PROMPT

# Re-export from parent config.py
import os
import importlib.util

# Import from config.py (the file, not this package)
config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.py')
spec = importlib.util.spec_from_file_location("config_file", config_file)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)

# Re-export all config values
FEE_TYPES = config_module.FEE_TYPES
VENDORS = config_module.VENDORS
PRODUCT_CATEGORIES = config_module.PRODUCT_CATEGORIES
FIS_BUNDLE_KEYWORDS = config_module.FIS_BUNDLE_KEYWORDS
JH_PRODUCT_FAMILIES = config_module.JH_PRODUCT_FAMILIES
TCO_COLUMNS = config_module.TCO_COLUMNS
DEFAULT_GROWTH_RATE = config_module.DEFAULT_GROWTH_RATE
DEFAULT_CPI_BUNDLE = config_module.DEFAULT_CPI_BUNDLE
DEFAULT_CPI_NON_BUNDLE = config_module.DEFAULT_CPI_NON_BUNDLE
LINE_ITEM_START_ROWS = config_module.LINE_ITEM_START_ROWS

__all__ = [
    'get_prompt', 'TCO_SYSTEM_PROMPT',
    'FEE_TYPES', 'VENDORS', 'PRODUCT_CATEGORIES',
    'FIS_BUNDLE_KEYWORDS', 'JH_PRODUCT_FAMILIES',
    'TCO_COLUMNS', 'DEFAULT_GROWTH_RATE',
    'DEFAULT_CPI_BUNDLE', 'DEFAULT_CPI_NON_BUNDLE',
    'LINE_ITEM_START_ROWS'
]
