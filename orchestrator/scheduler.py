"""
Scheduler Module

Handles automated scheduling of pipeline runs using cron-like syntax.
"""

import os
import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Thread, Event

try:
    import schedule
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False

from dotenv import load_dotenv

# Local imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.pipeline import Pipeline, PipelineResult


logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


@dataclass
class JobConfig:
    """Configuration for a scheduled job."""
    name: str
    input_dir: str
    output_dir: str
    schedule: str  # e.g., "daily", "hourly", "*/5 * * * *"
    vendor: Optional[str] = None
    template_path: Optional[str] = None
    term: str = '5_year'
    use_llm: bool = True
    enabled: bool = True
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobResult:
    """Result of a scheduled job execution."""
    job_name: str
    start_time: datetime
    end_time: datetime
    success: bool
    output_file: Optional[str]
    documents_processed: int
    errors: List[str]
    warnings: List[str]


class Scheduler:
    """
    Job scheduler for automated pipeline execution.

    Features:
    - Cron-like scheduling
    - Job history tracking
    - Error notifications
    - Configurable retry logic
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        history_path: Optional[str] = './data/job_history.json'
    ):
        """
        Initialize scheduler.

        Args:
            config_path: Path to jobs configuration file
            history_path: Path to job history file
        """
        if not HAS_SCHEDULE:
            raise ImportError("schedule package required for scheduling")

        self.jobs: Dict[str, JobConfig] = {}
        self.history: List[JobResult] = []
        self.history_path = Path(history_path) if history_path else None

        self._stop_event = Event()
        self._runner_thread: Optional[Thread] = None

        # Load configuration
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

        # Load history
        if self.history_path and self.history_path.exists():
            self._load_history()

    def _load_config(self, config_path: str):
        """Load jobs from configuration file."""
        with open(config_path) as f:
            config = json.load(f)

        for job_data in config.get('jobs', []):
            job = JobConfig(**job_data)
            self.jobs[job.name] = job

    def _load_history(self):
        """Load job history from file."""
        try:
            with open(self.history_path) as f:
                data = json.load(f)
                # Convert to JobResult objects
                for item in data:
                    item['start_time'] = datetime.fromisoformat(item['start_time'])
                    item['end_time'] = datetime.fromisoformat(item['end_time'])
                    self.history.append(JobResult(**item))
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")

    def _save_history(self):
        """Save job history to file."""
        if not self.history_path:
            return

        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        data = []
        for result in self.history[-100:]:  # Keep last 100
            data.append({
                'job_name': result.job_name,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat(),
                'success': result.success,
                'output_file': result.output_file,
                'documents_processed': result.documents_processed,
                'errors': result.errors,
                'warnings': result.warnings
            })

        with open(self.history_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_job(self, config: JobConfig):
        """
        Add a job to the scheduler.

        Args:
            config: Job configuration
        """
        self.jobs[config.name] = config
        self._schedule_job(config)
        logger.info(f"Added job: {config.name} ({config.schedule})")

    def remove_job(self, name: str):
        """
        Remove a job from the scheduler.

        Args:
            name: Job name
        """
        if name in self.jobs:
            del self.jobs[name]
            # Note: schedule library doesn't support removing specific jobs easily
            # Would need to clear and re-add all jobs
            logger.info(f"Removed job: {name}")

    def _schedule_job(self, config: JobConfig):
        """Schedule a job based on its configuration."""
        if not config.enabled:
            return

        job_func = lambda c=config: self._run_job(c)

        # Parse schedule string
        sched = config.schedule.lower()

        if sched == 'hourly':
            schedule.every().hour.do(job_func)
        elif sched == 'daily':
            schedule.every().day.at("00:00").do(job_func)
        elif sched == 'weekly':
            schedule.every().monday.at("00:00").do(job_func)
        elif sched.startswith('every'):
            # Parse "every X minutes/hours"
            parts = sched.split()
            if len(parts) >= 3:
                interval = int(parts[1])
                unit = parts[2]
                if 'minute' in unit:
                    schedule.every(interval).minutes.do(job_func)
                elif 'hour' in unit:
                    schedule.every(interval).hours.do(job_func)
        else:
            # Assume cron-like format - run daily for now
            # Full cron parsing would require additional library
            schedule.every().day.at("00:00").do(job_func)
            logger.warning(f"Cron format '{sched}' simplified to daily")

    def _run_job(self, config: JobConfig) -> JobResult:
        """
        Execute a scheduled job.

        Args:
            config: Job configuration

        Returns:
            JobResult with execution details
        """
        start_time = datetime.now()
        logger.info(f"Starting job: {config.name}")

        try:
            # Create and run pipeline
            pipeline = Pipeline(
                input_dir=config.input_dir,
                output_dir=config.output_dir,
                template_path=config.template_path,
                use_llm=config.use_llm
            )

            result = pipeline.run(
                vendor=config.vendor,
                term=config.term
            )

            # Create job result
            job_result = JobResult(
                job_name=config.name,
                start_time=start_time,
                end_time=datetime.now(),
                success=result.success,
                output_file=result.output_file,
                documents_processed=result.processed_documents,
                errors=result.errors,
                warnings=result.warnings
            )

            # Update job status
            config.last_run = start_time
            config.last_status = 'success' if result.success else 'failed'

        except Exception as e:
            logger.error(f"Job {config.name} failed: {e}")

            job_result = JobResult(
                job_name=config.name,
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                output_file=None,
                documents_processed=0,
                errors=[str(e)],
                warnings=[]
            )

            config.last_run = start_time
            config.last_status = 'error'

        # Save to history
        self.history.append(job_result)
        self._save_history()

        # Send notification if configured
        self._notify(job_result)

        logger.info(
            f"Job {config.name} completed: "
            f"{'success' if job_result.success else 'failed'}"
        )

        return job_result

    def _notify(self, result: JobResult):
        """Send notification for job completion."""
        # Placeholder for notification logic
        # Could integrate with email, Slack, webhooks, etc.

        if not result.success:
            logger.warning(
                f"Job {result.job_name} failed with errors: {result.errors}"
            )

    def run_now(self, job_name: str) -> Optional[JobResult]:
        """
        Run a job immediately.

        Args:
            job_name: Name of job to run

        Returns:
            JobResult or None if job not found
        """
        if job_name not in self.jobs:
            logger.error(f"Job not found: {job_name}")
            return None

        return self._run_job(self.jobs[job_name])

    def start(self, blocking: bool = False):
        """
        Start the scheduler.

        Args:
            blocking: Whether to block the main thread
        """
        logger.info("Starting scheduler")

        # Schedule all jobs
        for config in self.jobs.values():
            self._schedule_job(config)

        if blocking:
            self._run_scheduler()
        else:
            self._stop_event.clear()
            self._runner_thread = Thread(target=self._run_scheduler)
            self._runner_thread.daemon = True
            self._runner_thread.start()

    def _run_scheduler(self):
        """Run the schedule loop."""
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler")
        self._stop_event.set()
        if self._runner_thread:
            self._runner_thread.join(timeout=5)

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            'running': self._runner_thread and self._runner_thread.is_alive(),
            'jobs': [
                {
                    'name': job.name,
                    'schedule': job.schedule,
                    'enabled': job.enabled,
                    'last_run': job.last_run.isoformat() if job.last_run else None,
                    'last_status': job.last_status
                }
                for job in self.jobs.values()
            ],
            'pending_jobs': len(schedule.jobs),
            'history_count': len(self.history)
        }

    def get_history(
        self,
        job_name: Optional[str] = None,
        limit: int = 10
    ) -> List[JobResult]:
        """
        Get job execution history.

        Args:
            job_name: Filter by job name
            limit: Maximum results to return

        Returns:
            List of JobResult objects
        """
        results = self.history

        if job_name:
            results = [r for r in results if r.job_name == job_name]

        return results[-limit:]


def schedule_job(
    name: str,
    input_dir: str,
    output_dir: str,
    schedule_time: str,
    **kwargs
) -> JobConfig:
    """
    Convenience function to create a job configuration.

    Args:
        name: Job name
        input_dir: Input directory
        output_dir: Output directory
        schedule_time: Schedule string
        **kwargs: Additional JobConfig parameters

    Returns:
        JobConfig object
    """
    return JobConfig(
        name=name,
        input_dir=input_dir,
        output_dir=output_dir,
        schedule=schedule_time,
        **kwargs
    )


def create_cron_config(jobs: List[JobConfig], output_path: str):
    """
    Create a crontab-compatible configuration file.

    Args:
        jobs: List of job configurations
        output_path: Output file path
    """
    lines = [
        "# TCO Automation Cron Jobs",
        "# Generated by scheduler.py",
        ""
    ]

    for job in jobs:
        # Convert schedule to cron format (simplified)
        sched = job.schedule.lower()
        if sched == 'hourly':
            cron = "0 * * * *"
        elif sched == 'daily':
            cron = "0 0 * * *"
        elif sched == 'weekly':
            cron = "0 0 * * 1"
        else:
            cron = "0 0 * * *"  # Default to daily

        cmd = (
            f"cd /path/to/tco_automation && "
            f"python -m orchestrator.pipeline {job.input_dir} "
            f"-o {job.output_dir}"
        )

        if job.vendor:
            cmd += f" -v {job.vendor}"
        if job.template_path:
            cmd += f" -t {job.template_path}"

        lines.append(f"# {job.name}")
        lines.append(f"{cron} {cmd}")
        lines.append("")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='TCO Automation Scheduler')
    parser.add_argument('--config', '-c', help='Jobs configuration file')
    parser.add_argument('--run', '-r', help='Run a specific job now')
    parser.add_argument('--list', '-l', action='store_true', help='List all jobs')
    parser.add_argument('--start', '-s', action='store_true', help='Start scheduler')

    args = parser.parse_args()

    scheduler = Scheduler(config_path=args.config)

    if args.list:
        status = scheduler.get_status()
        print("Scheduler Status:")
        print(f"  Jobs: {len(status['jobs'])}")
        for job in status['jobs']:
            print(f"    - {job['name']}: {job['schedule']} "
                  f"({'enabled' if job['enabled'] else 'disabled'})")

    elif args.run:
        result = scheduler.run_now(args.run)
        if result:
            print(f"Job {result.job_name}: "
                  f"{'success' if result.success else 'failed'}")
            print(f"  Documents: {result.documents_processed}")
            if result.output_file:
                print(f"  Output: {result.output_file}")

    elif args.start:
        print("Starting scheduler (Ctrl+C to stop)")
        try:
            scheduler.start(blocking=True)
        except KeyboardInterrupt:
            scheduler.stop()
            print("\nScheduler stopped")

    else:
        # Demo mode - create sample job
        job = schedule_job(
            name='daily_fis_processing',
            input_dir='./data/raw/fis',
            output_dir='./data/output',
            schedule_time='daily',
            vendor='FIS',
            term='5_year'
        )

        scheduler.add_job(job)
        print(f"Created demo job: {job.name}")
        print("Run with --start to begin scheduling")
