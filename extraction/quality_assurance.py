"""
Quality Assurance Module

Implements the 4-layer QA system for extraction validation:
1. Confidence Scoring - Per-field and per-item confidence tracking
2. Cross-Validation - Sum checks, rate calculations, consistency
3. Business Rules - Sanity checks, required fields, valid ranges
4. Source Traceability - Track where each value was extracted from
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from ..config import QA_CONFIG, CONFIDENCE_THRESHOLDS

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation result status."""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class QABucket(Enum):
    """Destination bucket for extraction results."""
    AUTO_ACCEPT = "bucket_1_auto"      # >= 90% confidence, all checks pass
    QUICK_REVIEW = "bucket_2_review"   # 70-90% confidence or minor issues
    MANUAL_ENTRY = "bucket_2_manual"   # < 70% confidence or critical issues


@dataclass
class ValidationCheck:
    """Result of a single validation check."""
    check_name: str
    layer: str  # "confidence", "cross_validation", "business_rules", "traceability"
    status: ValidationStatus
    message: str
    expected: Any = None
    actual: Any = None
    item_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_name": self.check_name,
            "layer": self.layer,
            "status": self.status.value,
            "message": self.message,
            "expected": self.expected,
            "actual": self.actual,
            "item_name": self.item_name
        }


@dataclass
class QAResult:
    """Complete QA validation result for an extraction."""
    passed: bool
    overall_confidence: float
    bucket: QABucket
    checks: List[ValidationCheck] = field(default_factory=list)
    passed_items: List[Dict] = field(default_factory=list)
    flagged_items: List[Dict] = field(default_factory=list)
    failed_items: List[Dict] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "overall_confidence": self.overall_confidence,
            "bucket": self.bucket.value,
            "checks": [c.to_dict() for c in self.checks],
            "passed_items_count": len(self.passed_items),
            "flagged_items_count": len(self.flagged_items),
            "failed_items_count": len(self.failed_items),
            "passed_items": self.passed_items,
            "flagged_items": self.flagged_items,
            "failed_items": self.failed_items,
            "summary": self.summary
        }


class QualityAssurance:
    """
    Quality Assurance system for extraction validation.

    Implements 4-layer validation:
    1. Confidence Scoring
    2. Cross-Validation
    3. Business Rules
    4. Source Traceability
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize QA system.

        Args:
            config: Optional QA configuration override
        """
        self.config = config or QA_CONFIG
        self.thresholds = CONFIDENCE_THRESHOLDS

        logger.info("QualityAssurance initialized")

    def validate(
        self,
        line_items: List[Dict],
        stated_totals: Optional[Dict] = None,
        calculations: Optional[Dict] = None
    ) -> QAResult:
        """
        Run full QA validation on extraction results.

        Args:
            line_items: List of extracted line items
            stated_totals: Document's stated totals (for cross-validation)
            calculations: Calculated projections

        Returns:
            QAResult with validation status and routing decision
        """
        result = QAResult(
            passed=True,
            overall_confidence=0.0,
            bucket=QABucket.AUTO_ACCEPT
        )

        if not line_items:
            result.passed = False
            result.bucket = QABucket.MANUAL_ENTRY
            result.checks.append(ValidationCheck(
                check_name="Empty Extraction",
                layer="business_rules",
                status=ValidationStatus.FAILED,
                message="No line items extracted"
            ))
            return result

        # Layer 1: Confidence Scoring
        if self.config.get('enable_confidence_check', True):
            self._layer1_confidence_scoring(line_items, result)

        # Layer 2: Cross-Validation
        if self.config.get('enable_cross_validation', True):
            self._layer2_cross_validation(line_items, stated_totals, calculations, result)

        # Layer 3: Business Rules
        if self.config.get('enable_business_rules', True):
            self._layer3_business_rules(line_items, result)

        # Layer 4: Source Traceability
        if self.config.get('enable_traceability', True):
            self._layer4_traceability(line_items, result)

        # Calculate overall confidence and determine bucket
        result.overall_confidence = self._calculate_overall_confidence(line_items, result)
        result.bucket = self._determine_bucket(result)
        result.passed = result.bucket == QABucket.AUTO_ACCEPT

        # Generate summary
        result.summary = self._generate_summary(result)

        logger.info(
            f"QA complete: {len(result.passed_items)} passed, "
            f"{len(result.flagged_items)} flagged, "
            f"{len(result.failed_items)} failed. "
            f"Bucket: {result.bucket.value}"
        )

        return result

    def _layer1_confidence_scoring(
        self,
        line_items: List[Dict],
        result: QAResult
    ) -> None:
        """Layer 1: Check confidence scores for each item and field."""
        min_field_confidence = self.config.get('min_field_confidence', 0.85)
        min_item_confidence = self.config.get('min_item_confidence', 0.90)

        for item in line_items:
            item_name = item.get('solution_name', 'Unknown')
            item_confidence = item.get('overall_confidence', 0.85)
            field_confidences = item.get('field_confidence', {})

            # Check overall item confidence
            if item_confidence >= min_item_confidence:
                result.passed_items.append(item)
                result.checks.append(ValidationCheck(
                    check_name="Item Confidence",
                    layer="confidence",
                    status=ValidationStatus.PASSED,
                    message=f"Item confidence {item_confidence:.1%} meets threshold",
                    expected=min_item_confidence,
                    actual=item_confidence,
                    item_name=item_name
                ))
            elif item_confidence >= self.thresholds['manual_review']:
                result.flagged_items.append(item)
                result.checks.append(ValidationCheck(
                    check_name="Item Confidence",
                    layer="confidence",
                    status=ValidationStatus.WARNING,
                    message=f"Item confidence {item_confidence:.1%} below auto-accept threshold",
                    expected=min_item_confidence,
                    actual=item_confidence,
                    item_name=item_name
                ))
            else:
                result.failed_items.append(item)
                result.checks.append(ValidationCheck(
                    check_name="Item Confidence",
                    layer="confidence",
                    status=ValidationStatus.FAILED,
                    message=f"Item confidence {item_confidence:.1%} below review threshold",
                    expected=self.thresholds['manual_review'],
                    actual=item_confidence,
                    item_name=item_name
                ))

            # Check individual field confidences
            for field_name, field_conf in field_confidences.items():
                if field_conf < min_field_confidence:
                    result.checks.append(ValidationCheck(
                        check_name=f"Field Confidence: {field_name}",
                        layer="confidence",
                        status=ValidationStatus.WARNING,
                        message=f"Field '{field_name}' confidence {field_conf:.1%} below threshold",
                        expected=min_field_confidence,
                        actual=field_conf,
                        item_name=item_name
                    ))

    def _layer2_cross_validation(
        self,
        line_items: List[Dict],
        stated_totals: Optional[Dict],
        calculations: Optional[Dict],
        result: QAResult
    ) -> None:
        """Layer 2: Cross-validate calculated totals against stated totals."""
        sum_tolerance = self.config.get('sum_tolerance_percent', 0.02)
        rate_tolerance = self.config.get('rate_tolerance_percent', 0.01)

        # Calculate totals from line items
        calc_monthly = sum(
            item.get('monthly_fee', 0) or 0
            for item in line_items
            if item.get('fee_type') in ['Monthly F', 'Monthly V']
        )
        calc_annual = sum(
            item.get('annual_fee', 0) or 0
            for item in line_items
            if item.get('fee_type') == 'Annual'
        )
        calc_one_time = sum(
            item.get('one_time_fee', 0) or 0
            for item in line_items
            if item.get('fee_type') == 'One-Time'
        )

        # Compare with stated totals
        if stated_totals:
            stated_monthly = stated_totals.get('monthly_total', 0)
            if stated_monthly > 0:
                diff = abs(calc_monthly - stated_monthly) / stated_monthly
                result.checks.append(ValidationCheck(
                    check_name="Sum Verification - Monthly",
                    layer="cross_validation",
                    status=ValidationStatus.PASSED if diff <= sum_tolerance else ValidationStatus.WARNING,
                    message=f"Monthly sum difference: {diff:.1%}",
                    expected=stated_monthly,
                    actual=calc_monthly
                ))

            stated_one_time = stated_totals.get('one_time_total', 0)
            if stated_one_time > 0:
                diff = abs(calc_one_time - stated_one_time) / stated_one_time
                result.checks.append(ValidationCheck(
                    check_name="Sum Verification - One-Time",
                    layer="cross_validation",
                    status=ValidationStatus.PASSED if diff <= sum_tolerance else ValidationStatus.WARNING,
                    message=f"One-time sum difference: {diff:.1%}",
                    expected=stated_one_time,
                    actual=calc_one_time
                ))

        # Validate rate consistency (monthly * 12 should approximate annual where applicable)
        for item in line_items:
            monthly = item.get('monthly_fee', 0) or 0
            annual = item.get('annual_fee', 0) or 0

            if monthly > 0 and annual > 0:
                expected_annual = monthly * 12
                if abs(expected_annual - annual) / annual > rate_tolerance:
                    result.checks.append(ValidationCheck(
                        check_name="Rate Consistency",
                        layer="cross_validation",
                        status=ValidationStatus.WARNING,
                        message=f"Monthly ({monthly}) * 12 != Annual ({annual})",
                        expected=expected_annual,
                        actual=annual,
                        item_name=item.get('solution_name')
                    ))

    def _layer3_business_rules(
        self,
        line_items: List[Dict],
        result: QAResult
    ) -> None:
        """Layer 3: Apply business rules validation."""
        allow_zero_required = self.config.get('allow_zero_required_items', False)
        max_monthly = self.config.get('max_monthly_fee', 500000)
        max_one_time = self.config.get('max_one_time_fee', 5000000)

        for item in line_items:
            item_name = item.get('solution_name', 'Unknown')
            is_optional = item.get('optional', False)

            # Rule 1: Required items must have pricing
            if not is_optional and not allow_zero_required:
                amounts = [
                    item.get('monthly_fee', 0) or 0,
                    item.get('annual_fee', 0) or 0,
                    item.get('one_time_fee', 0) or 0,
                    item.get('per_unit_rate', 0) or 0
                ]
                if all(amt == 0 for amt in amounts):
                    result.checks.append(ValidationCheck(
                        check_name="Zero Pricing Check",
                        layer="business_rules",
                        status=ValidationStatus.FAILED,
                        message="Required item has $0 pricing",
                        item_name=item_name
                    ))
                    # Move from passed to failed if not already there
                    if item in result.passed_items:
                        result.passed_items.remove(item)
                        result.failed_items.append(item)

            # Rule 2: Amounts within reasonable ranges
            monthly = item.get('monthly_fee', 0) or 0
            one_time = item.get('one_time_fee', 0) or 0

            if monthly > max_monthly:
                result.checks.append(ValidationCheck(
                    check_name="Monthly Fee Range",
                    layer="business_rules",
                    status=ValidationStatus.WARNING,
                    message=f"Monthly fee ${monthly:,.2f} exceeds sanity check limit",
                    expected=f"<= ${max_monthly:,.2f}",
                    actual=monthly,
                    item_name=item_name
                ))

            if one_time > max_one_time:
                result.checks.append(ValidationCheck(
                    check_name="One-Time Fee Range",
                    layer="business_rules",
                    status=ValidationStatus.WARNING,
                    message=f"One-time fee ${one_time:,.2f} exceeds sanity check limit",
                    expected=f"<= ${max_one_time:,.2f}",
                    actual=one_time,
                    item_name=item_name
                ))

            # Rule 3: No negative amounts (except credits)
            category = item.get('category', '')
            if 'Credit' not in category:
                for field_name in ['monthly_fee', 'annual_fee', 'one_time_fee', 'per_unit_rate']:
                    amount = item.get(field_name, 0) or 0
                    if amount < 0:
                        result.checks.append(ValidationCheck(
                            check_name="Negative Amount Check",
                            layer="business_rules",
                            status=ValidationStatus.FAILED,
                            message=f"Negative amount in non-credit item",
                            expected=">= 0",
                            actual=amount,
                            item_name=item_name
                        ))

            # Rule 4: Required fields present
            required_fields = ['solution_name', 'fee_type', 'category']
            for field_name in required_fields:
                if not item.get(field_name):
                    result.checks.append(ValidationCheck(
                        check_name=f"Required Field: {field_name}",
                        layer="business_rules",
                        status=ValidationStatus.FAILED,
                        message=f"Missing required field: {field_name}",
                        item_name=item_name
                    ))

            # Rule 5: Valid fee_type
            valid_fee_types = ['Monthly F', 'Monthly V', 'Annual', 'One-Time']
            if item.get('fee_type') not in valid_fee_types:
                result.checks.append(ValidationCheck(
                    check_name="Valid Fee Type",
                    layer="business_rules",
                    status=ValidationStatus.WARNING,
                    message=f"Invalid fee_type: {item.get('fee_type')}",
                    expected=valid_fee_types,
                    actual=item.get('fee_type'),
                    item_name=item_name
                ))

    def _layer4_traceability(
        self,
        line_items: List[Dict],
        result: QAResult
    ) -> None:
        """Layer 4: Check source traceability for each item."""
        require_source = self.config.get('require_source_context', True)

        if not require_source:
            return

        for item in line_items:
            item_name = item.get('solution_name', 'Unknown')
            source_location = item.get('source_location', '')
            source_text = item.get('source_text', '')

            if not source_location and not source_text:
                result.checks.append(ValidationCheck(
                    check_name="Source Traceability",
                    layer="traceability",
                    status=ValidationStatus.WARNING,
                    message="Missing source context for extracted item",
                    item_name=item_name
                ))

    def _calculate_overall_confidence(
        self,
        line_items: List[Dict],
        result: QAResult
    ) -> float:
        """Calculate overall confidence score."""
        if not line_items:
            return 0.0

        # Start with average item confidence
        confidences = [
            item.get('overall_confidence', 0.85)
            for item in line_items
        ]
        avg_confidence = sum(confidences) / len(confidences)

        # Count issues by severity
        failed_checks = sum(
            1 for c in result.checks
            if c.status == ValidationStatus.FAILED
        )
        warning_checks = sum(
            1 for c in result.checks
            if c.status == ValidationStatus.WARNING
        )

        # Reduce confidence based on issues
        # Each failed check reduces by 5%, each warning by 1%
        reduction = (failed_checks * 0.05) + (warning_checks * 0.01)
        final_confidence = max(0.0, avg_confidence - reduction)

        return round(final_confidence, 4)

    def _determine_bucket(self, result: QAResult) -> QABucket:
        """Determine which bucket the extraction should go to."""
        # Count critical failures
        critical_failures = sum(
            1 for c in result.checks
            if c.status == ValidationStatus.FAILED
        )

        # If any critical failures, needs manual review
        if critical_failures > 0:
            return QABucket.QUICK_REVIEW

        # If too many failed items, needs manual entry
        total_items = len(result.passed_items) + len(result.flagged_items) + len(result.failed_items)
        if total_items > 0:
            failed_ratio = len(result.failed_items) / total_items
            if failed_ratio > 0.2:  # More than 20% failed
                return QABucket.MANUAL_ENTRY

        # Check overall confidence
        if result.overall_confidence >= self.thresholds['auto_accept']:
            return QABucket.AUTO_ACCEPT
        elif result.overall_confidence >= self.thresholds['manual_review']:
            return QABucket.QUICK_REVIEW
        else:
            return QABucket.MANUAL_ENTRY

    def _generate_summary(self, result: QAResult) -> Dict[str, Any]:
        """Generate a summary of QA results."""
        total_items = len(result.passed_items) + len(result.flagged_items) + len(result.failed_items)
        total_checks = len(result.checks)
        passed_checks = sum(1 for c in result.checks if c.status == ValidationStatus.PASSED)
        warning_checks = sum(1 for c in result.checks if c.status == ValidationStatus.WARNING)
        failed_checks = sum(1 for c in result.checks if c.status == ValidationStatus.FAILED)

        return {
            "total_items": total_items,
            "items_passed": len(result.passed_items),
            "items_flagged": len(result.flagged_items),
            "items_failed": len(result.failed_items),
            "total_checks": total_checks,
            "checks_passed": passed_checks,
            "checks_warning": warning_checks,
            "checks_failed": failed_checks,
            "overall_confidence": f"{result.overall_confidence:.1%}",
            "routing_decision": result.bucket.value,
            "recommendation": self._get_recommendation(result)
        }

    def _get_recommendation(self, result: QAResult) -> str:
        """Get human-readable recommendation based on QA results."""
        if result.bucket == QABucket.AUTO_ACCEPT:
            return "Extraction meets all quality thresholds. Safe for auto-population."
        elif result.bucket == QABucket.QUICK_REVIEW:
            flagged_names = [i.get('solution_name', 'Unknown') for i in result.flagged_items[:5]]
            return f"Review flagged items: {', '.join(flagged_names)}"
        else:
            failed_names = [i.get('solution_name', 'Unknown') for i in result.failed_items[:5]]
            return f"Manual entry required. Failed items: {', '.join(failed_names)}"

    def validate_single_item(self, item: Dict) -> Tuple[QABucket, List[ValidationCheck]]:
        """
        Validate a single line item.

        Args:
            item: Single line item dictionary

        Returns:
            Tuple of (bucket, list of checks)
        """
        result = self.validate([item])
        return result.bucket, result.checks
