"""
Pipeline Module

Orchestrates the complete document processing pipeline from ingestion to output.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Local imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.document_loader import DocumentLoader, ExtractedDocument
from extractors.llm_extractor import LLMExtractor, ExtractionResult
from preprocessors.text_processor import TextProcessor
from mappers.schema_mapper import SchemaMapper
from writers.tco_writer import TCOWriter


logger = logging.getLogger(__name__)


class StageStatus(Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    """Represents a single stage in the pipeline."""
    name: str
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class PipelineResult:
    """Complete result of pipeline execution."""
    success: bool
    stages: List[PipelineStage]
    output_file: Optional[str]
    start_time: datetime
    end_time: datetime
    total_documents: int
    processed_documents: int
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class Pipeline:
    """
    Document processing pipeline orchestrator.

    Stages:
    1. Ingestion - Load documents (PDF/DOCX/XLSX/images)
    2. Preprocessing - Clean and chunk text
    3. Extraction - Extract structured fields using LLM/NLP
    4. Validation - Validate and fix extracted data
    5. Mapping - Map to TCO schema
    6. Output - Write to Excel
    """

    def __init__(
        self,
        input_dir: str = './data/raw',
        output_dir: str = './data/output',
        processed_dir: str = './data/processed',
        template_path: Optional[str] = None,
        api_key: Optional[str] = None,
        use_llm: bool = True
    ):
        """
        Initialize pipeline.

        Args:
            input_dir: Directory containing input documents
            output_dir: Directory for output Excel files
            processed_dir: Directory for intermediate JSON files
            template_path: Path to TCO Excel template
            api_key: Anthropic API key for LLM extraction
            use_llm: Whether to use LLM for extraction
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.processed_dir = Path(processed_dir)
        self.template_path = template_path
        self.use_llm = use_llm

        # Initialize components
        self.loader = DocumentLoader()
        self.text_processor = TextProcessor()
        self.llm_extractor = LLMExtractor(api_key=api_key) if use_llm else None
        self.schema_mapper = SchemaMapper()

        # Pipeline state
        self.stages: List[PipelineStage] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _create_stages(self) -> List[PipelineStage]:
        """Create the pipeline stages."""
        return [
            PipelineStage(name="ingestion"),
            PipelineStage(name="preprocessing"),
            PipelineStage(name="extraction"),
            PipelineStage(name="validation"),
            PipelineStage(name="mapping"),
            PipelineStage(name="output")
        ]

    def _run_stage(
        self,
        stage: PipelineStage,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Run a single pipeline stage with error handling.

        Args:
            stage: The pipeline stage
            func: Function to execute
            *args, **kwargs: Arguments for the function

        Returns:
            Result of the function
        """
        stage.status = StageStatus.RUNNING
        stage.start_time = time.time()

        try:
            result = func(*args, **kwargs)
            stage.status = StageStatus.COMPLETED
            stage.result = result
            return result

        except Exception as e:
            stage.status = StageStatus.FAILED
            stage.error = str(e)
            self.errors.append(f"Stage '{stage.name}' failed: {e}")
            logger.error(f"Stage '{stage.name}' failed: {e}")
            raise

        finally:
            stage.end_time = time.time()

    def run(
        self,
        input_files: Optional[List[str]] = None,
        output_filename: Optional[str] = None,
        vendor: Optional[str] = None,
        term: str = '5_year'
    ) -> PipelineResult:
        """
        Run the complete pipeline.

        Args:
            input_files: Specific files to process (or all in input_dir)
            output_filename: Name for output file
            vendor: Vendor name (FIS, Jack Henry)
            term: Contract term

        Returns:
            PipelineResult with complete execution details
        """
        start_time = datetime.now()
        self.stages = self._create_stages()
        self.errors = []
        self.warnings = []

        documents = []
        extracted_data = []
        normalized_data = []

        try:
            # Stage 1: Ingestion
            stage = self.stages[0]
            if input_files:
                documents = self._run_stage(
                    stage,
                    self._ingest_files,
                    input_files
                )
            else:
                documents = self._run_stage(
                    stage,
                    self._ingest_directory
                )

            if not documents:
                self.warnings.append("No documents found to process")
                return self._create_result(
                    success=False,
                    output_file=None,
                    start_time=start_time,
                    documents=documents
                )

            # Stage 2: Preprocessing
            stage = self.stages[1]
            processed_docs = self._run_stage(
                stage,
                self._preprocess_documents,
                documents
            )

            # Stage 3: Extraction
            stage = self.stages[2]
            extracted_data = self._run_stage(
                stage,
                self._extract_data,
                processed_docs,
                vendor
            )

            # Stage 4: Validation
            stage = self.stages[3]
            validated_data = self._run_stage(
                stage,
                self._validate_data,
                extracted_data
            )

            # Stage 5: Mapping
            stage = self.stages[4]
            normalized_data = self._run_stage(
                stage,
                self._map_data,
                validated_data,
                vendor,
                term
            )

            # Stage 6: Output
            stage = self.stages[5]
            output_file = self._run_stage(
                stage,
                self._write_output,
                normalized_data,
                output_filename,
                vendor
            )

            return self._create_result(
                success=True,
                output_file=output_file,
                start_time=start_time,
                documents=documents
            )

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return self._create_result(
                success=False,
                output_file=None,
                start_time=start_time,
                documents=documents
            )

    def _ingest_files(self, file_paths: List[str]) -> List[ExtractedDocument]:
        """Load specific files."""
        documents = []
        for path in file_paths:
            try:
                doc = self.loader.load(path)
                documents.append(doc)
                logger.info(f"Loaded: {path}")
            except Exception as e:
                self.warnings.append(f"Failed to load {path}: {e}")
                logger.warning(f"Failed to load {path}: {e}")
        return documents

    def _ingest_directory(self) -> List[ExtractedDocument]:
        """Load all documents from input directory."""
        return self.loader.load_directory(str(self.input_dir))

    def _preprocess_documents(
        self,
        documents: List[ExtractedDocument]
    ) -> List[Dict[str, Any]]:
        """Preprocess and clean documents."""
        processed = []

        for doc in documents:
            # Clean text
            cleaned_text = self.text_processor.clean_for_extraction(doc.raw_text)

            # Chunk if needed
            chunks = self.text_processor.chunk(cleaned_text)

            processed.append({
                'file_path': doc.file_path,
                'document_type': doc.document_type.value,
                'cleaned_text': cleaned_text,
                'chunks': chunks,
                'tables': doc.tables,
                'metadata': doc.metadata
            })

        return processed

    def _extract_data(
        self,
        processed_docs: List[Dict[str, Any]],
        vendor: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Extract structured data from documents."""
        extracted = []

        for doc in processed_docs:
            if self.use_llm and self.llm_extractor:
                # Use LLM extraction
                if doc['chunks']:
                    result = self.llm_extractor.extract_from_chunks(
                        doc['chunks'],
                        self.llm_extractor.TCO_FIELDS
                    )
                else:
                    result = self.llm_extractor.extract_tco_fields(
                        doc['cleaned_text'],
                        vendor
                    )

                extracted.append({
                    'file_path': doc['file_path'],
                    'fields': result.fields,
                    'confidence': result.confidence,
                    'method': result.extraction_method,
                    'tables': doc['tables'],
                    'warnings': result.warnings
                })

                if result.warnings:
                    self.warnings.extend(result.warnings)
            else:
                # Fallback: return raw data for rule-based extraction
                extracted.append({
                    'file_path': doc['file_path'],
                    'fields': {},
                    'confidence': 0.0,
                    'method': 'none',
                    'tables': doc['tables'],
                    'raw_text': doc['cleaned_text']
                })

        # Save intermediate results
        self._save_intermediate(extracted, 'extracted.json')

        return extracted

    def _validate_data(
        self,
        extracted_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate extracted data and apply corrections."""
        validated = []

        for data in extracted_data:
            fields = data['fields']
            validation_errors = []
            corrections = []

            # Apply auto-corrections
            for field_name, value in fields.items():
                corrected, was_corrected = self._auto_correct(field_name, value)
                if was_corrected:
                    corrections.append(f"{field_name}: '{value}' -> '{corrected}'")
                    fields[field_name] = corrected

            # Validate required fields
            required = ['solution_name', 'fee_type', 'category']
            for req in required:
                if req not in fields or not fields[req]:
                    validation_errors.append(f"Missing required field: {req}")

            # Validate numeric fields
            numeric_fields = ['monthly_fee', 'annual_fee', 'one_time_fee']
            for nf in numeric_fields:
                if nf in fields and fields[nf] is not None:
                    try:
                        fields[nf] = float(str(fields[nf]).replace('$', '').replace(',', ''))
                    except (ValueError, TypeError):
                        validation_errors.append(f"Invalid numeric value for {nf}")

            validated.append({
                **data,
                'fields': fields,
                'validation_errors': validation_errors,
                'corrections': corrections
            })

            if validation_errors:
                self.warnings.extend(validation_errors)

        return validated

    def _auto_correct(self, field_name: str, value: Any) -> tuple[Any, bool]:
        """Apply auto-corrections to field values."""
        if value is None:
            return value, False

        # Fee type corrections
        if field_name == 'fee_type':
            corrections = {
                'monthly': 'Monthly F',
                'annual': 'Annual',
                'one-time': 'One-Time',
                'onetime': 'One-Time'
            }
            lower_val = str(value).lower()
            if lower_val in corrections:
                return corrections[lower_val], True

        # Category corrections
        if field_name == 'category':
            corrections = {
                'bundle': 'Bundle',
                'optional': 'Non-Bundle Optional',
                'required': 'Non-Bundle Required'
            }
            lower_val = str(value).lower()
            if lower_val in corrections:
                return corrections[lower_val], True

        return value, False

    def _map_data(
        self,
        validated_data: List[Dict[str, Any]],
        vendor: Optional[str],
        term: str
    ) -> List[Dict[str, Any]]:
        """Map extracted data to TCO schema."""
        # For now, pass through - the schema_mapper handles the actual mapping
        # when writing to Excel

        mapped = []
        for data in validated_data:
            mapped.append({
                **data,
                'vendor': vendor or data['fields'].get('vendor_name', 'Unknown'),
                'term': term
            })

        return mapped

    def _write_output(
        self,
        normalized_data: List[Dict[str, Any]],
        output_filename: Optional[str],
        vendor: Optional[str]
    ) -> str:
        """Write data to Excel output."""
        # Generate output filename
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            vendor_str = vendor or 'multi'
            output_filename = f"tco_output_{vendor_str}_{timestamp}.xlsx"

        output_path = self.output_dir / output_filename

        # For now, save as JSON (Excel writing requires template)
        # The TCOWriter would be used with a template
        json_output = output_path.with_suffix('.json')
        with open(json_output, 'w') as f:
            json.dump(normalized_data, f, indent=2, default=str)

        logger.info(f"Output saved to: {json_output}")

        # If template provided, write to Excel
        if self.template_path and os.path.exists(self.template_path):
            try:
                writer = TCOWriter(self.template_path, str(output_path))
                # Would need to format data for writer here
                writer.save()
                return str(output_path)
            except Exception as e:
                self.warnings.append(f"Excel output failed: {e}")

        return str(json_output)

    def _save_intermediate(self, data: Any, filename: str):
        """Save intermediate results for debugging."""
        path = self.processed_dir / filename
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def _create_result(
        self,
        success: bool,
        output_file: Optional[str],
        start_time: datetime,
        documents: List
    ) -> PipelineResult:
        """Create the pipeline result object."""
        return PipelineResult(
            success=success,
            stages=self.stages,
            output_file=output_file,
            start_time=start_time,
            end_time=datetime.now(),
            total_documents=len(documents),
            processed_documents=sum(
                1 for s in self.stages
                if s.status == StageStatus.COMPLETED
            ),
            errors=self.errors,
            warnings=self.warnings
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        return {
            'stages': [
                {
                    'name': s.name,
                    'status': s.status.value,
                    'duration': s.duration
                }
                for s in self.stages
            ],
            'errors': self.errors,
            'warnings': self.warnings
        }


def run_pipeline(
    input_path: str,
    output_dir: str = './data/output',
    template_path: Optional[str] = None,
    vendor: Optional[str] = None,
    term: str = '5_year',
    use_llm: bool = True
) -> PipelineResult:
    """
    Convenience function to run the pipeline.

    Args:
        input_path: File or directory to process
        output_dir: Output directory
        template_path: TCO template path
        vendor: Vendor name
        term: Contract term
        use_llm: Whether to use LLM extraction

    Returns:
        PipelineResult
    """
    # Determine if input is file or directory
    input_path = Path(input_path)

    if input_path.is_file():
        pipeline = Pipeline(
            input_dir=str(input_path.parent),
            output_dir=output_dir,
            template_path=template_path,
            use_llm=use_llm
        )
        return pipeline.run(
            input_files=[str(input_path)],
            vendor=vendor,
            term=term
        )
    else:
        pipeline = Pipeline(
            input_dir=str(input_path),
            output_dir=output_dir,
            template_path=template_path,
            use_llm=use_llm
        )
        return pipeline.run(vendor=vendor, term=term)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run TCO document processing pipeline')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', '-o', default='./data/output', help='Output directory')
    parser.add_argument('--template', '-t', help='TCO template path')
    parser.add_argument('--vendor', '-v', help='Vendor name')
    parser.add_argument('--term', default='5_year', help='Contract term')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM extraction')

    args = parser.parse_args()

    result = run_pipeline(
        input_path=args.input,
        output_dir=args.output,
        template_path=args.template,
        vendor=args.vendor,
        term=args.term,
        use_llm=not args.no_llm
    )

    print(f"\nPipeline {'succeeded' if result.success else 'failed'}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Documents: {result.processed_documents}/{result.total_documents}")

    if result.output_file:
        print(f"Output: {result.output_file}")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings[:5]:
            print(f"  - {warning}")
        if len(result.warnings) > 5:
            print(f"  ... and {len(result.warnings) - 5} more")
