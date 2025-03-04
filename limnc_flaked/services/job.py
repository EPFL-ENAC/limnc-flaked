from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from pathlib import Path
import os
import re
from .config import config_service
from .upload import UploadService


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

        # Get folder path
        source = self._to_absolute_path(self.instrument.input.path)
        if not source.exists():
            print(f"Source folder {source} does not exist")
            return []
        if not source.is_dir():
            print(f"Source folder {source} is not a directory")
            return []

        # Define regex pattern (e.g., match .log files starting with "error")
        pattern = re.compile(
            self.instrument.input.filter.regex) if self.instrument.input.filter else re.compile('.*')

        # Get filtered and sorted files
        files = sorted(
            [f for f in source.iterdir() if f.is_file()
             and pattern.match(f.name)],
            key=lambda f: f.stat().st_mtime,  # Sort by last modification time
            reverse=True  # Newest files first
        )

        # Skip files if needed
        if self.instrument.input.filter and self.instrument.input.filter.skip > 0:
            files = files[self.instrument.input.filter.skip:]

        return files

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def upload_files(self, files):
        print(
            f"Step 2: Uploading {len(files)} data file to {self.config.general.sftp.username}@{self.config.general.sftp.host}:{self.instrument.output.path}...")
        if len(files) == 0:
            print("No files to upload")
            return []

        # Upload files
        upload_service = UploadService()
        uploaded = upload_service.upload_files(
            files, self.instrument.name)
        return uploaded

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def move_files(self, files):
        print(f"Step 3: Moving data file to {self.instrument.output.path}...")
        destination = self._to_absolute_path(self.instrument.output.path)
        if destination.exists() and not destination.is_dir():
            print(f"Destination {destination} is not a directory")
            return

        if not destination.exists():
            destination.mkdir(parents=True)
        if len(files) == 0:
            print("No files to move")
            return []
        for file in files:
            file.rename(destination / file.name)

    def _to_absolute_path(self, file: str) -> Path:
        path = Path(file)
        if path.is_absolute():
            return path
        return Path(self.config.general.work if self.config.general.work else os.getcwd()) / file
