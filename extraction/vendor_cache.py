"""
Vendor Cache Module

Caches vendor-specific context for faster extraction and cost optimization.
Supports:
- Vendor profiles (terminology, document patterns)
- Extraction templates from successful extractions
- Correction history for learning
- Anthropic prompt caching optimization
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

from ..config import CACHE_CONFIG, CACHE_COMPONENTS

logger = logging.getLogger(__name__)


@dataclass
class VendorProfile:
    """Cached vendor profile data."""
    vendor_name: str
    document_types: List[str] = field(default_factory=list)
    product_lines: List[str] = field(default_factory=list)
    terminology_map: Dict[str, str] = field(default_factory=dict)
    document_patterns: Dict[str, Any] = field(default_factory=dict)
    extraction_templates: List[Dict] = field(default_factory=list)
    correction_history: List[Dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    extraction_count: int = 0
    success_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'VendorProfile':
        return cls(**data)


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""
    key: str
    data: Dict[str, Any]
    confidence: float
    created_at: str
    expires_at: str
    access_count: int = 0
    last_accessed: str = ""

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        return cls(**data)


class VendorCache:
    """
    Vendor context caching system.

    Caches vendor-specific information to:
    1. Speed up extraction for known vendors
    2. Reduce API costs via prompt caching
    3. Learn from corrections over time
    4. Maintain consistent terminology mapping
    """

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize the vendor cache.

        Args:
            cache_dir: Directory for cache files (default from config)
            config: Cache configuration override
        """
        self.config = config or CACHE_CONFIG
        self.components = CACHE_COMPONENTS

        # Set up cache directory
        cache_path = cache_dir or self.config.get('cache_directory', 'vendor_cache')
        self.cache_dir = Path(cache_path)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cache settings
        self.enabled = self.config.get('enabled', True)
        self.expiry_days = self.config.get('cache_expiry_days', 90)
        self.min_confidence = self.config.get('min_confidence_to_cache', 0.70)
        self.max_entries = self.config.get('max_cache_entries_per_vendor', 100)

        # In-memory cache for current session
        self._memory_cache: Dict[str, VendorProfile] = {}

        logger.info(f"VendorCache initialized at: {self.cache_dir}")

    def get_vendor_context(self, vendor_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached context for a vendor.

        Args:
            vendor_name: Name of the vendor

        Returns:
            Vendor context dict or None if not cached
        """
        if not self.enabled:
            return None

        # Check memory cache first
        normalized_name = self._normalize_vendor_name(vendor_name)
        if normalized_name in self._memory_cache:
            profile = self._memory_cache[normalized_name]
            logger.debug(f"Cache hit (memory): {vendor_name}")
            return profile.to_dict()

        # Check file cache
        profile = self._load_vendor_profile(normalized_name)
        if profile:
            self._memory_cache[normalized_name] = profile
            logger.info(f"Cache hit (file): {vendor_name}")
            return profile.to_dict()

        logger.debug(f"Cache miss: {vendor_name}")
        return None

    def cache_vendor_context(
        self,
        vendor_name: str,
        context: Dict[str, Any],
        confidence: float = 1.0
    ) -> bool:
        """
        Cache vendor context from extraction.

        Args:
            vendor_name: Vendor name
            context: Context data to cache
            confidence: Extraction confidence (must meet threshold)

        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False

        if confidence < self.min_confidence:
            logger.debug(f"Confidence {confidence:.1%} below threshold, not caching")
            return False

        normalized_name = self._normalize_vendor_name(vendor_name)

        # Get or create profile
        profile = self._memory_cache.get(normalized_name)
        if not profile:
            profile = self._load_vendor_profile(normalized_name)
        if not profile:
            profile = VendorProfile(
                vendor_name=vendor_name,
                created_at=datetime.now().isoformat()
            )

        # Update profile with new context
        if self.components.get('terminology_map', True):
            new_terms = context.get('terminology_map', {})
            profile.terminology_map.update(new_terms)

        if self.components.get('document_patterns', True):
            new_patterns = context.get('tables_with_pricing', [])
            if new_patterns:
                profile.document_patterns['pricing_tables'] = new_patterns

        if self.components.get('vendor_profile', True):
            if context.get('document_type'):
                if context['document_type'] not in profile.document_types:
                    profile.document_types.append(context['document_type'])

        profile.updated_at = datetime.now().isoformat()
        profile.extraction_count += 1

        # Save to memory and file
        self._memory_cache[normalized_name] = profile
        self._save_vendor_profile(normalized_name, profile)

        logger.info(f"Cached context for vendor: {vendor_name}")
        return True

    def cache_extraction_template(
        self,
        vendor_name: str,
        template: Dict[str, Any],
        confidence: float
    ) -> bool:
        """
        Cache a successful extraction template for learning.

        Args:
            vendor_name: Vendor name
            template: Extraction template (document structure + results)
            confidence: Extraction confidence

        Returns:
            True if cached
        """
        if not self.enabled or not self.components.get('extraction_templates', True):
            return False

        if confidence < self.min_confidence:
            return False

        normalized_name = self._normalize_vendor_name(vendor_name)
        profile = self._get_or_create_profile(normalized_name, vendor_name)

        # Add template (limit to max entries)
        template_entry = {
            'template': template,
            'confidence': confidence,
            'created_at': datetime.now().isoformat()
        }

        profile.extraction_templates.append(template_entry)
        if len(profile.extraction_templates) > self.max_entries:
            # Remove oldest, lowest confidence entries
            profile.extraction_templates.sort(
                key=lambda x: (x.get('confidence', 0), x.get('created_at', '')),
                reverse=True
            )
            profile.extraction_templates = profile.extraction_templates[:self.max_entries]

        self._memory_cache[normalized_name] = profile
        self._save_vendor_profile(normalized_name, profile)

        return True

    def record_correction(
        self,
        vendor_name: str,
        original: Dict[str, Any],
        corrected: Dict[str, Any],
        field_name: str
    ) -> None:
        """
        Record a manual correction for learning.

        Args:
            vendor_name: Vendor name
            original: Original extracted value
            corrected: Corrected value
            field_name: Name of the corrected field
        """
        if not self.enabled or not self.components.get('correction_history', True):
            return

        normalized_name = self._normalize_vendor_name(vendor_name)
        profile = self._get_or_create_profile(normalized_name, vendor_name)

        correction = {
            'field': field_name,
            'original': original,
            'corrected': corrected,
            'timestamp': datetime.now().isoformat()
        }

        profile.correction_history.append(correction)

        # Limit correction history
        if len(profile.correction_history) > self.max_entries * 2:
            profile.correction_history = profile.correction_history[-self.max_entries:]

        self._memory_cache[normalized_name] = profile
        self._save_vendor_profile(normalized_name, profile)

        logger.info(f"Recorded correction for {vendor_name}: {field_name}")

    def get_terminology_map(self, vendor_name: str) -> Dict[str, str]:
        """Get terminology mapping for a vendor."""
        context = self.get_vendor_context(vendor_name)
        return context.get('terminology_map', {}) if context else {}

    def get_extraction_templates(
        self,
        vendor_name: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get best extraction templates for a vendor."""
        normalized_name = self._normalize_vendor_name(vendor_name)
        profile = self._memory_cache.get(normalized_name)
        if not profile:
            profile = self._load_vendor_profile(normalized_name)
        if not profile:
            return []

        # Return highest confidence templates
        templates = sorted(
            profile.extraction_templates,
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )
        return templates[:limit]

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Count cached vendors
        cached_files = list(self.cache_dir.glob('*.json'))
        vendors_cached = len(cached_files)

        # Calculate total entries
        total_entries = 0
        total_corrections = 0
        for name in self._memory_cache:
            profile = self._memory_cache[name]
            total_entries += len(profile.extraction_templates)
            total_corrections += len(profile.correction_history)

        return {
            'enabled': self.enabled,
            'cache_directory': str(self.cache_dir),
            'vendors_cached': vendors_cached,
            'vendors_in_memory': len(self._memory_cache),
            'total_extraction_templates': total_entries,
            'total_corrections': total_corrections,
            'expiry_days': self.expiry_days,
            'min_confidence_threshold': self.min_confidence
        }

    def clear_cache(self, vendor_name: Optional[str] = None) -> int:
        """
        Clear cache entries.

        Args:
            vendor_name: Specific vendor to clear, or None for all

        Returns:
            Number of entries cleared
        """
        cleared = 0

        if vendor_name:
            normalized = self._normalize_vendor_name(vendor_name)
            if normalized in self._memory_cache:
                del self._memory_cache[normalized]
                cleared += 1
            cache_file = self.cache_dir / f"{normalized}.json"
            if cache_file.exists():
                cache_file.unlink()
                cleared += 1
        else:
            cleared = len(self._memory_cache)
            self._memory_cache.clear()
            for f in self.cache_dir.glob('*.json'):
                f.unlink()
                cleared += 1

        logger.info(f"Cleared {cleared} cache entries")
        return cleared

    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        removed = 0
        cutoff = datetime.now() - timedelta(days=self.expiry_days)

        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)

                updated = data.get('updated_at', data.get('created_at', ''))
                if updated:
                    updated_dt = datetime.fromisoformat(updated)
                    if updated_dt < cutoff:
                        cache_file.unlink()
                        removed += 1
                        # Also remove from memory
                        name = cache_file.stem
                        if name in self._memory_cache:
                            del self._memory_cache[name]

            except Exception as e:
                logger.warning(f"Error checking cache file {cache_file}: {e}")

        logger.info(f"Cleaned up {removed} expired cache entries")
        return removed

    def _normalize_vendor_name(self, name: str) -> str:
        """Normalize vendor name for consistent cache keys."""
        # Remove special characters, lowercase, replace spaces
        normalized = name.lower().strip()
        normalized = ''.join(c if c.isalnum() else '_' for c in normalized)
        return normalized

    def _get_or_create_profile(
        self,
        normalized_name: str,
        display_name: str
    ) -> VendorProfile:
        """Get existing profile or create new one."""
        if normalized_name in self._memory_cache:
            return self._memory_cache[normalized_name]

        profile = self._load_vendor_profile(normalized_name)
        if profile:
            return profile

        return VendorProfile(
            vendor_name=display_name,
            created_at=datetime.now().isoformat()
        )

    def _load_vendor_profile(self, normalized_name: str) -> Optional[VendorProfile]:
        """Load vendor profile from file cache."""
        cache_file = self.cache_dir / f"{normalized_name}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return VendorProfile.from_dict(data)
        except Exception as e:
            logger.warning(f"Error loading cache file {cache_file}: {e}")
            return None

    def _save_vendor_profile(
        self,
        normalized_name: str,
        profile: VendorProfile
    ) -> None:
        """Save vendor profile to file cache."""
        cache_file = self.cache_dir / f"{normalized_name}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache file {cache_file}: {e}")

    def get_prompt_cache_prefix(self, vendor_name: str) -> Optional[str]:
        """
        Generate a consistent prefix for Anthropic prompt caching.

        This allows repeated extractions for the same vendor to
        benefit from Anthropic's prompt caching feature.

        Args:
            vendor_name: Vendor name

        Returns:
            Cache prefix string or None
        """
        context = self.get_vendor_context(vendor_name)
        if not context:
            return None

        # Create consistent prefix from vendor context
        cache_key_data = {
            'vendor': vendor_name,
            'terminology': sorted(context.get('terminology_map', {}).items()),
            'doc_types': sorted(context.get('document_types', []))
        }

        # Generate hash for cache key
        key_str = json.dumps(cache_key_data, sort_keys=True)
        cache_hash = hashlib.md5(key_str.encode()).hexdigest()[:16]

        return f"vendor_context_{cache_hash}"
