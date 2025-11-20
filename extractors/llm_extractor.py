"""
LLM Extractor Module

Uses Claude API for intelligent field extraction from documents.
Combines LLM capabilities with regex and NER for robust extraction.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field

# Claude API
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# NLP for NER
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

from dotenv import load_dotenv

# Local imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TCO_COLUMNS
from preprocessors.text_processor import TextProcessor, TextChunk


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@dataclass
class ExtractionResult:
    """Result of LLM extraction."""
    fields: Dict[str, Any]
    confidence: float
    raw_response: str
    tokens_used: int
    extraction_method: str  # 'llm', 'regex', 'ner', 'hybrid'
    warnings: List[str] = field(default_factory=list)


@dataclass
class FieldDefinition:
    """Definition of a field to extract."""
    name: str
    description: str
    field_type: str  # 'string', 'number', 'currency', 'date', 'boolean', 'list'
    required: bool = True
    regex_pattern: Optional[str] = None
    examples: List[str] = field(default_factory=list)


class LLMExtractor:
    """
    Extract structured data from text using Claude API.

    Features:
    - Field-specific extraction prompts
    - Confidence scoring
    - Hybrid extraction (LLM + regex + NER)
    - Chunk processing for long documents
    - Error handling and retries
    """

    # Common regex patterns for extraction
    PATTERNS = {
        'currency': r'\$[\d,]+(?:\.\d{2})?',
        'percentage': r'\d+(?:\.\d+)?%',
        'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'phone': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'year': r'\b20\d{2}\b',
        'integer': r'\b\d+\b',
        'decimal': r'\b\d+\.\d+\b',
    }

    # TCO-specific field definitions
    TCO_FIELDS = [
        FieldDefinition(
            name='vendor_name',
            description='The name of the vendor (e.g., FIS, Jack Henry)',
            field_type='string',
            examples=['FIS', 'Jack Henry', 'Fiserv']
        ),
        FieldDefinition(
            name='product_name',
            description='Name of the product or solution',
            field_type='string',
            examples=['SilverLake', 'Digital Banking', 'Core Processing']
        ),
        FieldDefinition(
            name='monthly_fee',
            description='Monthly recurring fee amount',
            field_type='currency',
            regex_pattern=r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:/\s*)?(?:mo|month))?',
            examples=['$1,234.56/mo', '$500.00']
        ),
        FieldDefinition(
            name='annual_fee',
            description='Annual fee amount',
            field_type='currency',
            regex_pattern=r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:/\s*)?(?:yr|year|annual))?',
            examples=['$14,814.72/yr', '$6,000 annual']
        ),
        FieldDefinition(
            name='one_time_fee',
            description='One-time implementation or setup fee',
            field_type='currency',
            examples=['$10,000', '$5,000 implementation']
        ),
        FieldDefinition(
            name='contract_term',
            description='Length of contract in years',
            field_type='string',
            regex_pattern=r'\b(\d+)[-\s]?year',
            examples=['5-year', '7 year', '10-year term']
        ),
        FieldDefinition(
            name='annual_increase',
            description='Annual price increase percentage',
            field_type='percentage',
            regex_pattern=r'(\d+(?:\.\d+)?%)\s*(?:annual|yearly|CPI)',
            examples=['3% annual', '6% CPI']
        ),
        FieldDefinition(
            name='category',
            description='Product category (Bundle, Non-Bundle, Third-Party, etc.)',
            field_type='string',
            examples=['Bundle', 'Non-Bundle Required', 'Optional', 'Third-Party']
        ),
        FieldDefinition(
            name='fee_type',
            description='Type of fee (Monthly Fixed, Monthly Variable, Annual, One-Time)',
            field_type='string',
            examples=['Monthly F', 'Monthly V', 'Annual', 'One-Time']
        ),
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'claude-sonnet-4-20250514',
        max_tokens: int = 4096,
        temperature: float = 0.0
    ):
        """
        Initialize LLM extractor.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Model temperature (0 for deterministic)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Initialize Anthropic client
        if HAS_ANTHROPIC:
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = Anthropic(api_key=api_key)
            else:
                self.client = None
                logger.warning("No API key provided - LLM extraction disabled")
        else:
            self.client = None
            logger.warning("anthropic package not installed")

        # Initialize spaCy for NER
        if HAS_SPACY:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                self.nlp = None
                logger.warning("spaCy model not found - NER disabled")
        else:
            self.nlp = None

        # Text processor for chunking
        self.text_processor = TextProcessor()

    def extract_with_regex(self, text: str, field: FieldDefinition) -> List[str]:
        """
        Extract field values using regex patterns.

        Args:
            text: Input text
            field: Field definition with regex pattern

        Returns:
            List of matched values
        """
        pattern = field.regex_pattern or self.PATTERNS.get(field.field_type, '')
        if not pattern:
            return []

        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m if isinstance(m, str) else m[0] for m in matches]

    def extract_with_ner(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy.

        Args:
            text: Input text

        Returns:
            Dictionary of entity_type -> list of entities
        """
        if not self.nlp:
            return {}

        doc = self.nlp(text)
        entities = {}

        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)

        return entities

    def extract_with_llm(
        self,
        text: str,
        fields: List[FieldDefinition],
        context: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract fields using Claude API.

        Args:
            text: Input text to extract from
            fields: List of fields to extract
            context: Additional context for extraction

        Returns:
            ExtractionResult with extracted fields
        """
        if not self.client:
            return ExtractionResult(
                fields={},
                confidence=0.0,
                raw_response='',
                tokens_used=0,
                extraction_method='none',
                warnings=['LLM client not initialized']
            )

        # Build extraction prompt
        prompt = self._build_extraction_prompt(text, fields, context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            raw_response = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Parse JSON response
            fields_data, confidence, warnings = self._parse_llm_response(raw_response, fields)

            return ExtractionResult(
                fields=fields_data,
                confidence=confidence,
                raw_response=raw_response,
                tokens_used=tokens_used,
                extraction_method='llm',
                warnings=warnings
            )

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return ExtractionResult(
                fields={},
                confidence=0.0,
                raw_response='',
                tokens_used=0,
                extraction_method='llm',
                warnings=[f"LLM extraction error: {str(e)}"]
            )

    def _build_extraction_prompt(
        self,
        text: str,
        fields: List[FieldDefinition],
        context: Optional[str] = None
    ) -> str:
        """Build the extraction prompt for Claude."""

        field_descriptions = []
        for field in fields:
            desc = f"- {field.name} ({field.field_type}): {field.description}"
            if field.examples:
                desc += f"\n  Examples: {', '.join(field.examples)}"
            if not field.required:
                desc += " [OPTIONAL]"
            field_descriptions.append(desc)

        prompt = f"""Extract the following fields from the document text below. Return ONLY a valid JSON object with the extracted values.

FIELDS TO EXTRACT:
{chr(10).join(field_descriptions)}

INSTRUCTIONS:
1. Extract exact values from the text - do not infer or calculate
2. For currency values, include the dollar sign and cents (e.g., "$1,234.56")
3. For missing required fields, use null
4. For fields with multiple values, return as an array
5. Include a "confidence" field (0.0 to 1.0) indicating extraction confidence
6. Include a "notes" field with any ambiguities or warnings

{f"ADDITIONAL CONTEXT: {context}" if context else ""}

DOCUMENT TEXT:
{text}

Respond with ONLY the JSON object, no additional text."""

        return prompt

    def _parse_llm_response(
        self,
        response: str,
        fields: List[FieldDefinition]
    ) -> tuple[Dict[str, Any], float, List[str]]:
        """Parse the JSON response from Claude."""

        warnings = []

        # Try to extract JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            # Extract confidence
            confidence = data.pop('confidence', 0.8)
            if isinstance(confidence, str):
                confidence = float(confidence)

            # Extract notes as warnings
            notes = data.pop('notes', '')
            if notes:
                warnings.append(notes)

            # Validate required fields
            for field in fields:
                if field.required and field.name not in data:
                    warnings.append(f"Required field '{field.name}' not extracted")
                elif field.name in data:
                    # Type validation
                    value = data[field.name]
                    if value is not None:
                        data[field.name] = self._convert_type(value, field.field_type)

            return data, confidence, warnings

        except json.JSONDecodeError as e:
            warnings.append(f"Failed to parse JSON response: {e}")
            return {}, 0.0, warnings

    def _convert_type(self, value: Any, field_type: str) -> Any:
        """Convert value to expected type."""
        if value is None:
            return None

        if field_type == 'currency':
            if isinstance(value, str):
                # Remove non-numeric except decimal and negative
                numeric = re.sub(r'[^\d.-]', '', value.replace(',', ''))
                try:
                    return float(numeric)
                except ValueError:
                    return value
            return value

        elif field_type == 'number':
            if isinstance(value, str):
                try:
                    return float(value.replace(',', ''))
                except ValueError:
                    return value
            return value

        elif field_type == 'boolean':
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1', 'y')
            return bool(value)

        return value

    def extract_tco_fields(self, text: str, vendor: Optional[str] = None) -> ExtractionResult:
        """
        Extract TCO-specific fields from text.

        Args:
            text: Document text
            vendor: Optional vendor name for context

        Returns:
            ExtractionResult with TCO fields
        """
        context = f"This is a {vendor} vendor proposal for TCO analysis." if vendor else None
        return self.extract_with_llm(text, self.TCO_FIELDS, context)

    def extract_hybrid(
        self,
        text: str,
        fields: List[FieldDefinition],
        prefer_llm: bool = True
    ) -> ExtractionResult:
        """
        Hybrid extraction combining LLM, regex, and NER.

        Args:
            text: Input text
            fields: Fields to extract
            prefer_llm: Whether to prefer LLM results over regex

        Returns:
            Combined ExtractionResult
        """
        results = {}
        warnings = []
        methods_used = set()

        # First pass: Regex extraction
        for field in fields:
            regex_matches = self.extract_with_regex(text, field)
            if regex_matches:
                results[field.name] = regex_matches[0] if len(regex_matches) == 1 else regex_matches
                methods_used.add('regex')

        # Second pass: NER extraction
        if self.nlp:
            entities = self.extract_with_ner(text)
            # Map NER entities to fields
            ner_mapping = {
                'MONEY': ['monthly_fee', 'annual_fee', 'one_time_fee'],
                'ORG': ['vendor_name'],
                'DATE': ['contract_term'],
                'PERCENT': ['annual_increase']
            }
            for ent_type, field_names in ner_mapping.items():
                if ent_type in entities:
                    for field_name in field_names:
                        if field_name not in results:
                            results[field_name] = entities[ent_type][0]
                            methods_used.add('ner')

        # Third pass: LLM extraction (for missing or all if preferred)
        if self.client:
            if prefer_llm:
                llm_result = self.extract_with_llm(text, fields)
                # Merge LLM results
                for key, value in llm_result.fields.items():
                    if value is not None and (key not in results or prefer_llm):
                        results[key] = value
                methods_used.add('llm')
                warnings.extend(llm_result.warnings)
            else:
                # Only use LLM for missing fields
                missing_fields = [f for f in fields if f.name not in results]
                if missing_fields:
                    llm_result = self.extract_with_llm(text, missing_fields)
                    results.update(llm_result.fields)
                    methods_used.add('llm')
                    warnings.extend(llm_result.warnings)

        # Calculate confidence based on coverage
        extracted_count = sum(1 for f in fields if f.name in results and results[f.name])
        confidence = extracted_count / len(fields) if fields else 0.0

        return ExtractionResult(
            fields=results,
            confidence=confidence,
            raw_response='',
            tokens_used=0,
            extraction_method='hybrid' if len(methods_used) > 1 else list(methods_used)[0] if methods_used else 'none',
            warnings=warnings
        )

    def extract_from_chunks(
        self,
        chunks: List[TextChunk],
        fields: List[FieldDefinition]
    ) -> ExtractionResult:
        """
        Extract from multiple text chunks and merge results.

        Args:
            chunks: List of text chunks
            fields: Fields to extract

        Returns:
            Merged ExtractionResult
        """
        all_results = {}
        all_warnings = []
        total_tokens = 0

        for chunk in chunks:
            result = self.extract_hybrid(chunk.text, fields)
            total_tokens += result.tokens_used
            all_warnings.extend(result.warnings)

            # Merge results (later chunks can override)
            for key, value in result.fields.items():
                if value is not None:
                    if key in all_results and isinstance(all_results[key], list):
                        if isinstance(value, list):
                            all_results[key].extend(value)
                        else:
                            all_results[key].append(value)
                    else:
                        all_results[key] = value

        # Calculate overall confidence
        extracted_count = sum(1 for f in fields if f.name in all_results and all_results[f.name])
        confidence = extracted_count / len(fields) if fields else 0.0

        return ExtractionResult(
            fields=all_results,
            confidence=confidence,
            raw_response='',
            tokens_used=total_tokens,
            extraction_method='hybrid',
            warnings=all_warnings
        )


def extract_fields(text: str, fields: Optional[List[FieldDefinition]] = None) -> ExtractionResult:
    """
    Convenience function to extract fields from text.

    Args:
        text: Input text
        fields: Fields to extract (default: TCO fields)

    Returns:
        ExtractionResult
    """
    extractor = LLMExtractor()
    fields = fields or extractor.TCO_FIELDS
    return extractor.extract_hybrid(text, fields)


def extract_tco_data(text: str, vendor: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to extract TCO data.

    Args:
        text: Document text
        vendor: Vendor name

    Returns:
        Dictionary of extracted fields
    """
    extractor = LLMExtractor()
    result = extractor.extract_tco_fields(text, vendor)
    return result.fields


if __name__ == '__main__':
    # Example usage
    sample_text = """
    FIS Proposal for Echelon Bank

    Core Processing Bundle - 5-Year Term
    Monthly Fee: $8,500.00/mo
    Annual Increase: 3% CPI

    Digital Banking Solution
    Monthly Fee: $2,100.00
    One-Time Implementation: $15,000

    Total Monthly: $10,600.00
    Contract Start: 01/15/2025
    """

    extractor = LLMExtractor()

    # Regex extraction
    for field in extractor.TCO_FIELDS:
        matches = extractor.extract_with_regex(sample_text, field)
        if matches:
            print(f"{field.name}: {matches}")

    print("\n--- Hybrid Extraction ---")
    result = extractor.extract_hybrid(sample_text, extractor.TCO_FIELDS)
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Method: {result.extraction_method}")
    for key, value in result.fields.items():
        print(f"  {key}: {value}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
