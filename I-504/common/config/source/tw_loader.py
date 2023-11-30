from ....types.source.twitter import *
import yaml

class TwitterSourceConfigLoader:
    # WIP
    def __init__(self, path:str):
        self.path = path

    def load(self) -> TwitterSourceConfig:
        with open(self.path, "r") as yml:
            config = yaml.safe_load(yml)
            
        return TwitterSourceConfig(
            auth_cookie=TwitterAuthCookie(
                ct0=config["auth_cookie"]["ct0"],
                auth_token=config["auth_cookie"]["auth_token"]
            ),
            update_limit=config["update_limit"]
        )
