"""
Cost Normalizer for Apples-to-Apples Vendor Comparison

This module implements:
- Cost normalization to standard 6-bucket taxonomy
- Time normalization (monthly/quarterly to annual)
- Terminology normalization (vendor terms to standard labels)
- Cost-per-unit calculations
- Full traceability and audit trail

Ensures fair comparison across vendors regardless of how they structure pricing.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import re

from .cost_taxonomy import (
    CostBucket,
    CostCategory,
    COST_CATEGORIES,
    TERMINOLOGY_MAPPINGS,
    TIME_NORMALIZATIONS,
    NORMALIZATION_METRICS,
    detect_cost_bucket,
    find_category_by_keywords,
    get_bucket_display_order,
    export_taxonomy_schema
)

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES FOR NORMALIZED OUTPUT
# =============================================================================

@dataclass
class SourceTraceability:
    """
    Traceability information linking normalized data back to source

    Principle 6: Every cost line links to source document
    """
    source_file: str
    extraction_method: str  # 'ai_enhanced', 'raw_table', 'manual'
    source_table_index: Optional[int] = None
    source_row_index: Optional[int] = None
    source_page: Optional[int] = None
    original_text: Optional[str] = None
    extraction_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence_score: float = 0.0
    extraction_notes: Optional[str] = None


@dataclass
class NormalizationAudit:
    """
    Audit trail for normalization decisions

    Tracks how each line item was classified and normalized
    """
    original_fee_type: str
    original_category: str
    original_solution_name: str
    normalized_bucket: str
    normalized_category: str
    normalization_rule_applied: str
    time_normalization_applied: str
    normalization_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    manual_override: bool = False
    override_justification: Optional[str] = None
    reviewer: Optional[str] = None


@dataclass
class NormalizedLineItem:
    """
    A fully normalized line item ready for comparison

    Level 3 in the hierarchy: Line Item Detail
    """
    # Identification
    item_id: str
    solution_name: str
    vendor: str
    client: str

    # Hierarchical Classification (3 levels)
    level_1_bucket: str  # Cost Purpose (6 buckets)
    level_2_category: str  # Cost Category (15-20)
    level_3_detail: str  # Line Item Detail (original name)

    # Normalized Costs (all annualized)
    annual_cost: float
    year_1_cost: float
    total_7_year_cost: float

    # Original Values (for audit)
    original_fee_type: str
    original_monthly_fee: float
    original_one_time_fee: float
    original_per_unit_rate: float

    # Flags
    is_recurring: bool
    is_variable: bool
    is_third_party: bool
    is_optional: bool

    # Traceability
    traceability: SourceTraceability
    audit: NormalizationAudit

    # Confidence
    confidence_score: float


@dataclass
class NormalizedProposal:
    """
    A fully normalized vendor proposal

    Contains all line items organized by cost bucket for comparison
    """
    # Identification
    proposal_id: str
    vendor: str
    client: str
    proposal_date: str
    extraction_date: str

    # Contract Parameters
    contract_term_years: int
    annual_cpi_rate: float

    # Normalized Line Items
    line_items: List[NormalizedLineItem]

    # Cost Summary by Bucket
    bucket_totals: Dict[str, Dict[str, float]]

    # Cost-per-Unit Metrics
    normalized_metrics: Dict[str, float]

    # Institution Parameters (for normalization)
    institution_params: Dict[str, Any]

    # Overall Confidence
    average_confidence: float

    # Audit Metadata
    normalization_version: str = "1.0"
    normalization_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# COST NORMALIZER CLASS
# =============================================================================

class CostNormalizer:
    """
    Main class for normalizing vendor proposals to standard taxonomy

    Implements:
    - 6-bucket cost classification
    - Time normalization
    - Terminology normalization
    - Cost-per-unit calculations
    - Full traceability
    """

    def __init__(self, cpi_rate: float = 0.03, contract_years: int = 7):
        """
        Initialize normalizer with default parameters

        Args:
            cpi_rate: Annual cost increase rate (default 3%)
            contract_years: Contract term for TCO calculation (default 7)
        """
        self.cpi_rate = cpi_rate
        self.contract_years = contract_years
        self.taxonomy_version = "1.0"

        logger.info(f"CostNormalizer initialized: CPI={cpi_rate}, Term={contract_years} years")

    def normalize_proposal(
        self,
        extraction_data: dict,
        source_file: str,
        institution_params: Optional[Dict[str, Any]] = None
    ) -> NormalizedProposal:
        """
        Normalize a complete vendor proposal

        Args:
            extraction_data: Raw extraction JSON from AI extraction
            source_file: Path to source document
            institution_params: Optional institution-specific parameters
                               for cost-per-unit calculations

        Returns:
            NormalizedProposal with all costs standardized
        """
        vendor = extraction_data.get("vendor", "Unknown")
        client = extraction_data.get("client", "Unknown")

        logger.info(f"Normalizing proposal: {vendor} for {client}")

        # Set default institution params if not provided
        if institution_params is None:
            institution_params = {
                "total_accounts": 50000,
                "total_users": 500,
                "annual_transactions": 1000000,
                "total_assets_millions": 500,
            }
        institution_params["contract_months"] = self.contract_years * 12

        # Normalize each line item
        normalized_items = []
        for idx, item in enumerate(extraction_data.get("line_items", [])):
            normalized = self._normalize_line_item(
                item=item,
                item_index=idx,
                vendor=vendor,
                client=client,
                source_file=source_file
            )
            normalized_items.append(normalized)

        # Calculate bucket totals
        bucket_totals = self._calculate_bucket_totals(normalized_items)

        # Calculate cost-per-unit metrics
        total_tco = sum(
            bucket_totals.get(b.value, {}).get("total_7_year", 0)
            for b in get_bucket_display_order()
        )
        normalized_metrics = self._calculate_normalized_metrics(
            total_tco, institution_params
        )

        # Calculate average confidence
        confidences = [item.confidence_score for item in normalized_items]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Create normalized proposal
        proposal = NormalizedProposal(
            proposal_id=f"{vendor}_{client}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            vendor=vendor,
            client=client,
            proposal_date=extraction_data.get("document_date", ""),
            extraction_date=datetime.now().isoformat(),
            contract_term_years=self.contract_years,
            annual_cpi_rate=self.cpi_rate,
            line_items=normalized_items,
            bucket_totals=bucket_totals,
            normalized_metrics=normalized_metrics,
            institution_params=institution_params,
            average_confidence=avg_confidence
        )

        logger.info(f"Normalized {len(normalized_items)} line items across {len(bucket_totals)} buckets")

        return proposal

    def _normalize_line_item(
        self,
        item: dict,
        item_index: int,
        vendor: str,
        client: str,
        source_file: str
    ) -> NormalizedLineItem:
        """
        Normalize a single line item

        Applies:
        - Cost bucket classification
        - Category assignment
        - Time normalization
        - Traceability tracking
        """
        solution_name = item.get("solution_name", f"Item_{item_index}")
        original_fee_type = item.get("fee_type", "Monthly F")
        original_category = item.get("category", "Other")
        original_monthly = item.get("monthly_fee", 0.0) or 0.0
        original_one_time = item.get("one_time_fee", 0.0) or 0.0
        original_per_unit = item.get("per_unit_rate", 0.0) or 0.0
        confidence = item.get("overall_confidence", 0.8)
        notes = item.get("extraction_notes", "")

        # Step 1: Detect cost bucket (terminology normalization)
        bucket = detect_cost_bucket(
            solution_name=solution_name,
            fee_type=original_fee_type,
            notes=notes
        )

        # Step 2: Find specific category within bucket
        category_match = find_category_by_keywords(f"{solution_name} {notes}")
        if category_match and category_match[0] == bucket:
            level_2_category = category_match[1].name
        else:
            # Default category for bucket
            categories = COST_CATEGORIES.get(bucket, [])
            level_2_category = categories[0].name if categories else "Other"

        # Step 3: Time normalization - calculate annual cost
        annual_cost, time_rule = self._apply_time_normalization(
            fee_type=original_fee_type,
            monthly_fee=original_monthly,
            one_time_fee=original_one_time,
            per_unit_rate=original_per_unit
        )

        # Step 4: Calculate multi-year costs
        year_1_cost = annual_cost
        if "one-time" in original_fee_type.lower():
            total_7_year = annual_cost  # One-time only in Year 1
        else:
            # Apply CPI for recurring costs
            total_7_year = self._calculate_total_tco(annual_cost)

        # Step 5: Determine flags
        is_recurring = "one-time" not in original_fee_type.lower()
        is_variable = "v" in original_fee_type.lower() or original_per_unit > 0
        is_third_party = item.get("third_party", False)
        is_optional = item.get("optional", False)

        # Step 6: Create traceability record
        traceability = SourceTraceability(
            source_file=source_file,
            extraction_method="ai_enhanced",
            source_table_index=item.get("source_table_index"),
            source_row_index=item_index,
            original_text=solution_name,
            confidence_score=confidence,
            extraction_notes=notes
        )

        # Step 7: Create audit record
        normalization_rule = self._get_normalization_rule_description(
            solution_name, original_fee_type, bucket
        )

        audit = NormalizationAudit(
            original_fee_type=original_fee_type,
            original_category=original_category,
            original_solution_name=solution_name,
            normalized_bucket=bucket.value,
            normalized_category=level_2_category,
            normalization_rule_applied=normalization_rule,
            time_normalization_applied=time_rule
        )

        # Create normalized line item
        return NormalizedLineItem(
            item_id=f"{vendor}_{item_index:04d}",
            solution_name=solution_name,
            vendor=vendor,
            client=client,
            level_1_bucket=bucket.value,
            level_2_category=level_2_category,
            level_3_detail=solution_name,
            annual_cost=annual_cost,
            year_1_cost=year_1_cost,
            total_7_year_cost=total_7_year,
            original_fee_type=original_fee_type,
            original_monthly_fee=original_monthly,
            original_one_time_fee=original_one_time,
            original_per_unit_rate=original_per_unit,
            is_recurring=is_recurring,
            is_variable=is_variable,
            is_third_party=is_third_party,
            is_optional=is_optional,
            traceability=traceability,
            audit=audit,
            confidence_score=confidence
        )

    def _apply_time_normalization(
        self,
        fee_type: str,
        monthly_fee: float,
        one_time_fee: float,
        per_unit_rate: float
    ) -> Tuple[float, str]:
        """
        Normalize costs to annual basis

        Returns: (annual_cost, rule_description)
        """
        fee_type_lower = fee_type.lower()

        if "one-time" in fee_type_lower:
            return (one_time_fee, "One-Time (Year 1 only)")

        if "monthly" in fee_type_lower:
            annual = monthly_fee * 12
            return (annual, "Monthly x 12 = Annual")

        if "annual" in fee_type_lower:
            # Annual fees - use monthly_fee field (often stored there)
            return (monthly_fee, "Annual = Annual")

        # Default: assume monthly
        if monthly_fee > 0:
            return (monthly_fee * 12, "Monthly x 12 = Annual (default)")

        return (0.0, "No cost detected")

    def _calculate_total_tco(self, annual_cost: float) -> float:
        """Calculate total TCO over contract term with CPI"""
        if annual_cost == 0:
            return 0.0

        total = 0.0
        current_cost = annual_cost

        for year in range(self.contract_years):
            total += current_cost
            current_cost *= (1 + self.cpi_rate)

        return total

    def _get_normalization_rule_description(
        self,
        solution_name: str,
        fee_type: str,
        bucket: CostBucket
    ) -> str:
        """Generate description of which normalization rule was applied"""
        combined = f"{solution_name} {fee_type}".lower()

        for term, mapped_bucket in TERMINOLOGY_MAPPINGS.items():
            if term in combined and mapped_bucket == bucket:
                return f"Terminology match: '{term}' -> {bucket.value}"

        return f"Default classification based on fee_type: {fee_type}"

    def _calculate_bucket_totals(
        self,
        items: List[NormalizedLineItem]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate totals for each cost bucket

        Returns dict with bucket name as key, containing:
        - annual_cost: Total annual cost
        - total_7_year: Total 7-year TCO
        - required_annual: Required items only
        - optional_annual: Optional items only
        - item_count: Number of items
        """
        totals = {}

        for bucket in get_bucket_display_order():
            bucket_items = [i for i in items if i.level_1_bucket == bucket.value]

            required_items = [i for i in bucket_items if not i.is_optional]
            optional_items = [i for i in bucket_items if i.is_optional]

            totals[bucket.value] = {
                "annual_cost": sum(i.annual_cost for i in bucket_items),
                "total_7_year": sum(i.total_7_year_cost for i in bucket_items),
                "required_annual": sum(i.annual_cost for i in required_items),
                "required_7_year": sum(i.total_7_year_cost for i in required_items),
                "optional_annual": sum(i.annual_cost for i in optional_items),
                "optional_7_year": sum(i.total_7_year_cost for i in optional_items),
                "item_count": len(bucket_items),
                "required_count": len(required_items),
                "optional_count": len(optional_items),
            }

        return totals

    def _calculate_normalized_metrics(
        self,
        total_tco: float,
        institution_params: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate cost-per-unit normalization metrics

        Enables comparison across different-sized institutions
        """
        metrics = {}

        for metric in NORMALIZATION_METRICS:
            denominator = institution_params.get(metric.denominator_field, 0)
            if denominator and denominator > 0:
                metrics[metric.name] = total_tco / denominator
            else:
                metrics[metric.name] = 0.0

        return metrics

    def export_to_json(
        self,
        proposal: NormalizedProposal,
        output_path: str
    ) -> str:
        """Export normalized proposal to JSON with full audit trail"""
        def serialize(obj):
            if hasattr(obj, '__dict__'):
                return asdict(obj) if hasattr(obj, '__dataclass_fields__') else obj.__dict__
            return str(obj)

        output = {
            "metadata": {
                "normalization_version": self.taxonomy_version,
                "generated_at": datetime.now().isoformat(),
                "taxonomy_schema": export_taxonomy_schema()
            },
            "proposal": asdict(proposal),
            "comparison_ready": True
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, default=serialize)

        logger.info(f"Exported normalized proposal to: {output_path}")
        return output_path


# =============================================================================
# COMPARISON REPORT GENERATOR
# =============================================================================

class ComparisonReportGenerator:
    """
    Generates apples-to-apples comparison reports from normalized proposals
    """

    def __init__(self):
        self.report_version = "1.0"

    def generate_comparison(
        self,
        proposals: List[NormalizedProposal],
        output_path: str
    ) -> dict:
        """
        Generate side-by-side comparison of multiple vendors

        Returns comparison data structure with:
        - Bucket-by-bucket comparison
        - Cost-per-unit comparisons
        - Winner determination per category
        """
        if not proposals:
            return {"error": "No proposals to compare"}

        comparison = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "vendors_compared": [p.vendor for p in proposals],
                "comparison_version": self.report_version
            },
            "bucket_comparison": self._compare_by_bucket(proposals),
            "metric_comparison": self._compare_by_metrics(proposals),
            "total_tco_comparison": self._compare_total_tco(proposals),
            "recommendation": self._generate_recommendation(proposals)
        }

        # Save comparison
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)

        logger.info(f"Generated comparison report: {output_path}")
        return comparison

    def _compare_by_bucket(
        self,
        proposals: List[NormalizedProposal]
    ) -> Dict[str, Dict[str, Any]]:
        """Compare costs bucket-by-bucket across vendors"""
        comparison = {}

        for bucket in get_bucket_display_order():
            bucket_name = bucket.value
            vendor_costs = {}

            for proposal in proposals:
                bucket_data = proposal.bucket_totals.get(bucket_name, {})
                vendor_costs[proposal.vendor] = {
                    "annual_cost": bucket_data.get("annual_cost", 0),
                    "total_7_year": bucket_data.get("total_7_year", 0),
                    "item_count": bucket_data.get("item_count", 0)
                }

            # Determine lowest cost vendor for this bucket
            costs = [(v, d["total_7_year"]) for v, d in vendor_costs.items()]
            costs_sorted = sorted(costs, key=lambda x: x[1])
            lowest = costs_sorted[0] if costs_sorted else (None, 0)

            comparison[bucket_name] = {
                "vendors": vendor_costs,
                "lowest_cost_vendor": lowest[0],
                "lowest_cost_amount": lowest[1],
                "cost_spread": costs_sorted[-1][1] - costs_sorted[0][1] if len(costs_sorted) > 1 else 0
            }

        return comparison

    def _compare_by_metrics(
        self,
        proposals: List[NormalizedProposal]
    ) -> Dict[str, Dict[str, float]]:
        """Compare cost-per-unit metrics across vendors"""
        comparison = {}

        for metric in NORMALIZATION_METRICS:
            metric_values = {}
            for proposal in proposals:
                metric_values[proposal.vendor] = proposal.normalized_metrics.get(metric.name, 0)

            # Determine best (lowest) value
            values_sorted = sorted(metric_values.items(), key=lambda x: x[1])
            best = values_sorted[0] if values_sorted else (None, 0)

            comparison[metric.name] = {
                "vendors": metric_values,
                "best_vendor": best[0],
                "best_value": best[1],
                "formula": metric.formula,
                "use_case": metric.use_case
            }

        return comparison

    def _compare_total_tco(
        self,
        proposals: List[NormalizedProposal]
    ) -> Dict[str, Any]:
        """Compare total 7-year TCO across vendors"""
        totals = {}

        for proposal in proposals:
            total = sum(
                proposal.bucket_totals.get(b.value, {}).get("total_7_year", 0)
                for b in get_bucket_display_order()
            )
            totals[proposal.vendor] = {
                "total_7_year_tco": total,
                "average_monthly": total / (proposal.contract_term_years * 12),
                "confidence": proposal.average_confidence
            }

        # Sort by TCO
        sorted_totals = sorted(totals.items(), key=lambda x: x[1]["total_7_year_tco"])

        return {
            "vendors": totals,
            "ranking": [v[0] for v in sorted_totals],
            "lowest_tco_vendor": sorted_totals[0][0] if sorted_totals else None,
            "highest_tco_vendor": sorted_totals[-1][0] if sorted_totals else None,
            "tco_difference": (sorted_totals[-1][1]["total_7_year_tco"] -
                             sorted_totals[0][1]["total_7_year_tco"]) if len(sorted_totals) > 1 else 0
        }

    def _generate_recommendation(
        self,
        proposals: List[NormalizedProposal]
    ) -> Dict[str, Any]:
        """Generate comparison recommendation"""
        if not proposals:
            return {"recommendation": "No proposals to compare"}

        # Simple scoring: count bucket wins
        wins = {p.vendor: 0 for p in proposals}

        for bucket in get_bucket_display_order():
            bucket_costs = []
            for p in proposals:
                cost = p.bucket_totals.get(bucket.value, {}).get("total_7_year", float('inf'))
                bucket_costs.append((p.vendor, cost))

            if bucket_costs:
                winner = min(bucket_costs, key=lambda x: x[1])
                if winner[1] < float('inf'):
                    wins[winner[0]] += 1

        # Determine overall winner
        winner = max(wins.items(), key=lambda x: x[1])

        return {
            "bucket_wins": wins,
            "recommended_vendor": winner[0],
            "win_count": winner[1],
            "total_buckets": len(get_bucket_display_order()),
            "note": "Recommendation based on lowest cost per bucket. Additional factors (risk, support, innovation) should be considered."
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def normalize_extraction(
    extraction_path: str,
    output_path: str = None,
    institution_params: Dict[str, Any] = None
) -> NormalizedProposal:
    """
    Convenience function to normalize an extraction file

    Args:
        extraction_path: Path to AI extraction JSON
        output_path: Optional path for normalized output
        institution_params: Optional institution parameters

    Returns:
        NormalizedProposal object
    """
    with open(extraction_path, 'r', encoding='utf-8') as f:
        extraction_data = json.load(f)

    normalizer = CostNormalizer()
    proposal = normalizer.normalize_proposal(
        extraction_data=extraction_data,
        source_file=extraction_path,
        institution_params=institution_params
    )

    if output_path:
        normalizer.export_to_json(proposal, output_path)

    return proposal


def compare_proposals(
    extraction_paths: List[str],
    output_path: str,
    institution_params: Dict[str, Any] = None
) -> dict:
    """
    Convenience function to compare multiple vendor proposals

    Args:
        extraction_paths: List of paths to AI extraction JSONs
        output_path: Path for comparison report
        institution_params: Institution parameters for normalization

    Returns:
        Comparison report dictionary
    """
    normalizer = CostNormalizer()
    proposals = []

    for path in extraction_paths:
        with open(path, 'r', encoding='utf-8') as f:
            extraction_data = json.load(f)

        proposal = normalizer.normalize_proposal(
            extraction_data=extraction_data,
            source_file=path,
            institution_params=institution_params
        )
        proposals.append(proposal)

    generator = ComparisonReportGenerator()
    return generator.generate_comparison(proposals, output_path)
