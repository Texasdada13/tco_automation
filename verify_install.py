#!/usr/bin/env python3
"""
Installation Verification Script

Checks that all dependencies and components are properly installed.
Run this after installing requirements to verify setup.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    package_name = package_name or module_name
    try:
        __import__(module_name)
        return True, None
    except ImportError as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("TCO Automation - Installation Verification")
    print("=" * 60)
    print()

    all_passed = True
    warnings = []

    # Core dependencies
    print("Checking core dependencies...")
    core_deps = [
        ('openpyxl', 'openpyxl'),
        ('docx', 'python-docx'),
        ('pandas', 'pandas'),
    ]

    for module, package in core_deps:
        ok, error = check_import(module)
        status = "OK" if ok else "MISSING"
        print(f"  {package}: {status}")
        if not ok:
            all_passed = False

    print()

    # Document processing dependencies
    print("Checking document processing dependencies...")
    doc_deps = [
        ('pdfplumber', 'pdfplumber', 'PDF text extraction'),
        ('fitz', 'PyMuPDF', 'PDF image extraction'),
        ('pytesseract', 'pytesseract', 'OCR'),
        ('PIL', 'Pillow', 'Image processing'),
    ]

    for module, package, desc in doc_deps:
        ok, error = check_import(module)
        status = "OK" if ok else "MISSING"
        print(f"  {package} ({desc}): {status}")
        if not ok:
            warnings.append(f"{package} not installed - {desc} will be unavailable")

    print()

    # NLP dependencies
    print("Checking NLP dependencies...")
    nlp_deps = [
        ('tiktoken', 'tiktoken', 'Token counting'),
        ('nltk', 'nltk', 'Sentence tokenization'),
        ('spacy', 'spacy', 'Named Entity Recognition'),
        ('rapidfuzz', 'rapidfuzz', 'Fuzzy matching'),
    ]

    for module, package, desc in nlp_deps:
        ok, error = check_import(module)
        status = "OK" if ok else "MISSING"
        print(f"  {package} ({desc}): {status}")
        if not ok:
            warnings.append(f"{package} not installed - {desc} will be unavailable")

    # Check spaCy model
    if check_import('spacy')[0]:
        try:
            import spacy
            spacy.load('en_core_web_sm')
            print(f"  spacy model (en_core_web_sm): OK")
        except OSError:
            print(f"  spacy model (en_core_web_sm): MISSING")
            warnings.append("spaCy model not installed - run: python -m spacy download en_core_web_sm")

    print()

    # LLM dependencies
    print("Checking LLM dependencies...")
    llm_deps = [
        ('anthropic', 'anthropic', 'Claude API'),
        ('dotenv', 'python-dotenv', 'Environment variables'),
    ]

    for module, package, desc in llm_deps:
        ok, error = check_import(module)
        status = "OK" if ok else "MISSING"
        print(f"  {package} ({desc}): {status}")
        if not ok:
            warnings.append(f"{package} not installed - {desc} will be unavailable")

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"  ANTHROPIC_API_KEY: SET")
    else:
        print(f"  ANTHROPIC_API_KEY: NOT SET")
        warnings.append("ANTHROPIC_API_KEY not set - LLM extraction will be disabled")

    print()

    # Scheduling dependencies
    print("Checking scheduling dependencies...")
    sched_deps = [
        ('schedule', 'schedule', 'Job scheduling'),
        ('jsonschema', 'jsonschema', 'Schema validation'),
    ]

    for module, package, desc in sched_deps:
        ok, error = check_import(module)
        status = "OK" if ok else "MISSING"
        print(f"  {package} ({desc}): {status}")
        if not ok:
            warnings.append(f"{package} not installed - {desc} will be unavailable")

    print()

    # Check project modules
    print("Checking project modules...")
    project_modules = [
        'config',
        'extractors',
        'extractors.document_loader',
        'extractors.llm_extractor',
        'preprocessors',
        'preprocessors.text_processor',
        'mappers',
        'mappers.schema_mapper',
        'writers',
        'orchestrator',
        'orchestrator.pipeline',
        'orchestrator.scheduler',
        'utils',
    ]

    for module in project_modules:
        ok, error = check_import(module)
        status = "OK" if ok else "ERROR"
        print(f"  {module}: {status}")
        if not ok:
            all_passed = False
            print(f"    Error: {error}")

    print()

    # Check directories
    print("Checking directories...")
    directories = [
        'data/raw',
        'data/processed',
        'data/output',
        'config',
    ]

    for dir_path in directories:
        exists = os.path.isdir(dir_path)
        status = "OK" if exists else "MISSING"
        print(f"  {dir_path}: {status}")

    print()

    # Summary
    print("=" * 60)
    if all_passed and not warnings:
        print("STATUS: All checks passed!")
        print("\nYou're ready to use the pipeline:")
        print("  python run_pipeline.py --help")
    elif all_passed:
        print("STATUS: Core checks passed with warnings")
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print("\nThe pipeline will work but some features may be limited.")
    else:
        print("STATUS: Some checks failed")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")

    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
