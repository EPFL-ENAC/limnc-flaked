import logging
import yaml
from pathlib import Path
from platformdirs import PlatformDirs
from ..models.domain import Config, SystemConfig, SFTPConfig, LogsConfig, InstrumentConfig


class ConfigService:

    def __init__(self):
        self.config_file = None
        self.load_config()

    def load_config(self, path: Path = None):
        """Load the configuration from provided file or from standard location

        Args:
            path (Path, optional): Path to the configuration file. Defaults to None.
        """
        if path != None:
            # Load the config file from the provided path
            if not path.exists():
                self._make_default_config_file(path)
            self.config_file = str(path)
        elif self.config_file == None:
            # Load the config file from the default path
            config_path = self._get_data_path() / "config.yml"
            if not config_path.exists():
                self._make_default_config_file(config_path)
            self.config_file = str(config_path)
        # Perform config loading
        self.config = None
        with open(self.config_file) as f:
            data = yaml.safe_load(f)
            self.config = Config(**data)

    def get_config(self) -> Config:
        return self.config

    def get_settings(self) -> SystemConfig:
        return self.config.settings

    def get_instrument_config(self, name: str) -> InstrumentConfig:
        for inst in self.config.instruments:
            if inst.name == name:
                return inst
        return None

    def update_config(self, config: Config):
        with open(self.config_file, 'w') as f:
            yaml.dump(config.model_dump(), f)

    def update_instrument_config(self, instrument: InstrumentConfig):
        for inst in self.config.instruments:
            if inst.name == instrument.name:
                inst = instrument
                break
        self.update_config(self.config)

    def delete_instrument_config(self, name: str):
        self.config.instruments = [
            inst for inst in self.config.instruments if inst.name != name]
        self.update_config(self.config)

    def add_instrument_config(self, instrument: InstrumentConfig):
        self.config.instruments.append(instrument)
        self.update_config(self.config)

    def add_or_update_instrument_config(self, instrument: InstrumentConfig):
        if self.get_instrument_config(instrument.name) == None:
            self.add_instrument_config(instrument)
        else:
            self.update_instrument_config(instrument)

    def _make_default_config_file(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        default_config = self._make_default_config()
        with open(path, 'w') as f:
            yaml.dump(default_config.model_dump(), f)

    def _make_default_config(self):
        sft_config = SFTPConfig(
            host="sftp.datalakes.org", port=22, prefix="data", username="user", password="changeme")
        logs_path = self._get_data_path() / "logs"
        logs_config = LogsConfig(path=str(logs_path), level="INFO")
        settings = SystemConfig(
            sftp=sft_config, logs=logs_config, input=None, output=None, attempts=3, wait=5)
        default_config = Config(settings=settings, instruments=[])
        return default_config

    def _get_data_path(self):
        data_path = None
        # Dev config
        try:
            data_path = Path("tests/data")
        except:
            pass

        # Deployment folder
        dirs = PlatformDirs("Flaked", "EPFL")
        if data_path == None or data_path.exists() == False:
            # User-specific config
            try:
                data_path = dirs.user_data_path
            except:
                pass
        if data_path == None or data_path.exists() == False:
            # System-wide config
            try:
                data_path = dirs.site_data_path
            except:
                pass
        if data_path == None:
            raise FileNotFoundError(
                "Data path cannot be identified for Flaked app")

        if data_path.exists() == False:
            # Make the data path at site level
            try:
                data_path = dirs.site_data_path
                data_path.mkdir(parents=True)
            except:
                # Make the data path at user level
                try:
                    data_path = dirs.user_data_path
                    data_path.mkdir(parents=True)
                except:
                    raise FileNotFoundError(
                        "Data path cannot be created for Flaked app")

        logging.info(f"Data path: {data_path}")
        return data_path


config_service = ConfigService()
