import yaml
from pathlib import Path
import os
from ..models.domain import Config, InstrumentConfig


class ConfigService:

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = None
        with open(config_file) as f:
            data = yaml.safe_load(f)
            self.config = Config(**data)

    def reload(self):
        with open(self.config_file) as f:
            data = yaml.safe_load(f)
            self.config = Config(**data)

    def get_config(self) -> Config:
        return self.config

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


config_path = None
# User-specific config
try:
    config_path = Path(os.getenv("APPDATA")) / "Flaked" / "config.yml"
except:
    pass
if config_path == None or config_path.exists() == False:
    # System-wide config
    try:
        config_path = Path("C:/ProgramData/Flaked/config.yml")
    except:
        pass
if config_path == None or config_path.exists() == False:
    # Dev config
    try:
        config_path = Path("tests/data/config.yml")
    except:
        pass

config_service = ConfigService(str(config_path))
