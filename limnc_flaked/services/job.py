from .config import config_service
from tenacity import retry, stop_after_attempt, wait_fixed
import logging


class JobProcessor:

    def __init__(self, job_id: str):
        self.job_id = job_id

    def process(self):
        try:
            print(f"Processing data for job {self.job_id}")
            self.config = config_service.get_config()
            self.instrument = config_service.get_instrument_config(self.job_id)

            input_files = self.read_input_files()
            uploaded_files = self.upload_files(input_files)
            self.move_files(uploaded_files)

            print("Pipeline finished successfully.")
        except Exception as e:
            logging.error("Pipeline failed", exc_info=True)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def read_input_files(self):
        print(f"Step 1: Extracting files from {self.instrument.input.path}...")
        return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def upload_files(self, files):
        print(
            f"Step 2: Uploading {len(files)} data file to {self.config.general.sftp.username}@{self.config.general.sftp.host}:{self.instrument.output.path}...")
        return files

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def move_files(self, files):
        print(f"Step 3: Moving data file to {self.instrument.output.path}...")
        return files
