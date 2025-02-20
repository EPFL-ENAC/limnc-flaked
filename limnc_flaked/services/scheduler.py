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
      self.scheduler.add_job(process_data, 'interval', minutes=1)  # Run every minute
      self.scheduler.start()
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
    

scheduler_service = SchedulerService()
