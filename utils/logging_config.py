"""
Logging Configuration

Centralized logging setup for TCO Automation.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


def setup_logging(
    level: int = logging.INFO,
    log_file: str = None,
    log_dir: str = './logs',
    format_string: str = None,
    console: bool = True
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Logging level (default: INFO)
        log_file: Specific log file path (optional)
        log_dir: Directory for log files (default: ./logs)
        format_string: Custom format string (optional)
        console: Whether to log to console (default: True)

    Returns:
        Root logger
    """
    # Default format
    if not format_string:
        format_string = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

    # Create formatter
    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers = []

    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file or log_dir:
        # Create log directory
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)

        # Generate log filename if not specified
        if not log_file:
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file = os.path.join(log_dir, f'tco_automation_{timestamp}.log')

        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class PipelineLogger:
    """
    Specialized logger for pipeline stages.

    Provides structured logging with stage context.
    """

    def __init__(self, pipeline_name: str = 'pipeline'):
        self.logger = logging.getLogger(pipeline_name)
        self.current_stage = None
        self.stage_start_time = None

    def start_stage(self, stage_name: str):
        """Log start of a pipeline stage."""
        import time
        self.current_stage = stage_name
        self.stage_start_time = time.time()
        self.logger.info(f"[{stage_name}] Starting...")

    def end_stage(self, stage_name: str = None, success: bool = True):
        """Log end of a pipeline stage."""
        import time
        stage = stage_name or self.current_stage
        duration = time.time() - self.stage_start_time if self.stage_start_time else 0
        status = "completed" if success else "failed"
        self.logger.info(f"[{stage}] {status.upper()} ({duration:.2f}s)")

    def stage_info(self, message: str):
        """Log info within current stage."""
        if self.current_stage:
            self.logger.info(f"[{self.current_stage}] {message}")
        else:
            self.logger.info(message)

    def stage_warning(self, message: str):
        """Log warning within current stage."""
        if self.current_stage:
            self.logger.warning(f"[{self.current_stage}] {message}")
        else:
            self.logger.warning(message)

    def stage_error(self, message: str):
        """Log error within current stage."""
        if self.current_stage:
            self.logger.error(f"[{self.current_stage}] {message}")
        else:
            self.logger.error(message)


# Convenience function for quick setup
def quick_setup(verbose: bool = False):
    """
    Quick logging setup for scripts.

    Args:
        verbose: Enable debug logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    setup_logging(level=level, log_dir=None)
