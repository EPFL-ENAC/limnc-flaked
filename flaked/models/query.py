
from pydantic import BaseModel, Field
from enum import Enum


class Action(str, Enum):
    """Action to perform on the scheduler service: start, stop, pause, or resume.
    """
    start = "start"
    stop = "stop"
    pause = "pause"
    resume = "resume"


class StatusValue(str, Enum):
    """Status of the scheduler or of a scheduled job
    """
    running = "running"
    stopped = "stopped"
    paused = "paused"


class Status(BaseModel):
    """Status of the scheduler or of a scheduled job
    """
    status: StatusValue
