"""
Bulk Upload Handler for TCO Automation
Handles multiple file uploads with progress tracking and batch processing.
"""

import json
import os
import shutil
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class UploadStatus(Enum):
    """Status of an individual upload."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(Enum):
    """Status of the overall upload job."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class UploadFile:
    """Represents a single uploaded file."""
    id: str
    filename: str
    original_filename: str
    size: int
    status: UploadStatus = UploadStatus.PENDING
    vendor: Optional[str] = None
    client: Optional[str] = None
    progress: int = 0
    message: str = ""
    result: Optional[Dict] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        return data


@dataclass
class UploadJob:
    """Represents a batch upload job."""
    id: str
    created_at: str
    status: JobStatus = JobStatus.QUEUED
    files: List[UploadFile] = field(default_factory=list)
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    progress: int = 0
    message: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        data = {
            'id': self.id,
            'created_at': self.created_at,
            'status': self.status.value,
            'files': [f.to_dict() for f in self.files],
            'total_files': self.total_files,
            'completed_files': self.completed_files,
            'failed_files': self.failed_files,
            'progress': self.progress,
            'message': self.message,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
        }
        return data


class BulkUploadManager:
    """Manages bulk file uploads and processing."""

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.docx', '.xlsx', '.pdf', '.doc', '.xls'}

    # Vendor detection patterns
    VENDOR_PATTERNS = {
        'FIS': ['fis', 'horizon', 'digital one', 'payments one'],
        'JACK_HENRY': ['jack henry', 'jh', 'silverlake', 'banno', 'symitar'],
        'CSI': ['csi', 'nupoint'],
        'FISERV': ['fiserv', 'dna', 'premier', 'signature'],
        'FINASTRA': ['finastra', 'fusion'],
    }

    def __init__(self, upload_dir: str = None, output_dir: str = None):
        """Initialize the upload manager."""
        base_dir = Path(__file__).parent.parent

        self.upload_dir = Path(upload_dir) if upload_dir else base_dir / "uploads"
        self.output_dir = Path(output_dir) if output_dir else base_dir / "Extracted JSON"

        # Create directories if needed
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Active jobs (in production, use Redis/database)
        self.jobs: Dict[str, UploadJob] = {}

        # Processing thread
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_processing = False

    def create_job(self) -> UploadJob:
        """Create a new upload job."""
        job_id = str(uuid.uuid4())[:8]
        job = UploadJob(
            id=job_id,
            created_at=datetime.now().isoformat()
        )
        self.jobs[job_id] = job
        return job

    def add_file_to_job(
        self,
        job_id: str,
        file_data: bytes,
        filename: str
    ) -> Optional[UploadFile]:
        """Add a file to an existing job."""
        job = self.jobs.get(job_id)
        if not job:
            return None

        # Validate extension
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return None

        # Generate unique filename
        file_id = str(uuid.uuid4())[:8]
        safe_filename = f"{file_id}_{filename}"
        file_path = self.upload_dir / job_id / safe_filename

        # Create job directory
        (self.upload_dir / job_id).mkdir(parents=True, exist_ok=True)

        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)

        # Detect vendor from filename
        vendor = self._detect_vendor(filename)

        # Create upload file record
        upload_file = UploadFile(
            id=file_id,
            filename=safe_filename,
            original_filename=filename,
            size=len(file_data),
            vendor=vendor,
            status=UploadStatus.PENDING
        )

        job.files.append(upload_file)
        job.total_files = len(job.files)

        return upload_file

    def _detect_vendor(self, filename: str) -> Optional[str]:
        """Detect vendor from filename."""
        filename_lower = filename.lower()

        for vendor, patterns in self.VENDOR_PATTERNS.items():
            for pattern in patterns:
                if pattern in filename_lower:
                    return vendor

        return None

    def _detect_client(self, filename: str) -> Optional[str]:
        """Try to extract client name from filename."""
        # Remove extension
        name = Path(filename).stem

        # Remove common patterns
        name = name.lower()
        for vendor_patterns in self.VENDOR_PATTERNS.values():
            for pattern in vendor_patterns:
                name = name.replace(pattern, '')

        # Remove common suffixes
        for suffix in ['_proposal', '_pricing', '_quote', '_2024', '_2025', '_2026']:
            name = name.replace(suffix, '')

        # Clean up
        name = name.strip('_- ')

        if name:
            return name.replace('_', ' ').title()

        return None

    def start_processing(self, job_id: str, callback=None):
        """Start processing a job in background."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status == JobStatus.RUNNING:
            return False

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now().isoformat()
        job.message = "Processing started"

        # Start background thread
        self._processing_thread = threading.Thread(
            target=self._process_job,
            args=(job_id, callback)
        )
        self._processing_thread.start()

        return True

    def _process_job(self, job_id: str, callback=None):
        """Process all files in a job (runs in background thread)."""
        job = self.jobs.get(job_id)
        if not job:
            return

        try:
            for i, upload_file in enumerate(job.files):
                if self._stop_processing:
                    job.status = JobStatus.CANCELLED
                    break

                # Update progress
                upload_file.status = UploadStatus.PROCESSING
                upload_file.started_at = datetime.now().isoformat()
                job.message = f"Processing {upload_file.original_filename}"

                try:
                    # Process the file
                    result = self._process_file(job_id, upload_file)

                    if result:
                        upload_file.status = UploadStatus.COMPLETED
                        upload_file.result = result
                        job.completed_files += 1
                    else:
                        upload_file.status = UploadStatus.FAILED
                        upload_file.error = "Extraction failed"
                        job.failed_files += 1

                except Exception as e:
                    logger.error(f"Error processing {upload_file.filename}: {e}")
                    upload_file.status = UploadStatus.FAILED
                    upload_file.error = str(e)
                    job.failed_files += 1

                finally:
                    upload_file.completed_at = datetime.now().isoformat()
                    upload_file.progress = 100

                # Update job progress
                job.progress = int((i + 1) / job.total_files * 100)

                if callback:
                    callback(job)

            # Mark job complete
            if not self._stop_processing:
                job.status = JobStatus.COMPLETED if job.failed_files == 0 else JobStatus.FAILED
                job.completed_at = datetime.now().isoformat()
                job.message = f"Completed: {job.completed_files} succeeded, {job.failed_files} failed"

        except Exception as e:
            logger.error(f"Job processing error: {e}")
            job.status = JobStatus.FAILED
            job.message = str(e)

    def _process_file(self, job_id: str, upload_file: UploadFile) -> Optional[Dict]:
        """Process a single file through the extraction pipeline."""
        file_path = self.upload_dir / job_id / upload_file.filename

        if not file_path.exists():
            return None

        # Try to import and use the extraction pipeline
        try:
            # Attempt to use existing extraction infrastructure
            from extraction.ai_pipeline import AIPipeline

            pipeline = AIPipeline()
            result = pipeline.process_document(str(file_path))

            if result:
                # Save to Extracted JSON folder
                client_name = upload_file.client or self._detect_client(upload_file.original_filename) or "unknown"
                vendor = upload_file.vendor or "unknown"

                output_filename = f"{client_name.lower().replace(' ', '_')}_{vendor.lower()}_extraction_ai.json"
                output_path = self.output_dir / output_filename

                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)

                return {
                    'output_file': str(output_path),
                    'line_items': len(result.get('line_items', [])),
                    'confidence': result.get('overall_confidence', 0)
                }

        except ImportError:
            logger.warning("AIPipeline not available, using mock extraction")

        # Mock extraction for demo purposes
        return self._mock_extract(file_path, upload_file)

    def _mock_extract(self, file_path: Path, upload_file: UploadFile) -> Dict:
        """Mock extraction for demo when full pipeline isn't available."""
        # Simulate processing time
        time.sleep(1)

        client_name = upload_file.client or self._detect_client(upload_file.original_filename) or "Unknown Client"
        vendor = upload_file.vendor or "UNKNOWN"

        # Create mock result
        result = {
            'vendor': vendor,
            'client': client_name,
            'document_date': datetime.now().strftime('%B %Y'),
            'contract_term': 7,
            'line_items': [],
            'overall_confidence': 0.85,
            'extraction_method': 'mock',
            'source_file': upload_file.original_filename
        }

        # Save result
        output_filename = f"{client_name.lower().replace(' ', '_')}_{vendor.lower()}_extraction_ai.json"
        output_path = self.output_dir / output_filename

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        return {
            'output_file': str(output_path),
            'line_items': 0,
            'confidence': 0.85,
            'mock': True
        }

    def get_job(self, job_id: str) -> Optional[UploadJob]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status as dictionary."""
        job = self.jobs.get(job_id)
        if job:
            return job.to_dict()
        return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status == JobStatus.RUNNING:
            self._stop_processing = True
            job.status = JobStatus.CANCELLED
            job.message = "Cancelled by user"
            return True

        return False

    def cleanup_job(self, job_id: str) -> bool:
        """Clean up job files and remove from memory."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        # Remove upload directory
        job_dir = self.upload_dir / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir)

        # Remove from jobs dict
        del self.jobs[job_id]

        return True

    def get_all_jobs(self) -> List[Dict]:
        """Get all jobs."""
        return [job.to_dict() for job in self.jobs.values()]


# Global instance
_upload_manager: Optional[BulkUploadManager] = None


def get_upload_manager() -> BulkUploadManager:
    """Get or create the global upload manager instance."""
    global _upload_manager
    if _upload_manager is None:
        _upload_manager = BulkUploadManager()
    return _upload_manager
