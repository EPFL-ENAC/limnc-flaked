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
        self.scheduler.start()
        for instrument in config_service.get_config().instruments:
            self.add_job(instrument.name)
        self.status = "running"

    def stop(self):
        if self.status != "stopped":
            self.scheduler.shutdown()
            self.status = "stopped"

    def pause(self):
        if self.status == "running":
            self.scheduler.pause()
            self.status = "paused"

    def resume(self):
        if self.status == "paused":
            self.scheduler.resume()
            self.status = "running"

    def has_job(self, job_id: str):
        return self.scheduler.get_job(job_id) is not None

    def stop_job(self, job_id: str):
        self.scheduler.remove_job(job_id)

    def pause_job(self, job_id: str):
        self.scheduler.pause_job(job_id)

    def resume_job(self, job_id: str):
        self.scheduler.resume_job(job_id)

    def start_job(self, job_id: str):
        if self.scheduler.get_job(job_id) is None:
            self.add_job(job_id)
        self.scheduler.resume_job(job_id)

    def get_status(self):
        return self.status

    def add_job(self, job_id: str):
        instrument = config_service.get_instrument_config(job_id)
        if instrument is None:
            return
        trigger = None
        if instrument.schedule.interval:
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
        elif instrument.schedule.cron:
            trigger = CronTrigger.from_crontab(instrument.schedule.cron)
        if trigger:
            self.scheduler.add_job(
                process_data, trigger, id=instrument.name, kwargs={"job_id": instrument.name}, replace_existing=True)

    def job_to_dict(self, job) -> dict:
        job_dict = {
            'id': job.id,
            'name': job.name,
            'trigger': {},
            'next_run_time': str(job.next_run_time),
            'func': job.func.__name__,
            'args': job.args,
            'kwargs': job.kwargs,
            'misfire_grace_time': job.misfire_grace_time,
            'coalesce': job.coalesce,
            'max_instances': job.max_instances
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

    def get_jobs(self) -> list:
        jobs = self.scheduler.get_jobs()
        return [self.job_to_dict(job) for job in jobs]

    def get_job(self, job_id: str) -> dict:
        job = self.scheduler.get_job(job_id)
        if job:
            return self.job_to_dict(job)
        return None


scheduler_service = SchedulerService()
