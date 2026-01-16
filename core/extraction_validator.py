"""
Extraction Data Validator

Validates extraction JSON data before saving to ensure data quality.
Checks for required fields, data types, and logical consistency.

Usage:
    from core.extraction_validator import validate_extraction, ValidationResult

    result = validate_extraction(data)
    if not result.is_valid:
        print(f"Validation errors: {result.errors}")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import re


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    auto_fixed: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def add_fix(self, message: str):
        """Record an auto-fix that was applied."""
        self.auto_fixed.append(message)


# Required top-level fields
REQUIRED_FIELDS = ['client', 'vendor', 'line_items']

# Optional but recommended fields
RECOMMENDED_FIELDS = ['contract_term', 'document_date', 'proposal_type']

# Required line item fields
REQUIRED_LINE_ITEM_FIELDS = ['solution_name', 'fee_type']

# Numeric fields that should not be None
NUMERIC_LINE_ITEM_FIELDS = ['monthly_fee', 'one_time_fee', 'per_unit_rate']

# Valid fee types
VALID_FEE_TYPES = [
    'Monthly F', 'Monthly V', 'One-Time', 'Annual',
    'Monthly Fixed', 'Monthly Variable', 'Implementation',
    'Setup', 'License', 'Subscription'
]

# Default values for auto-fix
DEFAULTS = {
    'contract_term': 7,
    'monthly_fee': 0.0,
    'one_time_fee': 0.0,
    'per_unit_rate': 0.0,
    'overall_confidence': 0.5,
}


def validate_extraction(
    data: Dict[str, Any],
    auto_fix: bool = True,
    strict: bool = False
) -> ValidationResult:
    """
    Validate extraction data.

    Args:
        data: Extraction data dictionary
        auto_fix: If True, automatically fix minor issues
        strict: If True, warnings become errors

    Returns:
        ValidationResult with any errors/warnings
    """
    result = ValidationResult()

    if not isinstance(data, dict):
        result.add_error("Extraction data must be a dictionary")
        return result

    # Check required fields
    _validate_required_fields(data, result, auto_fix)

    # Check recommended fields
    _validate_recommended_fields(data, result, auto_fix, strict)

    # Validate line items
    _validate_line_items(data, result, auto_fix, strict)

    # Validate contract term
    _validate_contract_term(data, result, auto_fix)

    # Validate client name
    _validate_client_name(data, result)

    # Validate vendor name
    _validate_vendor_name(data, result)

    return result


def _validate_required_fields(
    data: Dict[str, Any],
    result: ValidationResult,
    auto_fix: bool
):
    """Check that required fields are present."""
    for field_name in REQUIRED_FIELDS:
        if field_name not in data:
            if field_name == 'line_items' and auto_fix:
                data['line_items'] = []
                result.add_fix(f"Added empty {field_name} list")
            else:
                result.add_error(f"Missing required field: {field_name}")
        elif data[field_name] is None:
            if field_name == 'line_items':
                if auto_fix:
                    data['line_items'] = []
                    result.add_fix(f"Replaced null {field_name} with empty list")
                else:
                    result.add_error(f"Required field {field_name} is null")
            else:
                result.add_error(f"Required field {field_name} is null")


def _validate_recommended_fields(
    data: Dict[str, Any],
    result: ValidationResult,
    auto_fix: bool,
    strict: bool
):
    """Check recommended fields and auto-fix if possible."""
    for field_name in RECOMMENDED_FIELDS:
        if field_name not in data or data[field_name] is None:
            if field_name in DEFAULTS and auto_fix:
                data[field_name] = DEFAULTS[field_name]
                result.add_fix(f"Set {field_name} to default: {DEFAULTS[field_name]}")
            else:
                msg = f"Missing recommended field: {field_name}"
                if strict:
                    result.add_error(msg)
                else:
                    result.add_warning(msg)


def _validate_line_items(
    data: Dict[str, Any],
    result: ValidationResult,
    auto_fix: bool,
    strict: bool
):
    """Validate line items array."""
    line_items = data.get('line_items', [])

    if not isinstance(line_items, list):
        result.add_error("line_items must be a list")
        return

    for i, item in enumerate(line_items):
        if not isinstance(item, dict):
            result.add_error(f"line_items[{i}] must be a dictionary")
            continue

        # Check required line item fields
        for field_name in REQUIRED_LINE_ITEM_FIELDS:
            if field_name not in item or item[field_name] is None:
                if field_name == 'solution_name':
                    result.add_error(f"line_items[{i}] missing solution_name")
                elif field_name == 'fee_type':
                    if auto_fix:
                        # Try to infer fee type
                        if item.get('monthly_fee', 0) > 0:
                            item['fee_type'] = 'Monthly F'
                            result.add_fix(f"line_items[{i}].fee_type set to 'Monthly F'")
                        elif item.get('one_time_fee', 0) > 0:
                            item['fee_type'] = 'One-Time'
                            result.add_fix(f"line_items[{i}].fee_type set to 'One-Time'")
                        else:
                            item['fee_type'] = 'Monthly F'
                            result.add_fix(f"line_items[{i}].fee_type defaulted to 'Monthly F'")
                    else:
                        result.add_warning(f"line_items[{i}] missing fee_type")

        # Validate and fix numeric fields
        for field_name in NUMERIC_LINE_ITEM_FIELDS:
            value = item.get(field_name)
            if value is None:
                if auto_fix:
                    item[field_name] = DEFAULTS.get(field_name, 0.0)
                    result.add_fix(f"line_items[{i}].{field_name}: null -> {DEFAULTS.get(field_name, 0.0)}")
            elif not isinstance(value, (int, float)):
                try:
                    item[field_name] = float(value)
                    result.add_fix(f"line_items[{i}].{field_name}: converted to float")
                except (ValueError, TypeError):
                    if auto_fix:
                        item[field_name] = 0.0
                        result.add_fix(f"line_items[{i}].{field_name}: invalid value -> 0.0")
                    else:
                        result.add_error(f"line_items[{i}].{field_name} is not a number: {value}")

        # Validate confidence score
        confidence = item.get('overall_confidence')
        if confidence is None:
            if auto_fix:
                item['overall_confidence'] = DEFAULTS['overall_confidence']
                result.add_fix(f"line_items[{i}].overall_confidence set to {DEFAULTS['overall_confidence']}")
        elif not isinstance(confidence, (int, float)):
            if auto_fix:
                item['overall_confidence'] = DEFAULTS['overall_confidence']
                result.add_fix(f"line_items[{i}].overall_confidence: invalid -> {DEFAULTS['overall_confidence']}")
        elif confidence < 0 or confidence > 1:
            msg = f"line_items[{i}].overall_confidence out of range: {confidence}"
            if strict:
                result.add_error(msg)
            else:
                result.add_warning(msg)

        # Validate fee type value
        fee_type = item.get('fee_type')
        if fee_type and fee_type not in VALID_FEE_TYPES:
            # Try to normalize fee type
            normalized = _normalize_fee_type(fee_type)
            if normalized and auto_fix:
                item['fee_type'] = normalized
                result.add_fix(f"line_items[{i}].fee_type: '{fee_type}' -> '{normalized}'")
            else:
                result.add_warning(f"line_items[{i}].fee_type '{fee_type}' is non-standard")

        # Check for negative values
        for field_name in ['monthly_fee', 'one_time_fee']:
            value = item.get(field_name, 0)
            if isinstance(value, (int, float)) and value < 0:
                msg = f"line_items[{i}].{field_name} is negative: {value}"
                if strict:
                    result.add_error(msg)
                else:
                    result.add_warning(msg)


def _validate_contract_term(
    data: Dict[str, Any],
    result: ValidationResult,
    auto_fix: bool
):
    """Validate contract term."""
    contract_term = data.get('contract_term')

    if contract_term is None:
        if auto_fix:
            data['contract_term'] = DEFAULTS['contract_term']
            result.add_fix(f"contract_term set to default: {DEFAULTS['contract_term']}")
        return

    if not isinstance(contract_term, (int, float)):
        try:
            data['contract_term'] = int(contract_term)
            result.add_fix(f"contract_term: converted to int")
        except (ValueError, TypeError):
            if auto_fix:
                data['contract_term'] = DEFAULTS['contract_term']
                result.add_fix(f"contract_term: invalid value -> {DEFAULTS['contract_term']}")
            else:
                result.add_error(f"contract_term is not a number: {contract_term}")
            return

    # Check reasonable range
    if contract_term < 1 or contract_term > 20:
        result.add_warning(f"contract_term {contract_term} is outside typical range (1-20 years)")


def _validate_client_name(data: Dict[str, Any], result: ValidationResult):
    """Validate client name."""
    client = data.get('client')

    if not client:
        result.add_error("client name is empty")
        return

    if client in ['Unknown', 'Not specified', 'null', 'None']:
        result.add_warning(f"client name '{client}' appears to be a placeholder")

    # Check for suspicious patterns
    if re.match(r'^[a-z_]+_extraction', client.lower()):
        result.add_warning(f"client name '{client}' looks like a filename")


def _validate_vendor_name(data: Dict[str, Any], result: ValidationResult):
    """Validate vendor name."""
    vendor = data.get('vendor')

    if not vendor:
        result.add_error("vendor name is empty")
        return

    if vendor in ['Unknown', 'Not specified', 'null', 'None']:
        result.add_warning(f"vendor name '{vendor}' appears to be a placeholder")


def _normalize_fee_type(fee_type: str) -> Optional[str]:
    """Try to normalize a fee type string."""
    fee_type_lower = fee_type.lower().strip()

    mappings = {
        'monthly': 'Monthly F',
        'monthly fixed': 'Monthly F',
        'monthly f': 'Monthly F',
        'monthly variable': 'Monthly V',
        'monthly v': 'Monthly V',
        'variable': 'Monthly V',
        'one-time': 'One-Time',
        'one time': 'One-Time',
        'onetime': 'One-Time',
        'implementation': 'One-Time',
        'setup': 'One-Time',
        'license': 'One-Time',
        'annual': 'Annual',
        'yearly': 'Annual',
    }

    return mappings.get(fee_type_lower)


def validate_and_fix_extraction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and fix extraction data in place.

    Convenience function that validates with auto_fix=True and returns
    the (potentially modified) data.

    Args:
        data: Extraction data dictionary

    Returns:
        The validated (and possibly fixed) data dictionary

    Raises:
        ValueError: If data has unfixable errors
    """
    result = validate_extraction(data, auto_fix=True, strict=False)

    if not result.is_valid:
        raise ValueError(f"Extraction data has errors: {result.errors}")

    return data


def get_validation_summary(result: ValidationResult) -> str:
    """Get a human-readable summary of validation results."""
    lines = []

    if result.is_valid:
        lines.append("✓ Validation passed")
    else:
        lines.append("✗ Validation failed")

    if result.auto_fixed:
        lines.append(f"\nAuto-fixed ({len(result.auto_fixed)}):")
        for fix in result.auto_fixed[:10]:  # Limit to first 10
            lines.append(f"  - {fix}")
        if len(result.auto_fixed) > 10:
            lines.append(f"  ... and {len(result.auto_fixed) - 10} more")

    if result.warnings:
        lines.append(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings[:10]:
            lines.append(f"  ⚠ {warning}")
        if len(result.warnings) > 10:
            lines.append(f"  ... and {len(result.warnings) - 10} more")

    if result.errors:
        lines.append(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            lines.append(f"  ✗ {error}")

    return '\n'.join(lines)
