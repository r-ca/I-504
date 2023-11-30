from ...types.common import *
from ...interface.system import *
import yaml


class YamlConfigLoader(IConfigLoader):
    def __init__(self, path:str):
        self.path = path

    def load(self) -> CoreConfig:
        # 1. Load yaml
        with open(self.path, "r") as yml:
            config = yaml.safe_load(yml)

            # DB settings
            db_settings = config["db_settings"]
            
            # Source settings
            source_list = config["source_list"]

            # Dest settings
            dest_list = config["dest_list"]

            # 2. Create CoreConfig
            return CoreConfig(db_settings, source_list, dest_list)
