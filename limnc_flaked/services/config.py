import yaml
from pathlib import Path
import os


class ConfigService:
  
  def __init__(self, config_file):
      self.config_file = config_file
      self.config = None
      with open(config_file) as f:
          self.config = yaml.safe_load(f)
  
  def reload(self):
      with open(self.config_file) as f:
          self.config = yaml.safe_load(f)
          
  def get_config(self):
      return self.config
    
config_path = None
# User-specific config
try:
  config_path = Path(os.getenv("APPDATA")) / "Flaked" / "config.yml"
except:
  pass
if config_path == None or config_path.exists() == False:
  # System-wide config
  try:
    config_path = Path("C:/ProgramData/Flaked/config.json")
  except:
    pass
if config_path == None or config_path.exists() == False:
  # Dev config
  try:
    config_path = Path("tests/data/config.yml") 
  except:
    pass

config_service = ConfigService(str(config_path))