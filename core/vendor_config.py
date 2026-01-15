"""
Vendor Configuration Module

Provides configuration-driven vendor support through YAML files.
New vendors can be added by creating a YAML configuration file
without any code changes.

Usage:
    from core.vendor_config import VendorConfigManager

    manager = VendorConfigManager()
    vendor = manager.detect_vendor(filename="fis_proposal.docx", content="FIS HORIZON")
    config = manager.get_vendor_config("fis")
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class VendorConfig:
    """Configuration for a vendor."""
    name: str
    aliases: List[str] = field(default_factory=list)

    # Detection patterns
    filename_patterns: List[str] = field(default_factory=list)
    content_keywords: List[str] = field(default_factory=list)

    # Extraction hints
    table_headers: Dict[str, List[str]] = field(default_factory=dict)

    # Category mapping rules
    category_rules: List[Dict[str, str]] = field(default_factory=list)

    # Fee type mapping
    fee_type_mappings: Dict[str, str] = field(default_factory=dict)

    # Terminology translations
    terminology: Dict[str, str] = field(default_factory=dict)

    # Default values
    defaults: Dict[str, Any] = field(default_factory=dict)

    def get_category(self, product_name: str) -> Optional[str]:
        """Map a product name to a category using rules."""
        product_lower = product_name.lower()
        for rule in self.category_rules:
            pattern = rule.get('pattern', '').lower()
            if pattern and pattern in product_lower:
                return rule.get('category')
        return None

    def get_fee_type(self, original_type: str) -> str:
        """Map a vendor-specific fee type to standard fee type."""
        return self.fee_type_mappings.get(original_type.lower(), original_type)

    def translate_term(self, term: str) -> str:
        """Translate vendor-specific terminology to standard terms."""
        return self.terminology.get(term.lower(), term)


class VendorConfigManager:
    """
    Manages vendor configurations from YAML files.

    Loads vendor configs from the vendors/ directory and provides
    vendor detection and configuration lookup.
    """

    # Standard categories (used for validation)
    STANDARD_CATEGORIES = [
        "Core", "Digital", "EFT", "Risk, Fraud & Compliance",
        "Treasury", "Image Solutions", "Item Processing", "FOS",
        "Lending", "ACH", "Accounts Payable", "Security Plus",
        "Network", "Other"
    ]

    # Standard fee types
    STANDARD_FEE_TYPES = ["Monthly F", "Monthly V", "Annual", "One-Time"]

    def __init__(self, config_dir: str = None):
        """
        Initialize the vendor config manager.

        Args:
            config_dir: Directory containing vendor YAML files
        """
        if config_dir is None:
            # Default to vendors/ folder in project root
            project_root = Path(__file__).parent.parent
            config_dir = str(project_root / "vendors")

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.vendors: Dict[str, VendorConfig] = {}
        self._load_all_configs()

        # Create default configs if none exist
        if not self.vendors:
            self._create_default_configs()
            self._load_all_configs()

        logger.info(f"VendorConfigManager loaded {len(self.vendors)} vendor configs")

    def _load_all_configs(self) -> None:
        """Load all vendor configurations from YAML files."""
        if not YAML_AVAILABLE:
            logger.warning("PyYAML not available, using built-in configs only")
            self._load_builtin_configs()
            return

        # Load from YAML files
        for yaml_file in self.config_dir.glob("*.yaml"):
            try:
                config = self._load_yaml_config(yaml_file)
                if config:
                    self.vendors[config.name.lower()] = config
                    # Also register aliases
                    for alias in config.aliases:
                        self.vendors[alias.lower()] = config
            except Exception as e:
                logger.error(f"Failed to load vendor config {yaml_file}: {e}")

        # Also load .yml files
        for yml_file in self.config_dir.glob("*.yml"):
            try:
                config = self._load_yaml_config(yml_file)
                if config:
                    self.vendors[config.name.lower()] = config
                    for alias in config.aliases:
                        self.vendors[alias.lower()] = config
            except Exception as e:
                logger.error(f"Failed to load vendor config {yml_file}: {e}")

    def _load_yaml_config(self, filepath: Path) -> Optional[VendorConfig]:
        """Load a single vendor config from YAML file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or 'vendor' not in data:
            return None

        vendor_data = data.get('vendor', {})
        detection = data.get('detection', {})
        extraction = data.get('extraction', {})
        mapping = data.get('mapping', {})

        return VendorConfig(
            name=vendor_data.get('name', filepath.stem),
            aliases=vendor_data.get('aliases', []),
            filename_patterns=detection.get('filename_patterns', []),
            content_keywords=detection.get('content_keywords', []),
            table_headers=extraction.get('table_headers', {}),
            category_rules=mapping.get('category_rules', []),
            fee_type_mappings=mapping.get('fee_type_mappings', {}),
            terminology=mapping.get('terminology', {}),
            defaults=data.get('defaults', {})
        )

    def _load_builtin_configs(self) -> None:
        """Load built-in vendor configurations."""
        # FIS
        self.vendors['fis'] = VendorConfig(
            name='FIS',
            aliases=['fis', 'fidelity', 'horizon'],
            filename_patterns=['fis', 'horizon', 'fidelity'],
            content_keywords=['FIS', 'HORIZON', 'Fidelity National'],
            table_headers={
                'monthly_fee': ['Monthly', 'Monthly Fee', 'MRC', 'Recurring'],
                'one_time': ['One-Time', 'Implementation', 'Setup', 'Conversion']
            },
            category_rules=[
                {'pattern': 'horizon', 'category': 'Core'},
                {'pattern': 'core', 'category': 'Core'},
                {'pattern': 'digital', 'category': 'Digital'},
                {'pattern': 'd1', 'category': 'Digital'},
                {'pattern': 'eft', 'category': 'EFT'},
                {'pattern': 'debit', 'category': 'EFT'},
                {'pattern': 'treasury', 'category': 'Treasury'},
                {'pattern': 'lending', 'category': 'Lending'},
                {'pattern': 'risk', 'category': 'Risk, Fraud & Compliance'},
                {'pattern': 'fraud', 'category': 'Risk, Fraud & Compliance'},
            ],
            fee_type_mappings={
                'monthly': 'Monthly F',
                'variable': 'Monthly V',
                'annual': 'Annual',
                'one-time': 'One-Time',
                'implementation': 'One-Time'
            }
        )

        # Jack Henry
        self.vendors['jack_henry'] = VendorConfig(
            name='Jack Henry',
            aliases=['jh', 'jack henry', 'jackhenry', 'silverlake', 'symitar'],
            filename_patterns=['jack', 'henry', 'jh', 'silverlake', 'symitar'],
            content_keywords=['Jack Henry', 'SilverLake', 'Symitar', 'Xperience'],
            table_headers={
                'monthly_fee': ['Monthly Net', 'Monthly', 'MRC'],
                'one_time': ['License Net', 'Install Net', 'One-Time']
            },
            category_rules=[
                {'pattern': 'silverlake', 'category': 'Core'},
                {'pattern': 'core', 'category': 'Core'},
                {'pattern': 'xperience', 'category': 'Core'},
                {'pattern': 'banno', 'category': 'Digital'},
                {'pattern': 'digital', 'category': 'Digital'},
                {'pattern': 'onboard', 'category': 'Digital'},
            ],
            fee_type_mappings={
                'monthly net': 'Monthly F',
                'license net': 'One-Time',
                'install net': 'One-Time',
                'maintenance': 'Monthly F'
            }
        )
        self.vendors['jh'] = self.vendors['jack_henry']

        # CSI
        self.vendors['csi'] = VendorConfig(
            name='CSI',
            aliases=['csi', 'computer services', 'nupoint'],
            filename_patterns=['csi', 'nupoint', 'computer services'],
            content_keywords=['CSI', 'NuPoint', 'Computer Services Inc'],
            category_rules=[
                {'pattern': 'nupoint', 'category': 'Core'},
                {'pattern': 'core', 'category': 'Core'},
                {'pattern': 'digital', 'category': 'Digital'},
            ]
        )

        # Fiserv
        self.vendors['fiserv'] = VendorConfig(
            name='Fiserv',
            aliases=['fiserv', 'dna', 'premier', 'precision'],
            filename_patterns=['fiserv', 'dna', 'premier'],
            content_keywords=['Fiserv', 'DNA', 'Premier', 'Precision'],
            category_rules=[
                {'pattern': 'dna', 'category': 'Core'},
                {'pattern': 'premier', 'category': 'Core'},
                {'pattern': 'digital', 'category': 'Digital'},
            ]
        )

        # Finastra
        self.vendors['finastra'] = VendorConfig(
            name='Finastra',
            aliases=['finastra', 'fusion', 'misys'],
            filename_patterns=['finastra', 'fusion', 'misys'],
            content_keywords=['Finastra', 'Fusion', 'FusionBanking'],
            category_rules=[
                {'pattern': 'fusion', 'category': 'Core'},
                {'pattern': 'core', 'category': 'Core'},
            ]
        )

    def _create_default_configs(self) -> None:
        """Create default vendor YAML configuration files."""
        if not YAML_AVAILABLE:
            return

        # FIS config
        fis_config = {
            'vendor': {
                'name': 'FIS',
                'aliases': ['fis', 'fidelity', 'horizon']
            },
            'detection': {
                'filename_patterns': ['fis', 'horizon', 'fidelity'],
                'content_keywords': ['FIS', 'HORIZON', 'Fidelity National', 'FIS Investment Summary']
            },
            'extraction': {
                'table_headers': {
                    'monthly_fee': ['Monthly', 'Monthly Fee', 'MRC', 'Recurring', 'New Pricing'],
                    'one_time': ['One-Time', 'Implementation', 'Setup', 'Conversion', 'One-Time Investment']
                }
            },
            'mapping': {
                'category_rules': [
                    {'pattern': 'HORIZON', 'category': 'Core'},
                    {'pattern': 'Core:', 'category': 'Core'},
                    {'pattern': 'Digital:', 'category': 'Digital'},
                    {'pattern': 'D1 Flex', 'category': 'Digital'},
                    {'pattern': 'EFT:', 'category': 'EFT'},
                    {'pattern': 'Debit', 'category': 'EFT'},
                    {'pattern': 'Treasury:', 'category': 'Treasury'},
                    {'pattern': 'Lending:', 'category': 'Lending'},
                    {'pattern': 'Risk', 'category': 'Risk, Fraud & Compliance'},
                    {'pattern': 'Fraud', 'category': 'Risk, Fraud & Compliance'},
                    {'pattern': 'Image', 'category': 'Image Solutions'},
                    {'pattern': 'Item Processing', 'category': 'Item Processing'},
                    {'pattern': 'FOS', 'category': 'FOS'},
                ],
                'fee_type_mappings': {
                    'monthly': 'Monthly F',
                    'per item': 'Monthly V',
                    'per transaction': 'Monthly V',
                    'annual': 'Annual',
                    'one-time': 'One-Time',
                    'implementation': 'One-Time'
                },
                'terminology': {
                    'mrc': 'Monthly Fee',
                    'nrc': 'One-Time Fee',
                    'signing bonus': 'One-Time Credit',
                    'conversion credit': 'One-Time Credit'
                }
            },
            'defaults': {
                'contract_term': 7,
                'annual_increase': 0.03
            }
        }

        # Jack Henry config
        jh_config = {
            'vendor': {
                'name': 'Jack Henry',
                'aliases': ['jh', 'jack henry', 'jackhenry', 'silverlake', 'symitar']
            },
            'detection': {
                'filename_patterns': ['jack', 'henry', 'jh', 'silverlake', 'symitar'],
                'content_keywords': ['Jack Henry', 'SilverLake', 'Symitar', 'Xperience', 'JHA']
            },
            'extraction': {
                'table_headers': {
                    'monthly_fee': ['Monthly Net', 'Monthly List', 'Monthly', 'MRC'],
                    'one_time': ['License Net', 'Install Net', 'One-Time', 'License List']
                }
            },
            'mapping': {
                'category_rules': [
                    {'pattern': 'SilverLake', 'category': 'Core'},
                    {'pattern': 'Xperience', 'category': 'Core'},
                    {'pattern': 'Core', 'category': 'Core'},
                    {'pattern': 'Banno', 'category': 'Digital'},
                    {'pattern': 'Digital', 'category': 'Digital'},
                    {'pattern': 'OnBoard', 'category': 'Digital'},
                    {'pattern': 'iPay', 'category': 'Digital'},
                    {'pattern': 'Teller', 'category': 'Core'},
                ],
                'fee_type_mappings': {
                    'monthly net': 'Monthly F',
                    'monthly list': 'Monthly F',
                    'license net': 'One-Time',
                    'install net': 'One-Time',
                    'maintenance': 'Monthly F'
                }
            },
            'defaults': {
                'contract_term': 7,
                'annual_increase': 0.03
            }
        }

        # CSI config
        csi_config = {
            'vendor': {
                'name': 'CSI',
                'aliases': ['csi', 'computer services', 'nupoint']
            },
            'detection': {
                'filename_patterns': ['csi', 'nupoint', 'computer_services'],
                'content_keywords': ['CSI', 'NuPoint', 'Computer Services Inc']
            },
            'mapping': {
                'category_rules': [
                    {'pattern': 'NuPoint', 'category': 'Core'},
                    {'pattern': 'Core', 'category': 'Core'},
                    {'pattern': 'Digital', 'category': 'Digital'},
                    {'pattern': 'Mobile', 'category': 'Digital'},
                ]
            }
        }

        # Generic/Unknown vendor config
        generic_config = {
            'vendor': {
                'name': 'Generic',
                'aliases': ['generic', 'unknown', 'other']
            },
            'detection': {
                'filename_patterns': [],
                'content_keywords': []
            },
            'mapping': {
                'category_rules': [
                    {'pattern': 'core', 'category': 'Core'},
                    {'pattern': 'digital', 'category': 'Digital'},
                    {'pattern': 'mobile', 'category': 'Digital'},
                    {'pattern': 'online', 'category': 'Digital'},
                    {'pattern': 'card', 'category': 'EFT'},
                    {'pattern': 'debit', 'category': 'EFT'},
                    {'pattern': 'ach', 'category': 'ACH'},
                    {'pattern': 'wire', 'category': 'Treasury'},
                    {'pattern': 'treasury', 'category': 'Treasury'},
                    {'pattern': 'lending', 'category': 'Lending'},
                    {'pattern': 'loan', 'category': 'Lending'},
                    {'pattern': 'risk', 'category': 'Risk, Fraud & Compliance'},
                    {'pattern': 'fraud', 'category': 'Risk, Fraud & Compliance'},
                    {'pattern': 'compliance', 'category': 'Risk, Fraud & Compliance'},
                ],
                'fee_type_mappings': {
                    'monthly': 'Monthly F',
                    'per month': 'Monthly F',
                    'recurring': 'Monthly F',
                    'variable': 'Monthly V',
                    'per transaction': 'Monthly V',
                    'per item': 'Monthly V',
                    'annual': 'Annual',
                    'yearly': 'Annual',
                    'one-time': 'One-Time',
                    'setup': 'One-Time',
                    'implementation': 'One-Time',
                    'license': 'One-Time'
                }
            }
        }

        # Write configs to files
        configs = {
            'fis.yaml': fis_config,
            'jack_henry.yaml': jh_config,
            'csi.yaml': csi_config,
            'generic.yaml': generic_config
        }

        for filename, config in configs.items():
            filepath = self.config_dir / filename
            if not filepath.exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                logger.info(f"Created default vendor config: {filepath}")

    def detect_vendor(
        self,
        filename: str = None,
        content: str = None
    ) -> Tuple[Optional[str], float]:
        """
        Detect vendor from filename and/or content.

        Args:
            filename: Name of the file
            content: Text content from the document

        Returns:
            Tuple of (vendor_name, confidence_score)
        """
        scores: Dict[str, float] = {}

        for name, config in self.vendors.items():
            if name in ['generic', 'unknown', 'other']:
                continue

            score = 0.0

            # Check filename patterns
            if filename:
                filename_lower = filename.lower()
                for pattern in config.filename_patterns:
                    if pattern.lower() in filename_lower:
                        score += 0.4
                        break

            # Check content keywords
            if content:
                content_lower = content.lower()
                keyword_matches = 0
                for keyword in config.content_keywords:
                    if keyword.lower() in content_lower:
                        keyword_matches += 1

                if keyword_matches > 0:
                    score += min(0.6, 0.2 * keyword_matches)

            if score > 0:
                # Use the main vendor name, not alias
                main_name = config.name
                if main_name not in scores or scores[main_name] < score:
                    scores[main_name] = score

        if scores:
            best_vendor = max(scores, key=scores.get)
            return best_vendor, scores[best_vendor]

        return None, 0.0

    def get_vendor_config(self, vendor_name: str) -> VendorConfig:
        """
        Get configuration for a vendor.

        Args:
            vendor_name: Name or alias of the vendor

        Returns:
            VendorConfig for the vendor (or generic if not found)
        """
        vendor_lower = vendor_name.lower().replace(' ', '_').replace('-', '_')

        if vendor_lower in self.vendors:
            return self.vendors[vendor_lower]

        # Try partial match
        for name, config in self.vendors.items():
            if vendor_lower in name or name in vendor_lower:
                return config

        # Return generic config
        if 'generic' in self.vendors:
            return self.vendors['generic']

        # Create a basic generic config
        return VendorConfig(name=vendor_name)

    def list_vendors(self) -> List[str]:
        """Get list of all configured vendor names (not aliases)."""
        seen = set()
        vendors = []
        for config in self.vendors.values():
            if config.name not in seen:
                seen.add(config.name)
                vendors.append(config.name)
        return sorted(vendors)

    def add_vendor(self, config: VendorConfig, save_yaml: bool = True) -> None:
        """
        Add a new vendor configuration.

        Args:
            config: VendorConfig to add
            save_yaml: Whether to save to YAML file
        """
        self.vendors[config.name.lower()] = config
        for alias in config.aliases:
            self.vendors[alias.lower()] = config

        if save_yaml and YAML_AVAILABLE:
            self._save_vendor_yaml(config)

        logger.info(f"Added vendor config: {config.name}")

    def _save_vendor_yaml(self, config: VendorConfig) -> None:
        """Save a vendor config to YAML file."""
        filename = config.name.lower().replace(' ', '_') + '.yaml'
        filepath = self.config_dir / filename

        data = {
            'vendor': {
                'name': config.name,
                'aliases': config.aliases
            },
            'detection': {
                'filename_patterns': config.filename_patterns,
                'content_keywords': config.content_keywords
            },
            'extraction': {
                'table_headers': config.table_headers
            },
            'mapping': {
                'category_rules': config.category_rules,
                'fee_type_mappings': config.fee_type_mappings,
                'terminology': config.terminology
            },
            'defaults': config.defaults
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Saved vendor config to: {filepath}")


# Global instance
_vendor_manager: Optional[VendorConfigManager] = None


def get_vendor_manager(config_dir: str = None) -> VendorConfigManager:
    """Get or create the global vendor config manager."""
    global _vendor_manager
    if _vendor_manager is None:
        _vendor_manager = VendorConfigManager(config_dir)
    return _vendor_manager
