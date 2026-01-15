"""
Core module for TCO Automation.

Contains:
- OutputManager: Standardized output folder structure
- VendorConfig: Configuration-driven vendor support
- StatusTracker: Pipeline status tracking and reporting
- QAReportGenerator: Quality assurance report generation
- CostTaxonomy: Universal 6-bucket cost classification
- CostNormalizer: Apples-to-apples cost normalization
"""

from .output_manager import OutputManager, ExtractionPaths, get_output_manager, create_output_paths
from .vendor_config import VendorConfigManager, VendorConfig, get_vendor_manager
from .status_tracker import StatusTracker, ExtractionStatus, get_status_tracker, print_pipeline_status
from .qa_report_generator import QAReportGenerator, QAMetrics, generate_qa_reports

# Cost Taxonomy and Normalization (Apples-to-Apples Comparison)
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
from .cost_normalizer import (
    CostNormalizer,
    NormalizedLineItem,
    NormalizedProposal,
    SourceTraceability,
    NormalizationAudit,
    ComparisonReportGenerator,
    normalize_extraction,
    compare_proposals
)

# Excel Integration for Normalized Data
from .normalized_excel_sheet import (
    add_normalized_sheet,
    create_comparison_workbook,
    NormalizedSheetConfig
)

__all__ = [
    # Output Management
    'OutputManager',
    'ExtractionPaths',
    'get_output_manager',
    'create_output_paths',
    # Vendor Configuration
    'VendorConfigManager',
    'VendorConfig',
    'get_vendor_manager',
    # Status Tracking
    'StatusTracker',
    'ExtractionStatus',
    'get_status_tracker',
    'print_pipeline_status',
    # QA Reporting
    'QAReportGenerator',
    'QAMetrics',
    'generate_qa_reports',
    # Cost Taxonomy (6-Bucket Classification)
    'CostBucket',
    'CostCategory',
    'COST_CATEGORIES',
    'TERMINOLOGY_MAPPINGS',
    'TIME_NORMALIZATIONS',
    'NORMALIZATION_METRICS',
    'detect_cost_bucket',
    'find_category_by_keywords',
    'get_bucket_display_order',
    'export_taxonomy_schema',
    # Cost Normalization (Apples-to-Apples)
    'CostNormalizer',
    'NormalizedLineItem',
    'NormalizedProposal',
    'SourceTraceability',
    'NormalizationAudit',
    'ComparisonReportGenerator',
    'normalize_extraction',
    'compare_proposals',
    # Excel Integration
    'add_normalized_sheet',
    'create_comparison_workbook',
    'NormalizedSheetConfig',
]
