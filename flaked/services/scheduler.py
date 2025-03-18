from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .config import config_service
from .job import JobProcessor


def process_data(job_id: str = None):
    """Launch the job processor

    Args:
        job_id (str): The job id is the instrument name
    """
    if job_id:
        processor = JobProcessor(job_id)
        processor.process()


class SchedulerService:

    def __init__(self):
        self.status = "stopped"
        self.scheduler = BackgroundScheduler()
        self.start()

    # Schedule the pipeline
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        for instrument in config_service.get_config().instruments:
            self.add_job(instrument.name)
        self.status = "running"

    def stop(self):
        """Stop the scheduler"""
        if self.status != "stopped":
            self.scheduler.shutdown()
            self.scheduler = BackgroundScheduler()  # Reset the scheduler
            self.status = "stopped"

    def pause(self):
        """Pause the scheduler"""
        if self.status == "running":
            self.scheduler.pause()
            self.status = "paused"

    def resume(self):
        """Resume the scheduler"""
        if self.status == "paused":
            self.scheduler.resume()
            self.status = "running"

    def has_job(self, job_id: str):
        """Check if the job exists

        Args:
            job_id (str): The job id
        """
        return self.scheduler.get_job(job_id) is not None

    def stop_job(self, job_id: str):
        """Stop the job (removes it)

        Args:
            job_id (str): The job id
        """
        self.scheduler.remove_job(job_id)

    def pause_job(self, job_id: str):
        """Pause the job

        Args:
            job_id (str): The job id
        """
        self.scheduler.pause_job(job_id)

    def resume_job(self, job_id: str):
        """Resume the job

        Args:
            job_id (str): The job id
        """
        self.scheduler.resume_job(job_id)

    def start_job(self, job_id: str):
        """Start the job (ensure it exists first)

        Args:
            job_id (str): The job id
        """
        if self.scheduler.get_job(job_id) is None:
            self.add_job(job_id)
        self.scheduler.resume_job(job_id)

    def run_job(self, job_id: str):
        """Run the job immediately (ensure it exists first)

        Args:
            job_id (str): The job id
        """
        if self.scheduler.get_job(job_id) is None:
            self.add_job(job_id)
        process_data(job_id)

    def get_status(self) -> str:
        """Get the status of the scheduler

        Returns:
            str: The status
        """
        return self.status

    def add_job(self, name_or_id: str):
        """Add the instrument job(s) to the scheduler.

        If a job id is provided, only this job will be added to the scheduler, as soon as there is an instrument trigger configuration for it.
        If an instrument name is provided, all jobs for this instrument will be added to the scheduler.

        Args:
            name_or_id (str): Name of the intrument or job id in the format "<instrumentname>:<interval|cron>"
        """
        instrument = config_service.get_instrument_config(
            self.get_instrument_name(name_or_id))
        if instrument is None:
            return
        trigger = None
        if instrument.schedule.interval and not name_or_id.endswith(":cron"):
            if instrument.schedule.interval.unit == "minutes":
                trigger = IntervalTrigger(
                    minutes=instrument.schedule.interval.value)
            if instrument.schedule.interval.unit == "hours":
                trigger = IntervalTrigger(
                    hours=instrument.schedule.interval.value)
            if instrument.schedule.interval.unit == "days":
                trigger = IntervalTrigger(
                    days=instrument.schedule.interval.value)
            if instrument.schedule.interval.unit == "weeks":
                trigger = IntervalTrigger(
                    weeks=instrument.schedule.interval.value)
            if trigger:
                job_id = f"{instrument.name}:interval"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
                self.scheduler.add_job(
                    process_data, trigger, id=job_id, name=instrument.name, kwargs={"job_id": instrument.name}, replace_existing=True)

        if instrument.schedule.cron and not name_or_id.endswith(":interval"):
            trigger = CronTrigger.from_crontab(instrument.schedule.cron)
            job_id = f"{instrument.name}:cron"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            self.scheduler.add_job(
                process_data, trigger, id=job_id, name=instrument.name, kwargs={"job_id": instrument.name}, replace_existing=True)

    def get_jobs(self, name: str = None) -> list:
        """Get the list of jobs registered in the scheduler

        Args:
            name (str): The name of the instrument to filter the jobs

        Returns:
            list: The job list
        """
        jobs = self.scheduler.get_jobs()
        return [self._job_to_dict(job) for job in jobs if name is None or job.name == name]

    def get_job(self, job_id: str) -> dict:
        """Get a specific job description

        Args:
            job_id (str): The job id

        Returns:
            dict: The job description
        """
        job = self.scheduler.get_job(job_id)
        if job:
            return self._job_to_dict(job)
        return None

    def get_instrument_name(self, job_id: str) -> str:
        """Extract instrument name from job id

        Args:
            job_id (str): The name or job id

        Returns:
            str: The instrument name
        """
        return job_id.split(':')[0]

    def _job_to_dict(self, job) -> dict:
        """Convert the job to a dictionary

        Args:
            job (_type_): The job object as provided by the scheduler

        Returns:
            dict: The job dictionary
        """
        job_dict = {
            'id': job.id,
            'name': job.name,
            'trigger': {},
            'next_run_time': str(job.next_run_time),
            # 'func': job.func.__name__,
            # 'args': job.args,
            # 'kwargs': job.kwargs,
            # 'misfire_grace_time': job.misfire_grace_time,
            # 'coalesce': job.coalesce,
            # 'max_instances': job.max_instances
        }

        # Add trigger-specific details
        trigger = job.trigger
        if hasattr(trigger, 'interval'):
            job_dict['trigger']['interval'] = trigger.interval.total_seconds()
        if hasattr(trigger, 'fields'):  # For cron triggers
            job_dict['trigger']['cron'] = {
                f.name: str(f) for f in trigger.fields}
        if hasattr(trigger, 'run_date'):  # For date triggers
            job_dict['trigger']['date'] = str(trigger.run_date)
        return job_dict


scheduler_service = SchedulerService()
