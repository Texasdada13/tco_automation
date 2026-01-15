"""
Universal Cost Breakdown Structure (CBS) for Apples-to-Apples Vendor Comparison

This module defines the standardized 6-bucket cost taxonomy and hierarchical
category structure for normalizing vendor proposals across different terminologies.

Based on industry best practices from:
- Gartner TCO Framework
- ISO 20400 Sustainable Procurement
- HOCH Solutions vendor evaluation criteria
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


class CostBucket(Enum):
    """
    Level 1: Universal Cost Purpose Buckets (6 standardized buckets)

    These buckets ensure apples-to-apples comparison across vendors
    regardless of how each vendor labels their costs.
    """
    SETUP_IMPLEMENTATION = "Setup/Implementation"
    LICENSING_SUBSCRIPTION = "Licensing/Subscription"
    TRANSACTION_USAGE = "Transaction/Usage"
    TRAINING_ENABLEMENT = "Training/Enablement"
    SUPPORT_MAINTENANCE = "Support/Maintenance"
    PROFESSIONAL_SERVICES = "Professional Services"


@dataclass
class CostCategory:
    """
    Level 2: Cost Category within a bucket

    Each bucket contains multiple categories for finer granularity.
    """
    name: str
    bucket: CostBucket
    description: str
    keywords: List[str] = field(default_factory=list)


# =============================================================================
# HIERARCHICAL CATEGORY STRUCTURE (3-Level)
# =============================================================================
# Level 1: Cost Bucket (6 buckets)
# Level 2: Cost Category (defined below)
# Level 3: Line Item Detail (unlimited, from extraction)
# =============================================================================

COST_CATEGORIES: Dict[CostBucket, List[CostCategory]] = {

    CostBucket.SETUP_IMPLEMENTATION: [
        CostCategory(
            name="Project Management",
            bucket=CostBucket.SETUP_IMPLEMENTATION,
            description="Project oversight, coordination, and management",
            keywords=["project management", "pm", "project coordination", "program management"]
        ),
        CostCategory(
            name="Data Migration",
            bucket=CostBucket.SETUP_IMPLEMENTATION,
            description="Historical data transfer and conversion",
            keywords=["data migration", "data conversion", "data transfer", "migration", "conversion"]
        ),
        CostCategory(
            name="System Configuration",
            bucket=CostBucket.SETUP_IMPLEMENTATION,
            description="Initial system setup and configuration",
            keywords=["configuration", "setup", "deployment", "installation", "activation"]
        ),
        CostCategory(
            name="Implementation Services",
            bucket=CostBucket.SETUP_IMPLEMENTATION,
            description="Core implementation and onboarding",
            keywords=["implementation", "onboarding", "go-live", "launch"]
        ),
        CostCategory(
            name="Implementation Credits",
            bucket=CostBucket.SETUP_IMPLEMENTATION,
            description="Credits or discounts on implementation",
            keywords=["credit", "discount", "signing bonus", "incentive", "waiver"]
        ),
    ],

    CostBucket.LICENSING_SUBSCRIPTION: [
        CostCategory(
            name="Core Platform",
            bucket=CostBucket.LICENSING_SUBSCRIPTION,
            description="Base platform or core system licensing",
            keywords=["core", "platform", "base", "horizon", "nupoint", "silverlake", "fusion"]
        ),
        CostCategory(
            name="Module Licensing",
            bucket=CostBucket.LICENSING_SUBSCRIPTION,
            description="Add-on module or feature licensing",
            keywords=["module", "add-on", "feature", "component"]
        ),
        CostCategory(
            name="User/Seat Licensing",
            bucket=CostBucket.LICENSING_SUBSCRIPTION,
            description="Per-user or per-seat license fees",
            keywords=["per user", "per seat", "user license", "seat", "named user"]
        ),
        CostCategory(
            name="Subscription Fees",
            bucket=CostBucket.LICENSING_SUBSCRIPTION,
            description="Recurring subscription or platform fees",
            keywords=["subscription", "mrc", "monthly recurring", "platform fee"]
        ),
    ],

    CostBucket.TRANSACTION_USAGE: [
        CostCategory(
            name="Per-Transaction Fees",
            bucket=CostBucket.TRANSACTION_USAGE,
            description="Fees charged per transaction processed",
            keywords=["per transaction", "per item", "transaction fee", "per call"]
        ),
        CostCategory(
            name="Volume-Based Fees",
            bucket=CostBucket.TRANSACTION_USAGE,
            description="Fees based on processing volume",
            keywords=["volume", "usage", "consumption", "throughput"]
        ),
        CostCategory(
            name="API/Integration Calls",
            bucket=CostBucket.TRANSACTION_USAGE,
            description="Fees for API calls or integration usage",
            keywords=["api", "api call", "integration", "web service"]
        ),
        CostCategory(
            name="Overage Fees",
            bucket=CostBucket.TRANSACTION_USAGE,
            description="Fees for exceeding volume tiers",
            keywords=["overage", "excess", "additional", "tier"]
        ),
    ],

    CostBucket.TRAINING_ENABLEMENT: [
        CostCategory(
            name="Initial Training",
            bucket=CostBucket.TRAINING_ENABLEMENT,
            description="Upfront training during implementation",
            keywords=["initial training", "implementation training", "go-live training"]
        ),
        CostCategory(
            name="User Training",
            bucket=CostBucket.TRAINING_ENABLEMENT,
            description="End-user training programs",
            keywords=["user training", "end user", "staff training", "employee training"]
        ),
        CostCategory(
            name="Administrator Training",
            bucket=CostBucket.TRAINING_ENABLEMENT,
            description="System administrator training",
            keywords=["admin training", "administrator", "system admin", "technical training"]
        ),
        CostCategory(
            name="Certification Programs",
            bucket=CostBucket.TRAINING_ENABLEMENT,
            description="Professional certification and credentials",
            keywords=["certification", "certified", "credential", "accreditation"]
        ),
        CostCategory(
            name="Training Materials",
            bucket=CostBucket.TRAINING_ENABLEMENT,
            description="Documentation and training resources",
            keywords=["materials", "documentation", "manuals", "guides", "resources"]
        ),
    ],

    CostBucket.SUPPORT_MAINTENANCE: [
        CostCategory(
            name="Standard Support",
            bucket=CostBucket.SUPPORT_MAINTENANCE,
            description="Basic technical support included",
            keywords=["standard support", "basic support", "help desk", "technical support"]
        ),
        CostCategory(
            name="Premium Support",
            bucket=CostBucket.SUPPORT_MAINTENANCE,
            description="Enhanced support with better SLA",
            keywords=["premium support", "priority support", "24/7", "dedicated support"]
        ),
        CostCategory(
            name="Annual Maintenance",
            bucket=CostBucket.SUPPORT_MAINTENANCE,
            description="Annual maintenance fees (AMF)",
            keywords=["annual maintenance", "amf", "maintenance fee", "yearly maintenance"]
        ),
        CostCategory(
            name="Software Updates",
            bucket=CostBucket.SUPPORT_MAINTENANCE,
            description="Software updates and patches",
            keywords=["updates", "patches", "upgrades", "releases", "versions"]
        ),
        CostCategory(
            name="SLA Fees",
            bucket=CostBucket.SUPPORT_MAINTENANCE,
            description="Service level agreement fees",
            keywords=["sla", "service level", "uptime", "availability"]
        ),
    ],

    CostBucket.PROFESSIONAL_SERVICES: [
        CostCategory(
            name="Consulting Services",
            bucket=CostBucket.PROFESSIONAL_SERVICES,
            description="Advisory and consulting work",
            keywords=["consulting", "advisory", "consultant", "expert services"]
        ),
        CostCategory(
            name="Custom Development",
            bucket=CostBucket.PROFESSIONAL_SERVICES,
            description="Custom software development",
            keywords=["custom development", "customization", "custom code", "bespoke"]
        ),
        CostCategory(
            name="Integration Services",
            bucket=CostBucket.PROFESSIONAL_SERVICES,
            description="Third-party system integration",
            keywords=["integration", "interface", "connector", "middleware"]
        ),
        CostCategory(
            name="Report Development",
            bucket=CostBucket.PROFESSIONAL_SERVICES,
            description="Custom report and analytics development",
            keywords=["reports", "reporting", "analytics", "dashboards", "bi"]
        ),
        CostCategory(
            name="PS Hours",
            bucket=CostBucket.PROFESSIONAL_SERVICES,
            description="Professional services hourly work",
            keywords=["ps hours", "professional services", "hourly", "time and materials"]
        ),
    ],
}


# =============================================================================
# TERMINOLOGY NORMALIZATION RULES
# =============================================================================
# Maps vendor-specific terminology to standard cost buckets
# =============================================================================

TERMINOLOGY_MAPPINGS: Dict[str, CostBucket] = {
    # Setup/Implementation terms
    "implementation": CostBucket.SETUP_IMPLEMENTATION,
    "onboarding": CostBucket.SETUP_IMPLEMENTATION,
    "deployment": CostBucket.SETUP_IMPLEMENTATION,
    "activation": CostBucket.SETUP_IMPLEMENTATION,
    "conversion": CostBucket.SETUP_IMPLEMENTATION,
    "configuration": CostBucket.SETUP_IMPLEMENTATION,
    "setup": CostBucket.SETUP_IMPLEMENTATION,
    "install": CostBucket.SETUP_IMPLEMENTATION,
    "installation": CostBucket.SETUP_IMPLEMENTATION,
    "go-live": CostBucket.SETUP_IMPLEMENTATION,
    "migration": CostBucket.SETUP_IMPLEMENTATION,
    "deconversion": CostBucket.SETUP_IMPLEMENTATION,
    "project management": CostBucket.SETUP_IMPLEMENTATION,

    # Licensing/Subscription terms
    "license": CostBucket.LICENSING_SUBSCRIPTION,
    "licensing": CostBucket.LICENSING_SUBSCRIPTION,
    "subscription": CostBucket.LICENSING_SUBSCRIPTION,
    "platform fee": CostBucket.LICENSING_SUBSCRIPTION,
    "base fee": CostBucket.LICENSING_SUBSCRIPTION,
    "seat fee": CostBucket.LICENSING_SUBSCRIPTION,
    "per-user": CostBucket.LICENSING_SUBSCRIPTION,
    "per user": CostBucket.LICENSING_SUBSCRIPTION,
    "mrc": CostBucket.LICENSING_SUBSCRIPTION,
    "monthly recurring": CostBucket.LICENSING_SUBSCRIPTION,
    "core": CostBucket.LICENSING_SUBSCRIPTION,
    "platform": CostBucket.LICENSING_SUBSCRIPTION,

    # Transaction/Usage terms
    "per-transaction": CostBucket.TRANSACTION_USAGE,
    "per transaction": CostBucket.TRANSACTION_USAGE,
    "per-item": CostBucket.TRANSACTION_USAGE,
    "per item": CostBucket.TRANSACTION_USAGE,
    "per-call": CostBucket.TRANSACTION_USAGE,
    "per call": CostBucket.TRANSACTION_USAGE,
    "per-api": CostBucket.TRANSACTION_USAGE,
    "usage-based": CostBucket.TRANSACTION_USAGE,
    "usage based": CostBucket.TRANSACTION_USAGE,
    "consumption": CostBucket.TRANSACTION_USAGE,
    "volume": CostBucket.TRANSACTION_USAGE,
    "variable": CostBucket.TRANSACTION_USAGE,

    # Training/Enablement terms
    "training": CostBucket.TRAINING_ENABLEMENT,
    "certification": CostBucket.TRAINING_ENABLEMENT,
    "workshop": CostBucket.TRAINING_ENABLEMENT,
    "education": CostBucket.TRAINING_ENABLEMENT,
    "learning": CostBucket.TRAINING_ENABLEMENT,
    "enablement": CostBucket.TRAINING_ENABLEMENT,

    # Support/Maintenance terms
    "support": CostBucket.SUPPORT_MAINTENANCE,
    "maintenance": CostBucket.SUPPORT_MAINTENANCE,
    "sla": CostBucket.SUPPORT_MAINTENANCE,
    "help desk": CostBucket.SUPPORT_MAINTENANCE,
    "helpdesk": CostBucket.SUPPORT_MAINTENANCE,
    "premium support": CostBucket.SUPPORT_MAINTENANCE,
    "amf": CostBucket.SUPPORT_MAINTENANCE,
    "annual maintenance": CostBucket.SUPPORT_MAINTENANCE,

    # Professional Services terms
    "consulting": CostBucket.PROFESSIONAL_SERVICES,
    "customization": CostBucket.PROFESSIONAL_SERVICES,
    "custom development": CostBucket.PROFESSIONAL_SERVICES,
    "custom dev": CostBucket.PROFESSIONAL_SERVICES,
    "ps hours": CostBucket.PROFESSIONAL_SERVICES,
    "professional services": CostBucket.PROFESSIONAL_SERVICES,
    "integration services": CostBucket.PROFESSIONAL_SERVICES,
}


# =============================================================================
# TIME NORMALIZATION RULES
# =============================================================================
# Standardizes all costs to annual basis for comparison
# =============================================================================

@dataclass
class TimeNormalization:
    """Rules for normalizing costs to annual basis"""
    source_period: str
    multiplier: float
    description: str


TIME_NORMALIZATIONS: Dict[str, TimeNormalization] = {
    "monthly": TimeNormalization("monthly", 12.0, "Monthly x 12 = Annual"),
    "monthly f": TimeNormalization("monthly", 12.0, "Fixed Monthly x 12 = Annual"),
    "monthly v": TimeNormalization("monthly", 12.0, "Variable Monthly x 12 = Annual"),
    "quarterly": TimeNormalization("quarterly", 4.0, "Quarterly x 4 = Annual"),
    "semi-annual": TimeNormalization("semi-annual", 2.0, "Semi-Annual x 2 = Annual"),
    "annual": TimeNormalization("annual", 1.0, "Annual = Annual"),
    "one-time": TimeNormalization("one-time", 1.0, "One-Time (Year 1 only)"),
    "per-seat": TimeNormalization("per-seat", 1.0, "Per-Seat x User Count = Annual"),
}


# =============================================================================
# COST-PER-UNIT NORMALIZATION METRICS
# =============================================================================
# For apples-to-apples comparison across different institution sizes
# =============================================================================

@dataclass
class NormalizationMetric:
    """Metric for cost-per-unit normalization"""
    name: str
    formula: str
    use_case: str
    denominator_field: str


NORMALIZATION_METRICS: List[NormalizationMetric] = [
    NormalizationMetric(
        name="Cost per Account",
        formula="Total TCO / Number of Accounts",
        use_case="Retail banking comparison",
        denominator_field="total_accounts"
    ),
    NormalizationMetric(
        name="Cost per User",
        formula="Total TCO / Number of Users",
        use_case="User-licensed software comparison",
        denominator_field="total_users"
    ),
    NormalizationMetric(
        name="Cost per Transaction",
        formula="Total TCO / Annual Transaction Volume",
        use_case="High-volume processing comparison",
        denominator_field="annual_transactions"
    ),
    NormalizationMetric(
        name="Cost per Month",
        formula="Total TCO / Contract Months",
        use_case="Cash flow analysis",
        denominator_field="contract_months"
    ),
    NormalizationMetric(
        name="Cost per Asset",
        formula="Total TCO / Total Assets (in millions)",
        use_case="Institution size comparison",
        denominator_field="total_assets_millions"
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_categories() -> List[CostCategory]:
    """Get flat list of all cost categories"""
    categories = []
    for bucket_categories in COST_CATEGORIES.values():
        categories.extend(bucket_categories)
    return categories


def get_categories_for_bucket(bucket: CostBucket) -> List[CostCategory]:
    """Get categories for a specific cost bucket"""
    return COST_CATEGORIES.get(bucket, [])


def find_category_by_keywords(text: str) -> Optional[Tuple[CostBucket, CostCategory]]:
    """
    Find matching bucket and category based on keywords in text

    Returns tuple of (CostBucket, CostCategory) or None if no match
    """
    text_lower = text.lower()

    for bucket, categories in COST_CATEGORIES.items():
        for category in categories:
            for keyword in category.keywords:
                if keyword.lower() in text_lower:
                    return (bucket, category)

    return None


def detect_cost_bucket(solution_name: str, fee_type: str = None,
                       notes: str = None) -> CostBucket:
    """
    Detect the appropriate cost bucket for a line item

    Uses multiple signals: solution name, fee type, and extraction notes
    """
    # Combine all text for analysis
    combined_text = f"{solution_name or ''} {fee_type or ''} {notes or ''}".lower()

    # Check terminology mappings first (most specific)
    for term, bucket in TERMINOLOGY_MAPPINGS.items():
        if term.lower() in combined_text:
            return bucket

    # Check category keywords
    result = find_category_by_keywords(combined_text)
    if result:
        return result[0]

    # Default based on fee type
    if fee_type:
        fee_type_lower = fee_type.lower()
        if "one-time" in fee_type_lower:
            return CostBucket.SETUP_IMPLEMENTATION
        elif "monthly v" in fee_type_lower or "variable" in fee_type_lower:
            return CostBucket.TRANSACTION_USAGE
        elif "monthly" in fee_type_lower or "annual" in fee_type_lower:
            return CostBucket.LICENSING_SUBSCRIPTION

    # Ultimate fallback
    return CostBucket.LICENSING_SUBSCRIPTION


def get_bucket_display_order() -> List[CostBucket]:
    """Get buckets in standard display order for reports"""
    return [
        CostBucket.SETUP_IMPLEMENTATION,
        CostBucket.LICENSING_SUBSCRIPTION,
        CostBucket.TRANSACTION_USAGE,
        CostBucket.TRAINING_ENABLEMENT,
        CostBucket.SUPPORT_MAINTENANCE,
        CostBucket.PROFESSIONAL_SERVICES,
    ]


# =============================================================================
# SCHEMA EXPORT FOR DOCUMENTATION
# =============================================================================

def export_taxonomy_schema() -> dict:
    """Export full taxonomy as dictionary for documentation/JSON"""
    return {
        "version": "1.0",
        "description": "Universal Cost Breakdown Structure for Vendor Comparison",
        "buckets": [
            {
                "id": bucket.name,
                "display_name": bucket.value,
                "categories": [
                    {
                        "name": cat.name,
                        "description": cat.description,
                        "keywords": cat.keywords
                    }
                    for cat in categories
                ]
            }
            for bucket, categories in COST_CATEGORIES.items()
        ],
        "terminology_mappings": {
            term: bucket.value for term, bucket in TERMINOLOGY_MAPPINGS.items()
        },
        "time_normalizations": {
            key: {
                "multiplier": tn.multiplier,
                "description": tn.description
            }
            for key, tn in TIME_NORMALIZATIONS.items()
        },
        "normalization_metrics": [
            {
                "name": m.name,
                "formula": m.formula,
                "use_case": m.use_case
            }
            for m in NORMALIZATION_METRICS
        ]
    }
