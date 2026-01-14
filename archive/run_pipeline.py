#!/usr/bin/env python3
"""
TCO Automation Pipeline - Main Entry Point

Simple CLI for running the document processing pipeline.

Usage:
    python run_pipeline.py input_file.docx
    python run_pipeline.py data/raw/ --vendor FIS --term 7_year
    python run_pipeline.py --help
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator.pipeline import Pipeline, run_pipeline
from orchestrator.scheduler import Scheduler, JobConfig
from utils.logging_config import setup_logging


def main():
    parser = argparse.ArgumentParser(
        description='TCO Automation - Document Processing Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a single FIS document:
    python run_pipeline.py proposal.docx --vendor FIS --term 7_year

  Process all documents in a directory:
    python run_pipeline.py data/raw/ -o data/output/

  Run with LLM extraction disabled:
    python run_pipeline.py document.docx --no-llm

  Schedule recurring jobs:
    python run_pipeline.py --schedule config/jobs.json
        """
    )

    # Input arguments
    parser.add_argument(
        'input',
        nargs='?',
        help='Input file or directory to process'
    )

    # Output options
    parser.add_argument(
        '-o', '--output',
        default='./data/output',
        help='Output directory (default: ./data/output)'
    )
    parser.add_argument(
        '-t', '--template',
        help='TCO Excel template file'
    )

    # Processing options
    parser.add_argument(
        '-v', '--vendor',
        choices=['FIS', 'Jack Henry', 'auto'],
        default='auto',
        help='Vendor type (default: auto-detect)'
    )
    parser.add_argument(
        '--term',
        choices=['5_year', '7_year', '10_year'],
        default='5_year',
        help='Contract term (default: 5_year)'
    )
    parser.add_argument(
        '--scenario',
        default='Proposal_1',
        help='Jack Henry scenario name (default: Proposal_1)'
    )

    # LLM options
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM extraction (use rule-based only)'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )

    # Scheduling options
    parser.add_argument(
        '--schedule',
        help='Path to jobs configuration file for scheduling'
    )
    parser.add_argument(
        '--run-job',
        help='Run a specific scheduled job by name'
    )

    # Output options
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    # Version
    parser.add_argument(
        '--version',
        action='version',
        version='TCO Automation Pipeline v2.0'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level)
    logger = logging.getLogger(__name__)

    # Handle scheduling mode
    if args.schedule:
        return run_scheduler(args)

    # Require input for processing mode
    if not args.input:
        parser.print_help()
        print("\nError: Input file or directory required")
        return 1

    # Validate input exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input not found: {args.input}")
        return 1

    # Auto-detect vendor from filename if needed
    vendor = args.vendor
    if vendor == 'auto':
        vendor = detect_vendor(str(input_path))
        if not args.quiet:
            print(f"Auto-detected vendor: {vendor or 'Unknown'}")

    # Run pipeline
    if not args.quiet:
        print(f"\n{'='*60}")
        print("TCO Automation Pipeline")
        print(f"{'='*60}")
        print(f"Input: {args.input}")
        print(f"Output: {args.output}")
        print(f"Vendor: {vendor or 'Auto'}")
        print(f"Term: {args.term}")
        print(f"LLM: {'Disabled' if args.no_llm else 'Enabled'}")
        print(f"{'='*60}\n")

    try:
        result = run_pipeline(
            input_path=str(input_path),
            output_dir=args.output,
            template_path=args.template,
            vendor=vendor,
            term=args.term,
            use_llm=not args.no_llm
        )

        # Print results
        if args.json:
            import json
            output = {
                'success': result.success,
                'duration_seconds': result.duration_seconds,
                'documents_processed': result.processed_documents,
                'output_file': result.output_file,
                'errors': result.errors,
                'warnings': result.warnings[:10]
            }
            print(json.dumps(output, indent=2))
        else:
            print_result(result, args.quiet)

        return 0 if result.success else 1

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def detect_vendor(filepath: str) -> str:
    """Auto-detect vendor from filename."""
    filename = os.path.basename(filepath).lower()

    if 'fis' in filename:
        return 'FIS'
    elif 'jack' in filename or 'jh' in filename or 'silverlake' in filename:
        return 'Jack Henry'

    # Check file extension
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.docx':
        return 'FIS'  # FIS typically uses Word
    elif ext == '.xlsx':
        return 'Jack Henry'  # JH typically uses Excel

    return None


def print_result(result, quiet: bool = False):
    """Print pipeline result summary."""
    status = "SUCCESS" if result.success else "FAILED"

    print(f"\n{'='*60}")
    print(f"Pipeline Result: {status}")
    print(f"{'='*60}")
    print(f"Duration: {result.duration_seconds:.2f} seconds")
    print(f"Documents processed: {result.processed_documents}/{result.total_documents}")

    if result.output_file:
        print(f"Output file: {result.output_file}")

    # Stage summary
    if not quiet:
        print(f"\nStage Summary:")
        for stage in result.stages:
            status_icon = "✓" if stage.status.value == "completed" else "✗" if stage.status.value == "failed" else "○"
            duration = f"{stage.duration:.2f}s" if stage.duration else "N/A"
            print(f"  {status_icon} {stage.name}: {stage.status.value} ({duration})")

    # Errors
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")

    # Warnings (show first 5)
    if result.warnings and not quiet:
        print(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings[:5]:
            print(f"  - {warning}")
        if len(result.warnings) > 5:
            print(f"  ... and {len(result.warnings) - 5} more")

    print()


def run_scheduler(args):
    """Run in scheduler mode."""
    scheduler = Scheduler(config_path=args.schedule)

    if args.run_job:
        # Run specific job
        result = scheduler.run_now(args.run_job)
        if result:
            print(f"Job '{result.job_name}': {'success' if result.success else 'failed'}")
            print(f"Documents processed: {result.documents_processed}")
            if result.output_file:
                print(f"Output: {result.output_file}")
            return 0 if result.success else 1
        else:
            print(f"Job not found: {args.run_job}")
            return 1
    else:
        # Start scheduler daemon
        print("Starting scheduler...")
        print("Press Ctrl+C to stop")
        try:
            scheduler.start(blocking=True)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nScheduler stopped")
        return 0


if __name__ == '__main__':
    sys.exit(main())
