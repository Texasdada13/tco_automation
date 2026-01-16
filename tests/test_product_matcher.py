"""
Tests for ProductMatcher class.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from core.product_matcher import (
    MatchMethod,
    MatchResult,
    ProductMatcher,
    print_match_summary,
)


@pytest.fixture
def sample_ontology():
    """Create a sample ontology for testing."""
    return {
        "metadata": {
            "version": "1.0",
            "last_updated": "2026-01-15",
            "supported_vendors": ["FIS", "JACK_HENRY", "CSI"]
        },
        "categories": {
            "core_banking_platform": {
                "canonical_name": "Core Banking Platform",
                "description": "Primary core banking system",
                "vendor_terms": {
                    "FIS": ["HORIZON", "Core: HORIZON", "IBS"],
                    "JACK_HENRY": ["SilverLake", "Core: SilverLake"],
                    "CSI": ["NuPoint", "NuPoint Core"]
                }
            },
            "digital_banking_platform": {
                "canonical_name": "Digital Banking Platform",
                "description": "Online and mobile banking",
                "vendor_terms": {
                    "FIS": ["D1 Flex", "Digital: D1 Flex, D1 Business, Mobile, Bill Pay"],
                    "JACK_HENRY": ["Banno", "Banno Digital"]
                }
            },
            "eft_debit_processing": {
                "canonical_name": "EFT/Debit Processing",
                "description": "EFT and debit card processing",
                "vendor_terms": {
                    "FIS": ["EFT Norcross", "EFT: EFT Norcross, 3D Secure, Tokenization, SecurLOCK"]
                }
            }
        }
    }


@pytest.fixture
def temp_ontology_file(sample_ontology, tmp_path):
    """Create a temporary ontology file."""
    ontology_path = tmp_path / "product_ontology.yaml"
    with open(ontology_path, 'w') as f:
        yaml.dump(sample_ontology, f)
    return ontology_path


@pytest.fixture
def matcher(temp_ontology_file, tmp_path):
    """Create a ProductMatcher with test ontology."""
    auto_approval_path = tmp_path / "auto_approved_matches.json"
    return ProductMatcher(
        ontology_path=str(temp_ontology_file),
        auto_approval_log_path=str(auto_approval_path),
        enable_fuzzy=True,
        enable_ai=False
    )


class TestProductMatcherInit:
    """Tests for ProductMatcher initialization."""

    def test_load_ontology(self, matcher):
        """Test that ontology loads correctly."""
        assert len(matcher.categories) == 3
        assert "core_banking_platform" in matcher.categories
        assert "digital_banking_platform" in matcher.categories

    def test_load_nonexistent_ontology(self, tmp_path):
        """Test error handling for missing ontology file."""
        with pytest.raises(FileNotFoundError):
            ProductMatcher(ontology_path=str(tmp_path / "nonexistent.yaml"))

    def test_metadata_loaded(self, matcher):
        """Test that metadata is loaded."""
        assert matcher.metadata["version"] == "1.0"


class TestExactMatching:
    """Tests for exact matching functionality."""

    def test_exact_match_simple(self, matcher):
        """Test simple exact match."""
        result = matcher.match("HORIZON", "FIS")
        assert result.match_method == MatchMethod.EXACT
        assert result.canonical_category == "core_banking_platform"
        assert result.canonical_name == "Core Banking Platform"
        assert result.confidence == 100.0
        assert result.needs_review is False

    def test_exact_match_with_prefix(self, matcher):
        """Test exact match with vendor prefix."""
        result = matcher.match("Core: HORIZON", "FIS")
        assert result.match_method == MatchMethod.EXACT
        assert result.canonical_category == "core_banking_platform"

    def test_exact_match_case_insensitive(self, matcher):
        """Test that matching is case-insensitive."""
        result = matcher.match("horizon", "FIS")
        assert result.match_method == MatchMethod.EXACT
        assert result.canonical_category == "core_banking_platform"

    def test_exact_match_different_vendor(self, matcher):
        """Test exact match for different vendor."""
        result = matcher.match("SilverLake", "JACK_HENRY")
        assert result.match_method == MatchMethod.EXACT
        assert result.canonical_category == "core_banking_platform"

    def test_exact_match_long_product_name(self, matcher):
        """Test exact match with long product name."""
        result = matcher.match("Digital: D1 Flex, D1 Business, Mobile, Bill Pay", "FIS")
        assert result.match_method == MatchMethod.EXACT
        assert result.canonical_category == "digital_banking_platform"

    def test_no_match_wrong_vendor(self, matcher):
        """Test that wrong vendor doesn't match."""
        result = matcher.match("HORIZON", "JACK_HENRY")
        assert result.match_method != MatchMethod.EXACT
        # HORIZON is FIS product, shouldn't match for Jack Henry

    def test_no_match_unknown_product(self, matcher):
        """Test unknown product doesn't match."""
        result = matcher.match("Unknown Product XYZ", "FIS")
        assert result.canonical_category is None


class TestFuzzyMatching:
    """Tests for fuzzy matching functionality."""

    def test_fuzzy_match_typo(self, matcher):
        """Test fuzzy match catches typos."""
        result = matcher.match("HORIZION", "FIS")  # Typo in HORIZON
        assert result.match_method == MatchMethod.FUZZY
        assert result.canonical_category == "core_banking_platform"
        assert result.confidence >= 85

    def test_fuzzy_match_missing_space(self, matcher):
        """Test fuzzy match handles missing spaces."""
        result = matcher.match("D1Flex", "FIS")  # Missing space
        assert result.match_method == MatchMethod.FUZZY
        assert result.canonical_category == "digital_banking_platform"

    def test_fuzzy_match_extra_whitespace(self, matcher):
        """Test fuzzy match handles extra whitespace."""
        result = matcher.match("Core:  HORIZON", "FIS")  # Extra space
        assert result.match_method == MatchMethod.FUZZY
        assert result.canonical_category == "core_banking_platform"

    def test_fuzzy_below_threshold_unmatched(self, matcher):
        """Test that low similarity scores don't match."""
        result = matcher.match("Completely Different Name", "FIS")
        assert result.match_method == MatchMethod.UNMATCHED


class TestVendorNormalization:
    """Tests for vendor name normalization."""

    def test_normalize_jh(self, matcher):
        """Test JH normalizes to JACK_HENRY."""
        result = matcher.match("SilverLake", "JH")
        assert result.match_method == MatchMethod.EXACT

    def test_normalize_jackhenry(self, matcher):
        """Test JACKHENRY normalizes to JACK_HENRY."""
        result = matcher.match("SilverLake", "JACKHENRY")
        assert result.match_method == MatchMethod.EXACT

    def test_normalize_lowercase(self, matcher):
        """Test lowercase vendor names work."""
        result = matcher.match("HORIZON", "fis")
        assert result.match_method == MatchMethod.EXACT


class TestBatchMatching:
    """Tests for batch matching functionality."""

    def test_batch_match(self, matcher):
        """Test matching a batch of items."""
        items = [
            {"solution_name": "HORIZON", "vendor": "FIS"},
            {"solution_name": "SilverLake", "vendor": "JACK_HENRY"},
            {"solution_name": "Unknown Product", "vendor": "FIS"}
        ]
        results = matcher.match_batch(items)

        assert len(results) == 3
        assert results[0].match_method == MatchMethod.EXACT
        assert results[1].match_method == MatchMethod.EXACT
        assert results[2].match_method == MatchMethod.UNMATCHED

    def test_batch_match_vendor_extraction(self, matcher):
        """Test that vendor is extracted from compound names."""
        items = [
            {"solution_name": "HORIZON", "vendor": "ECHELON_BANK_FIS"}
        ]
        results = matcher.match_batch(items)

        assert results[0].match_method == MatchMethod.EXACT
        assert results[0].vendor == "FIS"


class TestAutoApprovalLogging:
    """Tests for auto-approval logging."""

    def test_auto_approval_creates_log(self, matcher, tmp_path):
        """Test that auto-approved matches are logged."""
        # Make an exact match (100% confidence = auto-approved)
        matcher.match("HORIZON", "FIS")

        # Check log file was created
        log_path = tmp_path / "auto_approved_matches.json"
        assert log_path.exists()

        with open(log_path) as f:
            data = json.load(f)

        assert len(data["auto_approved"]) >= 1
        entry = data["auto_approved"][0]
        assert entry["vendor"] == "FIS"
        assert entry["original_name"] == "HORIZON"
        assert entry["confidence"] == 100.0

    def test_low_confidence_not_auto_approved(self, matcher, tmp_path):
        """Test that low confidence matches are not auto-approved."""
        # Start fresh - remove any existing log
        log_path = tmp_path / "auto_approved_matches.json"
        if log_path.exists():
            os.remove(log_path)

        # Make a fuzzy match that should need review
        result = matcher.match("HORIZIONNN", "FIS")  # More typos = lower confidence

        # If confidence is below threshold, should need review
        if result.confidence < 95:
            assert result.needs_review is True


class TestStatistics:
    """Tests for match statistics."""

    def test_get_match_statistics(self, matcher):
        """Test statistics calculation."""
        items = [
            {"solution_name": "HORIZON", "vendor": "FIS"},
            {"solution_name": "SilverLake", "vendor": "JACK_HENRY"},
            {"solution_name": "Unknown", "vendor": "FIS"}
        ]
        results = matcher.match_batch(items)
        stats = matcher.get_match_statistics(results)

        assert stats["total"] == 3
        assert stats["exact_matches"] == 2
        assert stats["unmatched"] == 1
        assert stats["match_rate"] == pytest.approx(66.67, rel=0.1)

    def test_empty_statistics(self, matcher):
        """Test statistics with empty results."""
        stats = matcher.get_match_statistics([])
        assert stats["total"] == 0
        assert stats["match_rate"] == 0.0


class TestOntologyManagement:
    """Tests for ontology management functions."""

    def test_add_term_to_ontology(self, matcher):
        """Test adding a new term to the ontology."""
        success = matcher.add_term_to_ontology(
            category_key="core_banking_platform",
            vendor="FIS",
            new_term="New HORIZON Module",
            save=False
        )
        assert success is True

        # Verify term is now matchable
        result = matcher.match("New HORIZON Module", "FIS")
        assert result.match_method == MatchMethod.EXACT

    def test_add_term_invalid_category(self, matcher):
        """Test adding term to non-existent category fails."""
        success = matcher.add_term_to_ontology(
            category_key="nonexistent_category",
            vendor="FIS",
            new_term="Some Term",
            save=False
        )
        assert success is False

    def test_get_category_info(self, matcher):
        """Test retrieving category information."""
        info = matcher.get_category_info("core_banking_platform")
        assert info is not None
        assert info["canonical_name"] == "Core Banking Platform"

    def test_get_all_categories(self, matcher):
        """Test getting all category keys."""
        categories = matcher.get_all_categories()
        assert "core_banking_platform" in categories
        assert "digital_banking_platform" in categories
        assert len(categories) == 3

    def test_get_vendor_terms(self, matcher):
        """Test getting vendor-specific terms."""
        terms = matcher.get_vendor_terms("core_banking_platform", "FIS")
        assert "HORIZON" in terms
        assert "Core: HORIZON" in terms


class TestMatchResult:
    """Tests for MatchResult dataclass."""

    def test_match_result_defaults(self):
        """Test MatchResult default values."""
        result = MatchResult(original_name="Test", vendor="FIS")
        assert result.canonical_category is None
        assert result.match_method == MatchMethod.UNMATCHED
        assert result.confidence == 0.0
        assert result.needs_review is False


class TestPrintSummary:
    """Tests for print_match_summary function."""

    def test_print_summary_runs(self, matcher, capsys):
        """Test that print_match_summary runs without error."""
        items = [
            {"solution_name": "HORIZON", "vendor": "FIS"},
            {"solution_name": "Unknown", "vendor": "FIS"}
        ]
        results = matcher.match_batch(items)
        print_match_summary(results, matcher)

        captured = capsys.readouterr()
        assert "PRODUCT MATCHING SUMMARY" in captured.out
        assert "Total products:" in captured.out


class TestAISuggestion:
    """Tests for AI suggestion functionality."""

    def test_ai_disabled_by_default_without_api_key(self, temp_ontology_file):
        """Test that AI is gracefully disabled when no API key is available."""
        # Create matcher without API key and with AI enabled
        # It should still work, just without AI suggestions
        matcher = ProductMatcher(
            ontology_path=str(temp_ontology_file),
            enable_ai=True
        )
        # Even if enable_ai=True, it will be False if anthropic isn't available or no API key
        # The matcher should still work for exact/fuzzy matching
        result = matcher.match("HORIZON", "FIS")
        assert result.match_method == MatchMethod.EXACT
        assert result.canonical_category == "core_banking_platform"

    def test_ai_explicitly_disabled(self, temp_ontology_file):
        """Test matcher works normally with AI explicitly disabled."""
        matcher = ProductMatcher(
            ontology_path=str(temp_ontology_file),
            enable_ai=False
        )
        assert matcher.enable_ai is False

        # Should still match known products
        result = matcher.match("HORIZON", "FIS")
        assert result.match_method == MatchMethod.EXACT

        # Unknown products should be marked as unmatched (no AI suggestion)
        result = matcher.match("Completely Unknown Product XYZ", "FIS")
        assert result.match_method == MatchMethod.UNMATCHED
        assert result.needs_review is True

    def test_statistics_include_ai_suggestions(self, matcher):
        """Test that statistics dict includes AI suggestion fields."""
        results = [
            MatchResult(original_name="Test1", vendor="FIS", match_method=MatchMethod.EXACT, confidence=100),
            MatchResult(original_name="Test2", vendor="FIS", match_method=MatchMethod.FUZZY, confidence=90),
            MatchResult(original_name="Test3", vendor="FIS", match_method=MatchMethod.AI_SUGGESTION, confidence=75, needs_review=True),
            MatchResult(original_name="Test4", vendor="FIS", match_method=MatchMethod.UNMATCHED, confidence=0, needs_review=True),
        ]

        stats = matcher.get_match_statistics(results)

        assert stats["total"] == 4
        assert stats["exact_matches"] == 1
        assert stats["fuzzy_matches"] == 1
        assert stats["ai_suggestions"] == 1
        assert stats["unmatched"] == 1
        assert stats["match_rate"] == 75.0  # 3/4 = 75%
        assert "ai_rate" in stats
