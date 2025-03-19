
import logging
import csv
import io
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..models.domain import InstrumentConfig
from .config import config_service

# Configure logging
logging.basicConfig(
    filename='data_processing.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class CSVFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        stringIO = io.StringIO()
        writer = csv.writer(stringIO, quoting=csv.QUOTE_ALL)
        row = [self.formatTime(record), record.levelname, record.name]
        row.extend(record.msg)
        writer.writerow(row)
        return stringIO.getvalue().strip()


class InstrumentLogger:

    def __init__(self, inst_config: InstrumentConfig):
        self.inst_config = inst_config
        self.logger = logging.getLogger(inst_config.name)
        default_logs_config = config_service.get_settings().logs

        # Log level
        if inst_config.logs:
            self.logger.setLevel(inst_config.logs.level)
        elif default_logs_config:
            self.logger.setLevel(default_logs_config.level)
        else:
            self.logger.setLevel(logging.INFO)

        # Log file path
        self.log_path = f"{inst_config.name}.log"
        if inst_config.logs:
            self.log_path = Path(inst_config.logs.path) / \
                f"{inst_config.name}.log"
        elif default_logs_config:
            self.log_path = Path(default_logs_config.path) / \
                f"{inst_config.name}.log"

        if not self.log_path.parent.exists():
            self.log_path.parent.mkdir(parents=True)

        print(f"Logging to {self.log_path}")
        handler = RotatingFileHandler(
            self.log_path,         # Log file name
            maxBytes=1000000,  # 1 MB before rotation
            backupCount=5      # Keep last 5 log files
        )
        handler.setFormatter(CSVFormatter())
        self.logger.addHandler(handler)

    def get_log_path(self) -> Path:
        """Get the log file path.

        Returns:
            Path: The log file path
        """
        return self.log_path

    def debug(self, message: str):
        """Output formatted debug message.

        Args:
            message (str): The message
        """
        self.logger.debug(self._format(message))

    def info(self, message: str):
        """Output formatted info message.

        Args:
            message (str): The message
        """
        self.logger.info(self._format(message))

    def error(self, message: str):
        """Output formatted error message.

        Args:
            message (str): The message
        """
        self.logger.error(self._format(message))

    def as_logger(self) -> logging.Logger:
        """Get the wrapped logger.

        Returns:
            Logger: The logging's logger
        """
        return self.logger

    def _format(self, message: str) -> list:
        if isinstance(message, list):
            return message
        return [message]


class LogService:

    def __init__(self):
        self.loggers = {}

    def for_instrument(self, inst_config: InstrumentConfig) -> InstrumentLogger:
        """Get or create the instrument logger

        Args:
            inst_config (InstrumentConfig): The instrument configuration

        Returns:
            InstrumentLogger: The instrument logger
        """
        if inst_config.name in self.loggers:
            return self.loggers[inst_config.name]
        self.loggers[inst_config.name] = InstrumentLogger(inst_config)
        return self.loggers[inst_config.name]

    def clear(self, name: str):
        """Clear registered logger by name.

        Args:
            name (str): The logger name
        """
        if name in self.loggers:
            self.loggers[name] = None


log_service = LogService()
