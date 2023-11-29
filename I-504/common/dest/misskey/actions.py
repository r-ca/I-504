from ....types import *
from ....interface.system import *
from ....interface.dest import *
from ....common.logger import Logger
import requests

logger = Logger("misskey")

class MisskeyActions(IDestinationActions):
    def __init__(self, config:CoreConfig):
        self.config = config # TODO: あとでなんとかする

    def check_connection(self) -> bool:
        return True

    def post(self, post_req_data:IPostReqData) -> int:
        post_logger = logger.child("post")
        
        post_data = post_req_data.post_data
        meta_data = post_req_data.meta_data

        resp = requests.post(
            meta_data.instance_address + "/api/notes/create",
            json={
                "i": meta_data.token,
                "visibility": meta_data.visibility,
                "text": post_data.content
            }
        )

        post_logger.debug("resp: {}".format(resp))

        return resp.status_code

    def get_info(self) -> dict:
        get_logger = logger.child("get_info")
        


class StubMisskeyActions(IDestinationActions):
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

    def get_info(self):
        get_logger = logger.child("get_info")

        get_logger.debug("Args: ")
        get_logger.debug("self.config: {}".format(self.config))

    
