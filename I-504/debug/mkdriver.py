# MisskeyPostドライバ

from ..types import *
from ..interface.system import *
from ..interface.dest import *
from ..common.logger import Logger

dbg_logger = Logger("DEBUG")
driver_logger = Logger("driver")
mk_logger = Logger("misskey")

def mk_post(misskeyActions: IDestinationActions):
    mk_logger.info("mk_post: Initializing the system")

    post_data = PostData(origin="@test", content="Hello, world!")
    meta_data = MisskeyMetaData(visibility=MisskeyVisibility.public, instance_address="https://misskey.xyz", token="test")



    misskeyActions.post(MisskeyPostReqData(post_data=post_data, meta_data=meta_data));

    misskeyActions.get_info()

    


