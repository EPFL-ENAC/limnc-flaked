from typing import List
from collections import deque
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..services.config import config_service
from ..services.log import InstrumentLogger
from ..models.domain import InstrumentConfig

router = APIRouter()


@router.get("/instrument/{name}")
async def get_instrument_logs(name: str, tail: int = 100) -> InstrumentConfig:
    """Get the instrument logs

    Args:
        name (str): The instrument name
        tail (int, optional): The number of lines to tail. Defaults to 100. All lines are returned if tail is not positive.

    Returns:
        str: The instrument logs
    """
    def file_stream(file_path: str):
        with open(file_path, "rb") as file:
            yield from file

    def tail_file(file_path: str, lines: int = 10):
        """Yield the last `lines` lines of a file."""
        try:
            with open(file_path, "rb") as file:
                # Keep only the last `lines` lines
                last_lines = deque(file, maxlen=lines)
            for line in last_lines:
                yield line  # Stream each line
        except FileNotFoundError:
            yield b"File not found\n"

    instrument = config_service.get_instrument_config(name)
    file_path = InstrumentLogger(instrument).get_log_path()
    try:
        return StreamingResponse(tail_file(str(file_path), tail) if tail > 0 else file_stream(str(file_path)), media_type="text/plain")
    except FileNotFoundError:
        return StreamingResponse(iter(["File not found"]), status_code=404, media_type="text/plain")
