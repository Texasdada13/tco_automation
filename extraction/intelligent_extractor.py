"""
Intelligent Extractor Module

AI-powered document extraction using Anthropic Claude API.
Implements the 4-stage extraction pipeline:
1. Context Analysis - Understand document structure
2. Line Item Extraction - Extract all pricing with confidence scores
3. Calculation Engine - Compute multi-year projections
4. QA Validation - Validate extraction accuracy
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..config import (
    AI_CONFIG,
    CONTRACT_DEFAULTS,
    CONFIDENCE_THRESHOLDS,
    get_prompt
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Container for extraction results with confidence tracking."""
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    calculations: Dict[str, Any] = field(default_factory=dict)
    qa_results: Dict[str, Any] = field(default_factory=dict)
    overall_confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class LineItem:
    """Represents a single extracted line item."""
    solution_name: str
    fee_type: str  # "Monthly F", "Monthly V", "Annual", "One-Time"
    category: str  # "Bundle", "Non-Bundle Required", etc.
    per_unit_rate: float = 0.0
    monthly_fee: float = 0.0
    annual_fee: float = 0.0
    one_time_fee: float = 0.0
    optional: bool = False
    third_party: bool = False
    field_confidence: Dict[str, float] = field(default_factory=dict)
    overall_confidence: float = 0.0
    source_location: str = ""
    source_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class IntelligentExtractor:
    """
    AI-powered document extractor using Anthropic Claude API.

    Implements vendor-agnostic extraction with confidence scoring
    and multi-stage validation pipeline.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the intelligent extractor.

        Args:
            api_key: Anthropic API key. If None, will look for ANTHROPIC_API_KEY env var.
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = AI_CONFIG['model']
        self.max_tokens = AI_CONFIG['max_tokens']
        self.temperature = AI_CONFIG['temperature']
        self.max_retries = AI_CONFIG['max_retries']
        self.retry_delay = AI_CONFIG['retry_delay_seconds']

        # Contract parameters (can be overridden per extraction)
        self.contract_term = CONTRACT_DEFAULTS['term_years']
        self.annual_increase = CONTRACT_DEFAULTS['annual_increase_rate']
        self.growth_rate = CONTRACT_DEFAULTS['volume_growth_rate']

        logger.info(f"IntelligentExtractor initialized with model: {self.model}")

    def extract(
        self,
        document_text: str,
        tables: Optional[List[Dict]] = None,
        contract_term: Optional[int] = None,
        annual_increase: Optional[float] = None,
        growth_rate: Optional[float] = None,
        vendor_context: Optional[Dict] = None
    ) -> ExtractionResult:
        """
        Execute the full 4-stage extraction pipeline.

        Args:
            document_text: Raw text extracted from the document
            tables: List of table dictionaries extracted from document
            contract_term: Contract term in years (overrides default)
            annual_increase: Annual price increase rate (overrides default)
            growth_rate: Volume growth rate (overrides default)
            vendor_context: Optional cached vendor context for faster extraction

        Returns:
            ExtractionResult with all extracted data and confidence scores
        """
        # Override defaults if provided
        term = contract_term or self.contract_term
        increase = annual_increase or self.annual_increase
        growth = growth_rate or self.growth_rate

        result = ExtractionResult()
        tables_str = json.dumps(tables or [], indent=2)

        try:
            # Stage 1: Context Analysis
            logger.info("Stage 1: Analyzing document context...")
            context = self._stage1_context_analysis(
                document_text, tables_str, vendor_context
            )
            result.context = context

            if not context:
                result.errors.append("Stage 1 failed: Could not analyze document context")
                return result

            # Stage 2: Line Item Extraction
            logger.info("Stage 2: Extracting line items...")
            line_items, stated_totals = self._stage2_line_item_extraction(
                document_text, tables_str, context
            )
            result.line_items = line_items

            if not line_items:
                result.warnings.append("Stage 2: No line items extracted")

            # Stage 3: Calculation Engine
            logger.info("Stage 3: Calculating projections...")
            calculations = self._stage3_calculation_engine(
                line_items, term, increase, growth
            )
            result.calculations = calculations

            # Stage 4: QA Validation
            logger.info("Stage 4: Running QA validation...")
            qa_results = self._stage4_qa_validation(
                line_items, calculations, stated_totals, context
            )
            result.qa_results = qa_results

            # Calculate overall confidence
            result.overall_confidence = self._calculate_overall_confidence(
                line_items, qa_results
            )

            logger.info(f"Extraction complete. Overall confidence: {result.overall_confidence:.2%}")

        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            result.errors.append(f"Extraction failed: {str(e)}")

        return result

    def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        parse_json: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Call the Claude API with retry logic.

        Args:
            system_prompt: System message for context
            user_prompt: User message with the actual request
            parse_json: Whether to parse response as JSON

        Returns:
            Parsed response or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )

                content = response.content[0].text

                if parse_json:
                    # Extract JSON from response (handle markdown code blocks)
                    json_str = self._extract_json(content)
                    return json.loads(json_str)

                return {"text": content}

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            except anthropic.APIError as e:
                logger.error(f"API error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        return None

    def _extract_json(self, content: str) -> str:
        """Extract JSON from response, handling markdown code blocks."""
        import re

        # Try to find JSON in code blocks first
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                json_str = content[start:end].strip()
                # Clean up common issues
                return self._clean_json(json_str)

        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                json_str = content[start:end].strip()
                return self._clean_json(json_str)

        # Try to find raw JSON
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return self._clean_json(content[start:end])

        return content

    def _clean_json(self, json_str: str) -> str:
        """Clean up common JSON issues."""
        import re

        # Remove trailing commas before } or ]
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # Fix unescaped quotes in strings (basic attempt)
        # Replace problematic characters
        json_str = json_str.replace('\t', ' ')

        return json_str

    def _stage1_context_analysis(
        self,
        document_text: str,
        tables: str,
        vendor_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Stage 1: Analyze document to understand structure and terminology.

        Returns context dict with vendor info, terminology map, etc.
        """
        system_prompt = get_prompt('tco_system')

        # Use cached context if available to skip full analysis
        if vendor_context and vendor_context.get('terminology_map'):
            logger.info("Using cached vendor context")
            return vendor_context

        user_prompt = get_prompt(
            'context_analysis',
            document_text=document_text[:15000],  # Limit text length
            tables=tables[:5000]
        )

        result = self._call_api(system_prompt, user_prompt)

        if result:
            logger.info(f"Context analysis complete. Vendor: {result.get('vendor_name', 'Unknown')}")

        return result or {}

    def _stage2_line_item_extraction(
        self,
        document_text: str,
        tables: str,
        context: Dict[str, Any]
    ) -> Tuple[List[Dict], Dict]:
        """
        Stage 2: Extract all line items with confidence scores.

        Returns tuple of (line_items, stated_totals).
        """
        system_prompt = get_prompt('tco_system')
        user_prompt = get_prompt(
            'line_item_extraction',
            context=json.dumps(context, indent=2),
            document_text=document_text[:20000],
            tables=tables
        )

        result = self._call_api(system_prompt, user_prompt)

        if not result:
            return [], {}

        line_items = result.get('line_items', [])
        stated_totals = result.get('stated_totals', {})

        # Convert to LineItem objects and back for validation
        validated_items = []
        for item in line_items:
            try:
                validated_items.append(self._validate_line_item(item))
            except Exception as e:
                logger.warning(f"Invalid line item skipped: {e}")

        logger.info(f"Extracted {len(validated_items)} line items")
        return validated_items, stated_totals

    def _validate_line_item(self, item: Dict) -> Dict:
        """Validate and normalize a line item dictionary."""
        # Ensure required fields exist
        required_fields = ['solution_name', 'fee_type', 'category']
        for field in required_fields:
            if field not in item or not item[field]:
                raise ValueError(f"Missing required field: {field}")

        # Normalize fee_type
        valid_fee_types = ['Monthly F', 'Monthly V', 'Annual', 'One-Time']
        if item['fee_type'] not in valid_fee_types:
            # Try to map common variations
            fee_type_map = {
                'monthly': 'Monthly F',
                'monthly fixed': 'Monthly F',
                'monthly variable': 'Monthly V',
                'annual': 'Annual',
                'yearly': 'Annual',
                'one-time': 'One-Time',
                'onetime': 'One-Time',
                'one time': 'One-Time',
            }
            mapped = fee_type_map.get(item['fee_type'].lower(), 'Monthly F')
            logger.warning(f"Mapped fee_type '{item['fee_type']}' to '{mapped}'")
            item['fee_type'] = mapped

        # Ensure numeric fields are floats
        numeric_fields = ['per_unit_rate', 'monthly_fee', 'annual_fee', 'one_time_fee']
        for field in numeric_fields:
            if field in item:
                try:
                    item[field] = float(item[field] or 0)
                except (ValueError, TypeError):
                    item[field] = 0.0

        # Ensure boolean fields
        item['optional'] = bool(item.get('optional', False))
        item['third_party'] = bool(item.get('third_party', False))

        # Ensure confidence scores
        if 'field_confidence' not in item:
            item['field_confidence'] = {}
        if 'overall_confidence' not in item:
            item['overall_confidence'] = 0.85  # Default confidence

        return item

    def _stage3_calculation_engine(
        self,
        line_items: List[Dict],
        contract_term: int,
        annual_increase: float,
        growth_rate: float
    ) -> Dict[str, Any]:
        """
        Stage 3: Calculate multi-year projections.

        Can be done locally or via API for complex scenarios.
        """
        # For simple calculations, do locally for speed
        if len(line_items) < 50:
            return self._calculate_projections_local(
                line_items, contract_term, annual_increase, growth_rate
            )

        # For complex scenarios, use API
        system_prompt = get_prompt('tco_system')
        user_prompt = get_prompt(
            'calculation_engine',
            line_items=json.dumps(line_items, indent=2),
            contract_term=contract_term,
            annual_increase=annual_increase * 100,
            growth_rate=growth_rate * 100
        )

        result = self._call_api(system_prompt, user_prompt)
        return result or self._calculate_projections_local(
            line_items, contract_term, annual_increase, growth_rate
        )

    def _calculate_projections_local(
        self,
        line_items: List[Dict],
        contract_term: int,
        annual_increase: float,
        growth_rate: float
    ) -> Dict[str, Any]:
        """Calculate projections locally without API call."""
        calculated_items = []
        year_totals = {f"year_{i}": 0.0 for i in range(1, contract_term + 1)}
        category_totals = {}

        for item in line_items:
            fee_type = item.get('fee_type', 'Monthly F')
            category = item.get('category', 'Non-Bundle Required')

            # Determine base amount
            if fee_type in ['Monthly F', 'Monthly V']:
                base_amount = item.get('monthly_fee', 0) or item.get('per_unit_rate', 0)
                base_qty = 12  # Monthly items
            elif fee_type == 'Annual':
                base_amount = item.get('annual_fee', 0) or item.get('per_unit_rate', 0)
                base_qty = 1
            else:  # One-Time
                base_amount = item.get('one_time_fee', 0) or item.get('per_unit_rate', 0)
                base_qty = 1

            item_costs = {}
            item_qtys = {}

            for year in range(1, contract_term + 1):
                if fee_type == 'One-Time':
                    # One-time fees only in year 1
                    qty = 1 if year == 1 else 0
                    rate = base_amount
                else:
                    # Apply growth rate to quantities (for variable fees)
                    if fee_type == 'Monthly V':
                        qty = base_qty * ((1 + growth_rate) ** (year - 1))
                    else:
                        qty = base_qty

                    # Apply annual increase to rates
                    rate = base_amount * ((1 + annual_increase) ** (year - 1))

                cost = qty * rate
                item_costs[f"year_{year}"] = round(cost, 2)
                item_qtys[f"year_{year}"] = round(qty, 2)
                year_totals[f"year_{year}"] += cost

            total_cost = sum(item_costs.values())

            calculated_items.append({
                "solution_name": item.get('solution_name'),
                "quantities_by_year": item_qtys,
                "costs_by_year": item_costs,
                "total_contract_cost": round(total_cost, 2)
            })

            # Category totals
            if category not in category_totals:
                category_totals[category] = 0.0
            category_totals[category] += total_cost

        grand_total = sum(year_totals.values())

        return {
            "calculated_items": calculated_items,
            "summary": {
                "total_contract_value": round(grand_total, 2),
                "average_annual_cost": round(grand_total / contract_term, 2),
                "year_by_year_totals": {k: round(v, 2) for k, v in year_totals.items()},
                "category_totals": {k: round(v, 2) for k, v in category_totals.items()}
            },
            "calculation_notes": ["Calculated locally"]
        }

    def _stage4_qa_validation(
        self,
        line_items: List[Dict],
        calculations: Dict,
        stated_totals: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Stage 4: Validate extraction accuracy.

        Runs multiple validation checks and returns results.
        """
        system_prompt = get_prompt('tco_system')
        user_prompt = get_prompt(
            'qa_validation',
            line_items=json.dumps(line_items, indent=2),
            calculated_totals=json.dumps(calculations.get('summary', {}), indent=2),
            stated_totals=json.dumps(stated_totals, indent=2),
            document_context=json.dumps({
                'vendor': context.get('vendor_name', 'Unknown'),
                'document_type': context.get('document_type', 'Unknown')
            }, indent=2)
        )

        result = self._call_api(system_prompt, user_prompt)

        if not result:
            # Run basic local validation
            return self._validate_locally(line_items, calculations, stated_totals)

        return result

    def _validate_locally(
        self,
        line_items: List[Dict],
        calculations: Dict,
        stated_totals: Dict
    ) -> Dict[str, Any]:
        """Run basic validation checks locally."""
        checks = []
        failed_items = []

        # Check 1: Sum verification
        calc_monthly_total = sum(
            item.get('monthly_fee', 0) for item in line_items
            if item.get('fee_type') in ['Monthly F', 'Monthly V']
        )
        stated_monthly = stated_totals.get('monthly_total', 0)

        if stated_monthly > 0:
            diff = abs(calc_monthly_total - stated_monthly) / stated_monthly
            checks.append({
                "check_name": "Sum Verification - Monthly",
                "passed": diff < 0.02,  # 2% tolerance
                "expected": stated_monthly,
                "actual": calc_monthly_total,
                "discrepancy": f"{diff:.1%}" if diff >= 0.02 else None
            })

        # Check 2: No required items with $0
        for item in line_items:
            if not item.get('optional', False):
                amounts = [
                    item.get('monthly_fee', 0),
                    item.get('annual_fee', 0),
                    item.get('one_time_fee', 0),
                    item.get('per_unit_rate', 0)
                ]
                if all(amt == 0 for amt in amounts):
                    failed_items.append({
                        "solution_name": item.get('solution_name'),
                        "failure_reason": "Required item with $0 pricing",
                        "failed_checks": ["Business Rules - Zero Pricing"],
                        "suggested_action": "Verify pricing or mark as optional"
                    })

        # Check 3: Confidence scores
        low_confidence_count = sum(
            1 for item in line_items
            if item.get('overall_confidence', 1.0) < CONFIDENCE_THRESHOLDS['manual_review']
        )

        checks.append({
            "check_name": "Confidence Check",
            "passed": low_confidence_count == 0,
            "expected": "All items >= 70% confidence",
            "actual": f"{low_confidence_count} items below threshold"
        })

        all_passed = all(c.get('passed', True) for c in checks)

        return {
            "validation_passed": all_passed and len(failed_items) == 0,
            "checks_performed": checks,
            "failed_items": failed_items,
            "passed_items_count": len(line_items) - len(failed_items),
            "failed_items_count": len(failed_items),
            "overall_confidence": self._calculate_average_confidence(line_items),
            "validation_summary": "All checks passed" if all_passed else "Some checks failed"
        }

    def _calculate_average_confidence(self, line_items: List[Dict]) -> float:
        """Calculate average confidence across all line items."""
        if not line_items:
            return 0.0

        confidences = [
            item.get('overall_confidence', 0.85)
            for item in line_items
        ]
        return sum(confidences) / len(confidences)

    def _calculate_overall_confidence(
        self,
        line_items: List[Dict],
        qa_results: Dict
    ) -> float:
        """Calculate overall extraction confidence."""
        if not line_items:
            return 0.0

        # Average item confidence
        avg_confidence = self._calculate_average_confidence(line_items)

        # Adjust based on QA results
        if not qa_results.get('validation_passed', True):
            failed_ratio = qa_results.get('failed_items_count', 0) / len(line_items)
            avg_confidence *= (1 - failed_ratio * 0.5)  # Reduce by up to 50%

        return round(avg_confidence, 4)

    def extract_single_stage(
        self,
        stage: str,
        document_text: str,
        tables: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a single extraction stage (for debugging/testing).

        Args:
            stage: One of 'context', 'line_items', 'calculations', 'qa'
            document_text: Document text
            tables: Optional tables
            **kwargs: Additional stage-specific parameters
        """
        tables_str = json.dumps(tables or [], indent=2)

        if stage == 'context':
            return self._stage1_context_analysis(
                document_text, tables_str, kwargs.get('vendor_context')
            )

        elif stage == 'line_items':
            context = kwargs.get('context', {})
            items, totals = self._stage2_line_item_extraction(
                document_text, tables_str, context
            )
            return {"line_items": items, "stated_totals": totals}

        elif stage == 'calculations':
            line_items = kwargs.get('line_items', [])
            return self._stage3_calculation_engine(
                line_items,
                kwargs.get('contract_term', self.contract_term),
                kwargs.get('annual_increase', self.annual_increase),
                kwargs.get('growth_rate', self.growth_rate)
            )

        elif stage == 'qa':
            return self._stage4_qa_validation(
                kwargs.get('line_items', []),
                kwargs.get('calculations', {}),
                kwargs.get('stated_totals', {}),
                kwargs.get('context', {})
            )

        else:
            raise ValueError(f"Unknown stage: {stage}")
