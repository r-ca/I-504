import time
from ..common.config.dest.mk_loader import *
from ..dest.misskey.actions import MisskeyActions
from ..types.dest.misskey import *

class ProcessTest:
    def stub_cat(is_cat: bool):
        if is_cat:
            time.sleep(5)
            print("Meow!")
        else:
            print("?????????????????????????????")

    def test_action_mk():
        misskeyConfig = MisskeyConfigLoader(path="./I-504/config/dest/misskey.yml").load()
        misskeyActions = MisskeyActions()

        MisskeyPostReqData = {
            "post_body": "投稿テスト at " + str(time.time()),
            "meta_data": MisskeyMetaData(
                instance_address=misskeyConfig["target_instance"],
                token=misskeyConfig["token"],
                visibility=misskeyConfig["default_visibility"]
            )
        }
        misskeyActions.post(MisskeyPostReqData)
