
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..models.domain import InstrumentConfig

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
        if inst_config.logs and inst_config.logs.level == 'DEBUG':
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        log_path = f"{inst_config.name}.log"
        if inst_config.logs and inst_config.logs.path:
            log_path = Path(inst_config.logs.path) / f"{inst_config.name}.log"
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
