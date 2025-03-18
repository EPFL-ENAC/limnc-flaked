from tenacity import retry, stop_after_attempt, wait_fixed
from typing import List
import logging
import subprocess
from pathlib import Path
import os
import re
from .config import config_service
from .log import log_service
from .upload import UploadService


class JobProcessor:

    def __init__(self, job_id: str):
        self.job_id = job_id

    def process(self):
        try:
            logging.info(f"Processing data for job {self.job_id}")
            self.config = config_service.get_config()
            self.instrument = config_service.get_instrument_config(self.job_id)
            self.logger = log_service.for_instrument(self.instrument)
            self.logger.debug(f"PROCESS_START;{self.job_id}")

            if self.instrument.preprocess:
                self.pre_process()

            input_files = self.read_input_files()
            if len(input_files) > 0:
                uploaded_files = self.upload_files(input_files)
                if len(uploaded_files) > 0:
                    self.move_files(uploaded_files)

            if self.instrument.postprocess:
                self.post_process()

            self.logger.debug("PROCESS_SUCCESS")
        except Exception as e:
            if self.logger:
                self.logger.debug("PROCESS_FAILURE")
            logging.error("Pipeline failed", exc_info=True)
            raise

    def pre_process(self):
        if not self.instrument.preprocess:
            return
        args = [self.instrument.preprocess.command]
        if self.instrument.preprocess.args:
            args.extend(self.instrument.preprocess.args)
        self.logger.info(
            f"PRE_PROCESS;Executing command: {' '.join(args)}")
        process = subprocess.Popen(args, shell=True)
        process.wait()
        self.logger.info(
            f"PRE_PROCESS;Command executed with return code: {process.returncode}")

    def post_process(self):
        if not self.instrument.postprocess:
            return
        args = [self.instrument.postprocess.command]
        if self.instrument.postprocess.args:
            args.extend(self.instrument.postprocess.args)
        self.logger.info(
            f"POST_PROCESS;Executing command: {' '.join(args)}")
        process = subprocess.Popen(args, shell=True)
        process.wait()
        self.logger.info(
            f"POST_PROCESS;Command executed with return code: {process.returncode}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def read_input_files(self) -> List[Path]:
        self.logger.debug(f"READ_INPUT_FILES;{self.instrument.input.path}")

        # Get folder path
        source = self._get_source(self.instrument.input.path)
        if not source.exists():
            self.logger.info(
                f"READ_INPUT_FILES;Source folder does not exist: {source}")
            return []
        if not source.is_dir():
            self.logger.error(
                f"READ_INPUT_FILES;Source folder is not a directory: {source}")
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

        self.logger.info(f"READ_INPUT_FILES;Source files count: {len(files)}")
        return files

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def upload_files(self, files: List[Path]) -> List[Path]:
        self.logger.debug(
            f"UPLOAD_FILES:Files to upload: {len(files)} files at {self.config.settings.sftp.username}@{self.config.settings.sftp.host}:{self.config.settings.sftp.prefix}/{self.instrument.name}")
        if len(files) == 0:
            return []

        # Upload files
        upload_service = UploadService()
        uploaded = upload_service.upload_files(
            files, self.instrument.name)
        self.logger.info(
            f"UPLOAD_FILES:Uploaded files: {len(uploaded)} files at {self.config.settings.sftp.username}@{self.config.settings.sftp.host}:{self.config.settings.sftp.prefix}/{self.instrument.name}")
        return uploaded

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def move_files(self, files: List[Path]):
        self.logger.info(
            f"MOVE_FILES;Moving data file to: {self.instrument.output.path}")
        destination = self._get_destination(self.instrument.output.path)
        if destination.exists() and not destination.is_dir():
            self.logger.error(
                f"MOVE_FILES;Destination is not a directory: {destination}")
            return

        if not destination.exists():
            destination.mkdir(parents=True)
        for file in files:
            file.rename(destination / file.name)
        self.logger.info(f"MOVE_FILES;Files moved: {len(files)}")

    def _get_source(self, file: str) -> Path:
        path = Path(file)
        if path.is_absolute():
            return path
        return Path(self.config.settings.input if self.config.settings.input else os.getcwd()) / file

    def _get_destination(self, file: str) -> Path:
        path = Path(file)
        if path.is_absolute():
            return path
        return Path(self.config.settings.output if self.config.settings.output else os.getcwd()) / file
