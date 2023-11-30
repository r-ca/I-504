from ...types import *
from ...interface.system import *

class MisskeyConfigLoader: # TODO: 型
    def __init__(self, path:str):
        self.path = path

    def load(self):
        import yaml
        with open(self.path, "r") as yml:
            config = yaml.safe_load(yml)
        return dict(
            target_instance=config["target_instance"],
            token=config["token"],
            default_visibility=config["default_visibility"]
        )

class StubMisskeyConfigLoader: # TODO: 型
    def load(self):
        return dict(
            target_instance="misskey.io",
            token="test",
            default_visibility="public"
        )
