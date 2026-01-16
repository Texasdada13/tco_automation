"""
Product Matcher - Maps vendor-specific product names to canonical categories.

This module provides the core matching functionality for the product ontology system:
1. Exact matching against known vendor terms
2. Fuzzy matching for typos and variations
3. AI-assisted suggestions for unknown products (optional)
4. Auto-approval logging for high-confidence matches
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


class MatchMethod(Enum):
    """How a product match was determined."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    AI_SUGGESTION = "ai_suggestion"
    HUMAN_APPROVED = "human_approved"
    UNMATCHED = "unmatched"


@dataclass
class MatchResult:
    """Result of attempting to match a product."""
    original_name: str
    vendor: str
    canonical_category: Optional[str] = None
    canonical_name: Optional[str] = None
    match_method: MatchMethod = MatchMethod.UNMATCHED
    confidence: float = 0.0
    matched_term: Optional[str] = None
    needs_review: bool = False
    ai_suggestion: Optional[str] = None
    ai_reasoning: Optional[str] = None


@dataclass
class AutoApprovalEntry:
    """Entry in the auto-approval log."""
    timestamp: str
    vendor: str
    original_name: str
    canonical_category: str
    canonical_name: str
    match_method: str
    confidence: float
    matched_term: str


class ProductMatcher:
    """
    Maps vendor-specific product names to canonical categories.

    Usage:
        matcher = ProductMatcher()
        result = matcher.match("Core: HORIZON", "FIS")
        print(result.canonical_category)  # "core_banking_platform"
    """

    # Thresholds
    FUZZY_THRESHOLD = 85  # Minimum fuzzy match score (0-100)
    AUTO_APPROVE_THRESHOLD = 95  # Auto-approve if confidence >= this

    def __init__(
        self,
        ontology_path: Optional[str] = None,
        auto_approval_log_path: Optional[str] = None,
        enable_fuzzy: bool = True,
        enable_ai: bool = True
    ):
        """
        Initialize the ProductMatcher.

        Args:
            ontology_path: Path to product_ontology.yaml. Defaults to ontology/product_ontology.yaml
            auto_approval_log_path: Path to auto_approved_matches.json. Defaults to ontology/auto_approved_matches.json
            enable_fuzzy: Whether to use fuzzy matching for unmatched products
            enable_ai: Whether to use AI suggestions (placeholder for Phase 3)
        """
        self.enable_fuzzy = enable_fuzzy and RAPIDFUZZ_AVAILABLE
        self.enable_ai = enable_ai

        # Determine paths
        if ontology_path is None:
            base_dir = Path(__file__).parent.parent
            ontology_path = base_dir / "ontology" / "product_ontology.yaml"
        self.ontology_path = Path(ontology_path)

        if auto_approval_log_path is None:
            self.auto_approval_log_path = self.ontology_path.parent / "auto_approved_matches.json"
        else:
            self.auto_approval_log_path = Path(auto_approval_log_path)

        # Load ontology
        self.categories = {}
        self._vendor_term_index = {}  # vendor -> {term_lower: (category_key, original_term)}
        self._all_terms_by_vendor = {}  # vendor -> [list of all terms for fuzzy matching]
        self._load_ontology()

    def _load_ontology(self) -> None:
        """Load and index the product ontology from YAML."""
        if not self.ontology_path.exists():
            raise FileNotFoundError(f"Ontology file not found: {self.ontology_path}")

        with open(self.ontology_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self.categories = data.get('categories', {})
        self.metadata = data.get('metadata', {})

        # Build lookup indices
        self._vendor_term_index = {}
        self._all_terms_by_vendor = {}

        for category_key, category_data in self.categories.items():
            vendor_terms = category_data.get('vendor_terms', {})

            for vendor, terms in vendor_terms.items():
                if vendor not in self._vendor_term_index:
                    self._vendor_term_index[vendor] = {}
                    self._all_terms_by_vendor[vendor] = []

                for term in terms:
                    term_lower = term.lower().strip()
                    self._vendor_term_index[vendor][term_lower] = (category_key, term)
                    self._all_terms_by_vendor[vendor].append(term)

    def reload_ontology(self) -> None:
        """Reload the ontology from disk (useful after updates)."""
        self._load_ontology()

    def match(self, product_name: str, vendor: str) -> MatchResult:
        """
        Match a product name to a canonical category.

        Args:
            product_name: The vendor-specific product name (e.g., "Core: HORIZON")
            vendor: The vendor code (e.g., "FIS", "JACK_HENRY", "CSI")

        Returns:
            MatchResult with match details
        """
        # Normalize vendor name
        vendor = self._normalize_vendor(vendor)
        product_name_clean = product_name.strip()

        # Step 1: Try exact match with provided vendor
        result = self._exact_match(product_name_clean, vendor)
        if result.match_method == MatchMethod.EXACT:
            self._maybe_log_auto_approval(result)
            return result

        # Step 1b: If vendor is unknown/generic, try all known vendors
        known_vendors = ["FIS", "JACK_HENRY", "CSI", "FISERV", "FINASTRA"]
        if vendor not in known_vendors:
            for try_vendor in known_vendors:
                result = self._exact_match(product_name_clean, try_vendor)
                if result.match_method == MatchMethod.EXACT:
                    # Found match - update vendor to the correct one
                    result.vendor = try_vendor
                    self._maybe_log_auto_approval(result)
                    return result

        # Step 2: Try fuzzy match with provided vendor
        if self.enable_fuzzy:
            result = self._fuzzy_match(product_name_clean, vendor)
            if result.match_method == MatchMethod.FUZZY:
                if result.confidence >= self.AUTO_APPROVE_THRESHOLD:
                    self._maybe_log_auto_approval(result)
                else:
                    result.needs_review = True
                return result

            # Step 2b: If vendor is unknown, try fuzzy match across all vendors
            if vendor not in known_vendors:
                best_result = None
                best_confidence = 0
                for try_vendor in known_vendors:
                    result = self._fuzzy_match(product_name_clean, try_vendor)
                    if result.match_method == MatchMethod.FUZZY and result.confidence > best_confidence:
                        best_confidence = result.confidence
                        best_result = result
                        best_result.vendor = try_vendor

                if best_result:
                    if best_result.confidence >= self.AUTO_APPROVE_THRESHOLD:
                        self._maybe_log_auto_approval(best_result)
                    else:
                        best_result.needs_review = True
                    return best_result

        # Step 3: AI suggestion (placeholder - will be implemented in Phase 3)
        # For now, just mark as needing review
        result = MatchResult(
            original_name=product_name_clean,
            vendor=vendor,
            match_method=MatchMethod.UNMATCHED,
            confidence=0.0,
            needs_review=True
        )

        return result

    def _normalize_vendor(self, vendor: str) -> str:
        """Normalize vendor name to standard format."""
        vendor_upper = vendor.upper().strip()

        # Handle common variations
        vendor_map = {
            "JH": "JACK_HENRY",
            "JACKHENRY": "JACK_HENRY",
            "JACK HENRY": "JACK_HENRY",
            "FIS": "FIS",
            "CSI": "CSI",
            "FISERV": "FISERV",
            "FINASTRA": "FINASTRA",
        }

        return vendor_map.get(vendor_upper, vendor_upper)

    def _exact_match(self, product_name: str, vendor: str) -> MatchResult:
        """Try to find an exact match in the ontology."""
        product_lower = product_name.lower().strip()

        vendor_terms = self._vendor_term_index.get(vendor, {})

        if product_lower in vendor_terms:
            category_key, matched_term = vendor_terms[product_lower]
            category_data = self.categories[category_key]

            return MatchResult(
                original_name=product_name,
                vendor=vendor,
                canonical_category=category_key,
                canonical_name=category_data.get('canonical_name', category_key),
                match_method=MatchMethod.EXACT,
                confidence=100.0,
                matched_term=matched_term,
                needs_review=False
            )

        return MatchResult(
            original_name=product_name,
            vendor=vendor,
            match_method=MatchMethod.UNMATCHED,
            confidence=0.0
        )

    def _fuzzy_match(self, product_name: str, vendor: str) -> MatchResult:
        """Try to find a fuzzy match in the ontology."""
        if not RAPIDFUZZ_AVAILABLE:
            return MatchResult(
                original_name=product_name,
                vendor=vendor,
                match_method=MatchMethod.UNMATCHED,
                confidence=0.0
            )

        vendor_terms = self._all_terms_by_vendor.get(vendor, [])

        if not vendor_terms:
            return MatchResult(
                original_name=product_name,
                vendor=vendor,
                match_method=MatchMethod.UNMATCHED,
                confidence=0.0
            )

        # Find best fuzzy match
        best_match = process.extractOne(
            product_name,
            vendor_terms,
            scorer=fuzz.token_sort_ratio
        )

        if best_match and best_match[1] >= self.FUZZY_THRESHOLD:
            matched_term = best_match[0]
            confidence = best_match[1]

            # Look up the category for this term
            term_lower = matched_term.lower().strip()
            category_key, _ = self._vendor_term_index[vendor][term_lower]
            category_data = self.categories[category_key]

            return MatchResult(
                original_name=product_name,
                vendor=vendor,
                canonical_category=category_key,
                canonical_name=category_data.get('canonical_name', category_key),
                match_method=MatchMethod.FUZZY,
                confidence=confidence,
                matched_term=matched_term,
                needs_review=(confidence < self.AUTO_APPROVE_THRESHOLD)
            )

        return MatchResult(
            original_name=product_name,
            vendor=vendor,
            match_method=MatchMethod.UNMATCHED,
            confidence=0.0,
            needs_review=True
        )

    def _maybe_log_auto_approval(self, result: MatchResult) -> None:
        """Log auto-approved matches for audit trail."""
        if result.confidence < self.AUTO_APPROVE_THRESHOLD:
            return

        if result.match_method == MatchMethod.EXACT:
            # Exact matches are always auto-approved, confidence is 100
            pass
        elif result.match_method != MatchMethod.FUZZY:
            # Only log exact and high-confidence fuzzy matches
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "vendor": result.vendor,
            "original_name": result.original_name,
            "canonical_category": result.canonical_category,
            "canonical_name": result.canonical_name,
            "match_method": result.match_method.value,
            "confidence": result.confidence,
            "matched_term": result.matched_term
        }

        # Load existing log
        log_data = {"auto_approved": []}
        if self.auto_approval_log_path.exists():
            try:
                with open(self.auto_approval_log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Append entry
        log_data["auto_approved"].append(entry)

        # Save
        with open(self.auto_approval_log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)

    def _extract_vendor_from_string(self, vendor_string: str) -> str:
        """
        Extract vendor code from compound strings like 'ECHELON_BANK_FIS'.

        Args:
            vendor_string: Raw vendor string that may contain client name

        Returns:
            Normalized vendor code (FIS, JACK_HENRY, CSI, etc.)
        """
        vendor_upper = vendor_string.upper().strip()

        # Direct vendor names
        if vendor_upper in ["FIS", "CSI", "FISERV", "FINASTRA"]:
            return vendor_upper
        if vendor_upper in ["JACK_HENRY", "JH", "JACKHENRY"]:
            return "JACK_HENRY"

        # Check for vendor names anywhere in the string
        # Order matters - check more specific patterns first
        if "FIS" in vendor_upper and "FISERV" not in vendor_upper:
            return "FIS"
        if "FISERV" in vendor_upper:
            return "FISERV"
        if "CSI" in vendor_upper:
            return "CSI"
        if "JACK" in vendor_upper or "JH" in vendor_upper:
            return "JACK_HENRY"
        if "FINASTRA" in vendor_upper:
            return "FINASTRA"

        # Return original if no match
        return vendor_upper

    def match_batch(self, items: list[dict], vendor_field: str = "vendor") -> list[MatchResult]:
        """
        Match a batch of line items.

        Args:
            items: List of dicts with 'solution_name' and vendor field
            vendor_field: Name of the field containing vendor info

        Returns:
            List of MatchResult objects
        """
        results = []
        for item in items:
            product_name = item.get("solution_name", "")
            vendor_raw = item.get(vendor_field, "")

            # Extract vendor from compound strings
            vendor = self._extract_vendor_from_string(vendor_raw)

            result = self.match(product_name, vendor)
            results.append(result)

        return results

    def get_category_info(self, category_key: str) -> Optional[dict]:
        """Get full information about a category."""
        return self.categories.get(category_key)

    def get_all_categories(self) -> list[str]:
        """Get list of all canonical category keys."""
        return list(self.categories.keys())

    def get_vendor_terms(self, category_key: str, vendor: str) -> list[str]:
        """Get all known terms for a vendor in a category."""
        category = self.categories.get(category_key, {})
        vendor_terms = category.get('vendor_terms', {})
        return vendor_terms.get(vendor, [])

    def add_term_to_ontology(
        self,
        category_key: str,
        vendor: str,
        new_term: str,
        save: bool = True
    ) -> bool:
        """
        Add a new term to the ontology.

        Args:
            category_key: The canonical category to add the term to
            vendor: The vendor this term belongs to
            new_term: The new product name to add
            save: Whether to save to disk immediately

        Returns:
            True if added successfully, False if category doesn't exist
        """
        if category_key not in self.categories:
            return False

        vendor = self._normalize_vendor(vendor)

        # Update in-memory structures
        if 'vendor_terms' not in self.categories[category_key]:
            self.categories[category_key]['vendor_terms'] = {}

        if vendor not in self.categories[category_key]['vendor_terms']:
            self.categories[category_key]['vendor_terms'][vendor] = []

        if new_term not in self.categories[category_key]['vendor_terms'][vendor]:
            self.categories[category_key]['vendor_terms'][vendor].append(new_term)

        # Update indices
        if vendor not in self._vendor_term_index:
            self._vendor_term_index[vendor] = {}
            self._all_terms_by_vendor[vendor] = []

        term_lower = new_term.lower().strip()
        self._vendor_term_index[vendor][term_lower] = (category_key, new_term)
        if new_term not in self._all_terms_by_vendor[vendor]:
            self._all_terms_by_vendor[vendor].append(new_term)

        if save:
            self._save_ontology()

        return True

    def _save_ontology(self) -> None:
        """Save the current ontology to disk."""
        data = {
            'metadata': self.metadata,
            'categories': self.categories
        }

        # Update metadata
        data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        with open(self.ontology_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def get_match_statistics(self, results: list[MatchResult]) -> dict:
        """
        Get statistics about a batch of match results.

        Args:
            results: List of MatchResult objects

        Returns:
            Dict with match statistics
        """
        total = len(results)
        if total == 0:
            return {
                "total": 0,
                "exact_matches": 0,
                "fuzzy_matches": 0,
                "unmatched": 0,
                "needs_review": 0,
                "auto_approved": 0,
                "match_rate": 0.0
            }

        exact = sum(1 for r in results if r.match_method == MatchMethod.EXACT)
        fuzzy = sum(1 for r in results if r.match_method == MatchMethod.FUZZY)
        unmatched = sum(1 for r in results if r.match_method == MatchMethod.UNMATCHED)
        needs_review = sum(1 for r in results if r.needs_review)
        auto_approved = sum(1 for r in results if r.confidence >= self.AUTO_APPROVE_THRESHOLD and not r.needs_review)

        return {
            "total": total,
            "exact_matches": exact,
            "fuzzy_matches": fuzzy,
            "unmatched": unmatched,
            "needs_review": needs_review,
            "auto_approved": auto_approved,
            "match_rate": ((exact + fuzzy) / total) * 100,
            "exact_rate": (exact / total) * 100,
            "fuzzy_rate": (fuzzy / total) * 100
        }


def print_match_summary(results: list[MatchResult], matcher: ProductMatcher) -> None:
    """Print a summary of match results to console."""
    stats = matcher.get_match_statistics(results)

    print("\n" + "=" * 60)
    print("PRODUCT MATCHING SUMMARY")
    print("=" * 60)
    print(f"Total products:     {stats['total']}")
    print(f"Exact matches:      {stats['exact_matches']} ({stats['exact_rate']:.1f}%)")
    print(f"Fuzzy matches:      {stats['fuzzy_matches']} ({stats['fuzzy_rate']:.1f}%)")
    print(f"Unmatched:          {stats['unmatched']}")
    print(f"Overall match rate: {stats['match_rate']:.1f}%")
    print("-" * 60)
    print(f"Auto-approved:      {stats['auto_approved']}")
    print(f"Needs review:       {stats['needs_review']}")
    print("=" * 60)

    # Show items needing review
    review_items = [r for r in results if r.needs_review]
    if review_items:
        print("\nITEMS NEEDING REVIEW:")
        for r in review_items[:10]:  # Show first 10
            print(f"  - [{r.vendor}] {r.original_name}")
            if r.match_method == MatchMethod.FUZZY:
                print(f"    Suggested: {r.canonical_name} (confidence: {r.confidence:.0f}%)")
        if len(review_items) > 10:
            print(f"  ... and {len(review_items) - 10} more")
