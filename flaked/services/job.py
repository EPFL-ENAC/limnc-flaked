from typing import List
import logging
import subprocess
import time
from pathlib import Path
import os
import re
from .config import config_service
from .log import log_service
from .upload import UploadService
from ..models.domain import CommandConfig


class JobProcessor:

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.instrument_name = job_id.split(':')[0]

    def process(self):
        try:
            logging.info(f"Processing data for job {self.job_id}")
            self.config = config_service.get_config()
            self.instrument = config_service.get_instrument_config(
                self.instrument_name)
            self.logger = log_service.for_instrument(self.instrument)
            self.logger.debug([self.job_id, "PROCESS_START"])

            if self.instrument.preprocess:
                self.pre_process()

            input_files = self.read_input_files()
            if len(input_files) > 0:
                uploaded_files = self.upload_files(input_files)
                if len(uploaded_files) > 0:
                    self.move_files(uploaded_files)

            if self.instrument.postprocess:
                self.post_process()

            self.logger.debug([self.job_id, "PROCESS_SUCCESS"])
        except Exception as e:
            if self.logger:
                self.logger.debug([self.job_id, "PROCESS_FAILURE", str(e)])
            logging.error("Pipeline failed", exc_info=True)
            raise

    def pre_process(self):
        self._do_process("PRE_PROCESS", self.instrument.preprocess)

    def post_process(self):
        self._do_process("POST_PROCESS", self.instrument.postprocess)

    def read_input_files(self) -> List[Path]:
        self.logger.debug([self.job_id, "READ_INPUT_FILES",
                          self.instrument.input.path])

        # Get folder path
        source = self._get_source(self.instrument.input.path)
        if not source.exists():
            self.logger.info(
                [self.job_id, "READ_INPUT_FILES", "Source folder does not exist", source])
            return []
        if not source.is_dir():
            self.logger.error(
                [self.job_id, "READ_INPUT_FILES", "Source folder is not a directory", source])
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

        self.logger.info(
            [self.job_id, "READ_INPUT_FILES", "Source files count", len(files)])
        return files

    def upload_files(self, files: List[Path]) -> List[Path]:
        self.logger.debug(
            [self.job_id, "UPLOAD_FILES", "Files to upload", f"{self.config.settings.sftp.username}@{self.config.settings.sftp.host}:{self.config.settings.sftp.prefix}/{self.instrument.name}"])
        if len(files) == 0:
            return []

        # Upload files
        upload_service = UploadService()
        attemps = 0
        uploaded = []
        max_attemps = self.config.settings.attempts
        wait_seconds = self.config.settings.wait
        while attemps < max_attemps and len(uploaded) == 0:
            try:
                uploaded = upload_service.upload_files(
                    files, self.instrument.name)
            except Exception as e:
                attemps += 1
                self.logger.debug(
                    [self.job_id, "UPLOAD_FILES", f"Failed to upload files, attempt {attemps}, retrying in {wait_seconds} seconds", str(e)])
                time.sleep(wait_seconds)
        if len(uploaded) == 0:
            self.logger.error(
                [self.job_id, "UPLOAD_FILES", "Failed to upload files", f"{self.config.settings.sftp.username}@{self.config.settings.sftp.host}:{self.config.settings.sftp.prefix}/{self.instrument.name}"])
            return []
        uploaded = upload_service.upload_files(
            files, self.instrument.name)
        self.logger.info(
            [self.job_id, "UPLOAD_FILES", "Uploaded files", len(uploaded)])
        return uploaded

    def move_files(self, files: List[Path]):
        self.logger.debug(
            [self.job_id, "MOVE_FILES", "Moving data file", self.instrument.output.path])
        destination = self._get_destination(self.instrument.output.path)
        if destination.exists() and not destination.is_dir():
            self.logger.error(
                [self.job_id, "MOVE_FILES", "Destination is not a directory", destination])
            return

        if not destination.exists():
            destination.mkdir(parents=True)
        for file in files:
            file.rename(destination / file.name)
        self.logger.info([self.job_id, "MOVE_FILES",
                         "Files moved", len(files)])

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

    def _do_process(self, type: str, command_config: CommandConfig):
        if not command_config:
            return
        args = [command_config.command]
        if command_config.args:
            args.extend(command_config.args)
        self.logger.info(
            [self.job_id, type, "Executing command", " ".join(args)])
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.wait()
        pstdout, pstderr = process.communicate()
        if pstdout:
            self.logger.info([self.job_id, type, pstdout])
        if pstderr:
            self.logger.error([self.job_id, type, pstderr])
        self.logger.info(
            [self.job_id, type, "Command executed with return code", process.returncode])
