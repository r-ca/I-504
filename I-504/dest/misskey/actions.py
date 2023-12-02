from ...types.dest.interface import *
from ...types.dest.misskey import *
from ...types.dest.common import *

import requests
from ...common.logger import Logger


mk_action_logger = Logger("misskey-actions")
class MisskeyActions:
    def post(self, post_req_data:IPostReqData) -> int:
        logger = mk_action_logger.child("post")
        post_body = post_req_data["post_body"]
        meta_data = post_req_data["meta_data"]

        resp = requests.post(
            meta_data.instance_address + "/api/notes/create",
            json={
                "i": meta_data.token,
                "visibility": meta_data.visibility,
                "text": post_body
            }
        )

        logger.debug("resp: {}".format(resp))

        return resp.status_code

    def check_update_user(engine, user_unique_id:str):
        pass
        # TODO
