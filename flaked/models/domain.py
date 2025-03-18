from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SFTPConfig(BaseModel):
    """SFTP destination service
    """
    host: str
    port: int = Field(default=22)
    # Path prefix in the destination folder
    prefix: str = Field(default='data')
    username: str
    password: str


class IOConfig(BaseModel):
    """Base class for file handling
    """
    # Folder path, absolute or relative to app's folder
    path: str


class LogsConfig(IOConfig):
    """Where log files are to be found/written
    """
    level: str = Field(default='INFO')


class SystemConfig(BaseModel):
    """General system configuration
    """
    sftp: SFTPConfig
    logs: LogsConfig
    input: Optional[str] = Field(default=None)   # Input folder prefix
    output: Optional[str] = Field(default=None)  # Output folder prefix
    attempts: int = Field(default=3)
    wait: int = Field(default=5)

# Enum for time unit


class TimeUnit(str, Enum):
    minutes = "minutes"
    hours = "hours"
    days = "days"
    weeks = "weeks"


class Interval(BaseModel):
    """Sheduler triggering interval
    """
    value: int
    unit: TimeUnit


class ScheduleConfig(BaseModel):
    """Scheduler triggering settings, cron and/or interval based"""
    cron: Optional[str]
    interval: Optional[Interval]


class CommandConfig(BaseModel):
    """A command to be executed"""
    command: str
    args: List[str] = Field(default=[])


class FileFilter(BaseModel):
    # File name pattern
    regex: Optional[str] = Field(default='.*')
    # Last files to skip
    skip: Optional[int] = Field(default=0)
    # Minimum age of the files
    minAge: Optional[Interval] = Field(default=None)


class InputConfig(IOConfig):
    """Source folder, where the instrument files are located.
    """
    filter: Optional[FileFilter] = Field(default=None)


class OutputConfig(IOConfig):
    """Destination folder, after the instrument files have been uploaded.
    """
    pass


class InstrumentConfig(BaseModel):
    """Instrument configuration, scheduling and folders
    """
    name: str
    schedule: ScheduleConfig
    preprocess: Optional[CommandConfig] = Field(default=None)
    postprocess: Optional[CommandConfig] = Field(default=None)
    input: InputConfig
    output: OutputConfig
    logs: Optional[LogsConfig] = Field(default=None)


class Config(BaseModel):
    """Application configuration
    """
    settings: SystemConfig
    instruments: List[InstrumentConfig]
