"""
Bucket Router Module

Routes extraction results to appropriate output destinations:
- Bucket 1 (Auto): Items with >= 90% confidence -> Excel auto-population
- Bucket 2 (Review): Items with < 90% confidence -> Review report
"""

import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field

from .quality_assurance import QAResult, QABucket, QualityAssurance
from ..config import CONFIDENCE_THRESHOLDS

logger = logging.getLogger(__name__)


@dataclass
class BucketResult:
    """Result of bucket routing."""
    bucket1_items: List[Dict] = field(default_factory=list)  # Auto-populate
    bucket2_items: List[Dict] = field(default_factory=list)  # Manual review
    routing_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucket1_count": len(self.bucket1_items),
            "bucket2_count": len(self.bucket2_items),
            "bucket1_items": self.bucket1_items,
            "bucket2_items": self.bucket2_items,
            "routing_summary": self.routing_summary
        }


class BucketRouter:
    """
    Routes extraction results to appropriate buckets based on QA results.

    Bucket 1 (Auto-Populate):
        - Items with confidence >= 90%
        - All QA checks passed
        - Safe for automatic Excel population

    Bucket 2 (Manual Review):
        - Items with confidence < 90%
        - Items with failed or warning QA checks
        - Requires human verification before population
    """

    def __init__(
        self,
        auto_threshold: float = None,
        review_threshold: float = None
    ):
        """
        Initialize the bucket router.

        Args:
            auto_threshold: Confidence threshold for auto-accept (default 0.90)
            review_threshold: Confidence threshold for review vs reject (default 0.70)
        """
        self.auto_threshold = auto_threshold or CONFIDENCE_THRESHOLDS['auto_accept']
        self.review_threshold = review_threshold or CONFIDENCE_THRESHOLDS['manual_review']

        logger.info(
            f"BucketRouter initialized: auto >= {self.auto_threshold:.0%}, "
            f"review >= {self.review_threshold:.0%}"
        )

    def route(
        self,
        line_items: List[Dict],
        qa_result: QAResult
    ) -> BucketResult:
        """
        Route line items to appropriate buckets based on QA results.

        Args:
            line_items: All extracted line items
            qa_result: QA validation results

        Returns:
            BucketResult with items routed to buckets
        """
        result = BucketResult()

        # Use QA results to route items
        for item in line_items:
            confidence = item.get('overall_confidence', 0.85)
            item_name = item.get('solution_name', 'Unknown')

            # Check if item was flagged in QA
            is_failed = any(
                i.get('solution_name') == item_name
                for i in qa_result.failed_items
            )
            is_flagged = any(
                i.get('solution_name') == item_name
                for i in qa_result.flagged_items
            )

            # Add routing info to item
            item_with_routing = item.copy()
            item_with_routing['_routing'] = {
                'confidence': confidence,
                'is_flagged': is_flagged,
                'is_failed': is_failed
            }

            # Route to appropriate bucket
            if is_failed or confidence < self.review_threshold:
                # Below review threshold or failed QA - needs manual entry
                item_with_routing['_routing']['reason'] = 'Low confidence or QA failure'
                item_with_routing['_routing']['action'] = 'manual_entry'
                result.bucket2_items.append(item_with_routing)

            elif is_flagged or confidence < self.auto_threshold:
                # Between thresholds or flagged - needs review
                item_with_routing['_routing']['reason'] = 'Below auto-accept threshold'
                item_with_routing['_routing']['action'] = 'quick_review'
                result.bucket2_items.append(item_with_routing)

            else:
                # High confidence and passed QA - auto-populate
                item_with_routing['_routing']['reason'] = 'High confidence, all checks passed'
                item_with_routing['_routing']['action'] = 'auto_populate'
                result.bucket1_items.append(item_with_routing)

        # Generate routing summary
        result.routing_summary = self._generate_summary(result, qa_result)

        logger.info(
            f"Routing complete: {len(result.bucket1_items)} to auto-populate, "
            f"{len(result.bucket2_items)} to review"
        )

        return result

    def route_with_qa(
        self,
        line_items: List[Dict],
        stated_totals: Dict = None
    ) -> Tuple[BucketResult, QAResult]:
        """
        Convenience method that runs QA and routes in one call.

        Args:
            line_items: Extracted line items
            stated_totals: Document stated totals for validation

        Returns:
            Tuple of (BucketResult, QAResult)
        """
        qa = QualityAssurance()
        qa_result = qa.validate(line_items, stated_totals)
        bucket_result = self.route(line_items, qa_result)

        return bucket_result, qa_result

    def _generate_summary(
        self,
        result: BucketResult,
        qa_result: QAResult
    ) -> Dict[str, Any]:
        """Generate routing summary."""
        total = len(result.bucket1_items) + len(result.bucket2_items)

        # Calculate average confidence per bucket
        bucket1_conf = 0.0
        if result.bucket1_items:
            bucket1_conf = sum(
                i.get('overall_confidence', 0)
                for i in result.bucket1_items
            ) / len(result.bucket1_items)

        bucket2_conf = 0.0
        if result.bucket2_items:
            bucket2_conf = sum(
                i.get('overall_confidence', 0)
                for i in result.bucket2_items
            ) / len(result.bucket2_items)

        # Count by action type
        auto_count = sum(
            1 for i in result.bucket1_items
            if i.get('_routing', {}).get('action') == 'auto_populate'
        )
        review_count = sum(
            1 for i in result.bucket2_items
            if i.get('_routing', {}).get('action') == 'quick_review'
        )
        manual_count = sum(
            1 for i in result.bucket2_items
            if i.get('_routing', {}).get('action') == 'manual_entry'
        )

        return {
            "total_items": total,
            "bucket1_auto_populate": len(result.bucket1_items),
            "bucket2_manual_review": len(result.bucket2_items),
            "auto_populate_rate": f"{len(result.bucket1_items) / total * 100:.1f}%" if total > 0 else "0%",
            "bucket1_avg_confidence": f"{bucket1_conf:.1%}",
            "bucket2_avg_confidence": f"{bucket2_conf:.1%}",
            "action_breakdown": {
                "auto_populate": auto_count,
                "quick_review": review_count,
                "manual_entry": manual_count
            },
            "qa_overall_confidence": f"{qa_result.overall_confidence:.1%}",
            "qa_bucket": qa_result.bucket.value,
            "estimated_time_saved": self._estimate_time_saved(result)
        }

    def _estimate_time_saved(self, result: BucketResult) -> str:
        """Estimate time saved by auto-population."""
        # Assume 2 minutes per manual entry, 30 seconds per review
        auto_items = len(result.bucket1_items)
        review_items = sum(
            1 for i in result.bucket2_items
            if i.get('_routing', {}).get('action') == 'quick_review'
        )

        # Time saved = auto items * 2 min + review items * 1.5 min (vs 2 min manual)
        minutes_saved = (auto_items * 2) + (review_items * 1.5)

        if minutes_saved >= 60:
            return f"{minutes_saved / 60:.1f} hours"
        else:
            return f"{minutes_saved:.0f} minutes"

    def get_bucket1_for_excel(self, bucket_result: BucketResult) -> List[Dict]:
        """
        Get Bucket 1 items formatted for Excel population.

        Removes internal routing metadata and returns clean items.
        """
        clean_items = []
        for item in bucket_result.bucket1_items:
            clean_item = {k: v for k, v in item.items() if not k.startswith('_')}
            clean_items.append(clean_item)
        return clean_items

    def get_bucket2_for_report(self, bucket_result: BucketResult) -> List[Dict]:
        """
        Get Bucket 2 items formatted for review report.

        Includes routing metadata for context.
        """
        return bucket_result.bucket2_items
