from apscheduler.schedulers.background import BackgroundScheduler
from tenacity import retry, stop_after_attempt, wait_fixed
import time
import logging


# Define the pipeline
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def process_data():
    try:
        print("Step 1: Extracting data...")
        time.sleep(1)  # Simulate work
        print("Step 2: Transforming data...")
        time.sleep(1)
        # Simulate an error
        if time.time() % 2 < 1:  
            raise ValueError("Random simulated error!")
        print("Step 3: Loading data...")
        time.sleep(1)
        print("Pipeline finished successfully.")
    except Exception as e:
        logging.error("Pipeline failed", exc_info=True)
        raise


class SchedulerService:
  
  def __init__(self):
      self.status = "stopped"
      self.scheduler = BackgroundScheduler()

  # Schedule the pipeline
  def start(self):
      self.scheduler.start()
      self.scheduler.add_job(process_data, 'interval', minutes=1, id="1", replace_existing=True)  # Run every minute
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
  
  def get_status(self):
      return self.status

  def job_to_dict(self, job):
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
        job_dict['trigger']['cron'] = {f.name: str(f) for f in trigger.fields}
    if hasattr(trigger, 'run_date'):  # For date triggers
        job_dict['trigger']['date'] = str(trigger.run_date)
    return job_dict

  def get_jobs(self):
      jobs = self.scheduler.get_jobs()
      return [self.job_to_dict(job) for job in jobs]
    

scheduler_service = SchedulerService()
