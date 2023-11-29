from ....types import *
from ....interface.system import *
from ....interface.dest import *
from ....common.logger import Logger

logger = Logger("misskey")

class MisskeyActions(IDestination):
    def __init__(self, config:CoreConfig):
        self.config = config # TODO: あとでなんとかする

    def check_connection(self) -> bool:
        return True

    def post(self, post_data:PostData, meta_data:MetaData) -> int:
        post_logger = logger.child("post")
        post_logger.debug("Args: post_data: {}, meta_data: {}".format(post_data, meta_data))

        return 200


class StubMisskeyActions(IDestination):
    def __init__(self, config:CoreConfig):
        self.config = config # TODO: あとでなんとかする

    def check_connection(self) -> bool:

        return True

    def post(self, post_req_data:IPostReqData) -> int:
        post_logger = logger.child("post")
        post_logger.debug("Args: post_req_data: {}".format(post_req_data))
        post_logger.debug("post_data: {}, meta_data: {}".format(post_req_data.post_data, post_req_data.meta_data))
        post_logger.debug("post_data.origin: {}, post_data.content: {}".format(post_req_data.post_data.origin, post_req_data.post_data.content))
        post_logger.debug("meta_data.visibility: {}, meta_data.instance_address: {}, meta_data.token: {}".format(post_req_data.meta_data.visibility, post_req_data.meta_data.instance_address, post_req_data.meta_data.token))

        return 200
