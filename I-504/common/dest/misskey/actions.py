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

    def post(self, post_data:PostData, meta_data:MetaData) -> int:
        post_logger = logger.child("post")
        post_logger.debug("Args: post_data: {}, meta_data: {}".format(post_data, meta_data))

        return 200
