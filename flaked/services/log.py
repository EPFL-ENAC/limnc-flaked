
import logging
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


class InstrumentLogger:

    def __init__(self, inst_config: InstrumentConfig):
        self.inst_config = inst_config
        self.logger = logging.getLogger(inst_config.name)
        default_logs_config = config_service.get_general_config().logs

        # Log level
        if inst_config.logs:
            self.logger.setLevel(inst_config.logs.level)
        elif default_logs_config:
            self.logger.setLevel(default_logs_config.level)
        else:
            self.logger.setLevel(logging.INFO)

        # Log file path
        log_path = f"{inst_config.name}.log"
        if inst_config.logs:
            log_path = Path(inst_config.logs.path) / f"{inst_config.name}.log"
        elif default_logs_config:
            log_path = Path(default_logs_config.path) / \
                f"{inst_config.name}.log"

        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True)

        print(f"Logging to {log_path}")
        handler = RotatingFileHandler(
            log_path,         # Log file name
            maxBytes=1000000,  # 1 MB before rotation
            backupCount=5      # Keep last 5 log files
        )
        formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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

    def _format(self, message: str) -> str:
        return f"{self.inst_config.name};{message}"


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
