"""
Output Manager Module

Manages standardized output folder structure for all extractions.
Provides predictable, organized output locations for all artifacts.

Structure:
./output/
├── YYYY-MM-DD/                          # Date-based organization
│   ├── {vendor}_{client}/
│   │   ├── input/
│   │   │   └── original_proposal.*      # Original file (copied)
│   │   ├── extraction/
│   │   │   ├── raw_extraction.json
│   │   │   └── ai_extraction.json
│   │   ├── validation/
│   │   │   ├── qa_report.json           # QA metrics
│   │   │   ├── qa_report.docx           # Formatted Word report
│   │   │   └── review_items.docx        # If Bucket 2 items exist
│   │   ├── output/
│   │   │   └── TCO_Workbook.xlsx        # Final deliverable
│   │   └── audit/
│   │       └── traceability.json        # Full audit trail
│   └── summary/
│       └── batch_report.xlsx            # All extractions summary
└── latest -> YYYY-MM-DD                 # Points to most recent
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractionPaths:
    """Container for all paths related to an extraction."""
    base_dir: str
    date_dir: str
    extraction_dir: str

    # Input
    input_dir: str
    original_file: str

    # Extraction
    extraction_subdir: str
    raw_extraction: str
    ai_extraction: str

    # Validation
    validation_dir: str
    qa_report_json: str
    qa_report_docx: str
    review_items_docx: str

    # Output
    output_dir: str
    tco_workbook: str

    # Audit
    audit_dir: str
    traceability_json: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class OutputManager:
    """
    Manages standardized output folder structure.

    Usage:
        manager = OutputManager(base_output_dir="./output")
        paths = manager.create_extraction_folder(
            vendor="FIS",
            client="First National Bank",
            source_file="proposal.docx"
        )
        # Now use paths.raw_extraction, paths.ai_extraction, etc.
    """

    def __init__(self, base_output_dir: str = "./output"):
        """
        Initialize the output manager.

        Args:
            base_output_dir: Base directory for all outputs
        """
        self.base_dir = Path(base_output_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"OutputManager initialized with base: {self.base_dir}")

    def create_extraction_folder(
        self,
        vendor: str,
        client: str,
        source_file: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> ExtractionPaths:
        """
        Create the full folder structure for an extraction.

        Args:
            vendor: Vendor name (e.g., "FIS", "Jack Henry")
            client: Client/bank name
            source_file: Path to source file (will be copied to input folder)
            date: Date for organization (defaults to today)

        Returns:
            ExtractionPaths object with all path locations
        """
        # Normalize names for folder creation
        vendor_clean = self._clean_name(vendor)
        client_clean = self._clean_name(client)
        folder_name = f"{vendor_clean}_{client_clean}"

        # Date-based organization
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")

        # Create directory structure
        date_dir = self.base_dir / date_str
        extraction_dir = date_dir / folder_name

        # Subdirectories
        input_dir = extraction_dir / "input"
        extraction_subdir = extraction_dir / "extraction"
        validation_dir = extraction_dir / "validation"
        output_dir = extraction_dir / "output"
        audit_dir = extraction_dir / "audit"

        # Create all directories
        for dir_path in [input_dir, extraction_subdir, validation_dir, output_dir, audit_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create summary directory
        summary_dir = date_dir / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)

        # Copy source file if provided
        original_file_path = ""
        if source_file and os.path.exists(source_file):
            source_path = Path(source_file)
            original_file_path = str(input_dir / source_path.name)
            shutil.copy2(source_file, original_file_path)
            logger.info(f"Copied source file to: {original_file_path}")

        # Build paths object
        paths = ExtractionPaths(
            base_dir=str(self.base_dir),
            date_dir=str(date_dir),
            extraction_dir=str(extraction_dir),

            input_dir=str(input_dir),
            original_file=original_file_path,

            extraction_subdir=str(extraction_subdir),
            raw_extraction=str(extraction_subdir / "raw_extraction.json"),
            ai_extraction=str(extraction_subdir / "ai_extraction.json"),

            validation_dir=str(validation_dir),
            qa_report_json=str(validation_dir / "qa_report.json"),
            qa_report_docx=str(validation_dir / "qa_report.docx"),
            review_items_docx=str(validation_dir / "review_items.docx"),

            output_dir=str(output_dir),
            tco_workbook=str(output_dir / f"{folder_name}_TCO.xlsx"),

            audit_dir=str(audit_dir),
            traceability_json=str(audit_dir / "traceability.json")
        )

        # Update latest symlink
        self._update_latest_link(date_dir)

        logger.info(f"Created extraction folder structure: {extraction_dir}")
        return paths

    def _clean_name(self, name: str) -> str:
        """Clean a name for use in folder/file names."""
        # Remove special characters, replace spaces with underscores
        cleaned = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        # Remove consecutive underscores
        while "__" in cleaned:
            cleaned = cleaned.replace("__", "_")
        # Remove leading/trailing underscores
        cleaned = cleaned.strip("_")
        return cleaned.lower()

    def _update_latest_link(self, date_dir: Path) -> None:
        """Update the 'latest' symlink to point to the most recent date folder."""
        latest_link = self.base_dir / "latest"

        try:
            # Remove existing link if it exists
            if latest_link.exists() or latest_link.is_symlink():
                if latest_link.is_symlink():
                    latest_link.unlink()
                elif latest_link.is_dir():
                    # On Windows, might be a junction or directory
                    try:
                        latest_link.unlink()
                    except:
                        shutil.rmtree(latest_link)

            # Create new symlink (use relative path)
            relative_target = date_dir.name

            # On Windows, use junction for directories
            import platform
            if platform.system() == "Windows":
                # Create a file that points to the latest directory instead
                latest_file = self.base_dir / "latest.txt"
                with open(latest_file, 'w') as f:
                    f.write(str(date_dir))
            else:
                latest_link.symlink_to(relative_target, target_is_directory=True)

        except Exception as e:
            logger.warning(f"Could not create latest link: {e}")

    def get_latest_dir(self) -> Optional[Path]:
        """Get the path to the most recent extraction date folder."""
        latest_file = self.base_dir / "latest.txt"
        if latest_file.exists():
            with open(latest_file, 'r') as f:
                return Path(f.read().strip())

        latest_link = self.base_dir / "latest"
        if latest_link.exists():
            return latest_link.resolve()

        # Fallback: find most recent date folder
        date_folders = [
            d for d in self.base_dir.iterdir()
            if d.is_dir() and d.name not in ['latest', 'summary']
        ]
        if date_folders:
            return max(date_folders, key=lambda d: d.name)

        return None

    def get_all_extractions(self, date: Optional[str] = None) -> list:
        """
        Get all extraction folders, optionally filtered by date.

        Args:
            date: Optional date string (YYYY-MM-DD) to filter by

        Returns:
            List of extraction folder paths
        """
        extractions = []

        if date:
            date_dir = self.base_dir / date
            if date_dir.exists():
                for item in date_dir.iterdir():
                    if item.is_dir() and item.name != 'summary':
                        extractions.append(item)
        else:
            # Get all extractions from all dates
            for date_folder in self.base_dir.iterdir():
                if date_folder.is_dir() and date_folder.name not in ['latest', 'summary']:
                    for item in date_folder.iterdir():
                        if item.is_dir() and item.name != 'summary':
                            extractions.append(item)

        return sorted(extractions, key=lambda x: str(x), reverse=True)

    def save_extraction_metadata(
        self,
        paths: ExtractionPaths,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save extraction metadata to the audit folder.

        Args:
            paths: ExtractionPaths object
            metadata: Metadata dictionary to save

        Returns:
            Path to saved metadata file
        """
        metadata_file = Path(paths.audit_dir) / "extraction_metadata.json"

        # Add timestamps
        metadata['saved_at'] = datetime.now().isoformat()
        metadata['paths'] = paths.to_dict()

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"Saved extraction metadata to: {metadata_file}")
        return str(metadata_file)


def get_output_manager(base_dir: str = None) -> OutputManager:
    """
    Get or create the global output manager instance.

    Args:
        base_dir: Base output directory (default: ./output)

    Returns:
        OutputManager instance
    """
    if base_dir is None:
        # Default to 'output' folder in project root
        project_root = Path(__file__).parent.parent
        base_dir = str(project_root / "output")

    return OutputManager(base_dir)


# Convenience function for quick path creation
def create_output_paths(
    vendor: str,
    client: str,
    source_file: Optional[str] = None,
    base_dir: str = None
) -> ExtractionPaths:
    """
    Quick function to create extraction output paths.

    Args:
        vendor: Vendor name
        client: Client name
        source_file: Optional source file to copy
        base_dir: Optional base output directory

    Returns:
        ExtractionPaths object
    """
    manager = get_output_manager(base_dir)
    return manager.create_extraction_folder(vendor, client, source_file)
