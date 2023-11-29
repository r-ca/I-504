from .interface import *

class MisskeyVisibility:
    public = "public"
    home = "home"
    followers = "followers"
    specified = "specified"
    private = "private"

class MisskeyMetaData(MetaData):
    def __init__(self, visibility:MisskeyVisibility, instance_address:str, token:str):
        self.visibility: MisskeyVisibility = visibility
        self.instance_address: str = instance_address
        self.token: str = token

class MisskeyPostReqData(IPostReqData):
    def __init__(self, post_data:PostData, meta_data:MisskeyMetaData):
        self.post_data:PostData = post_data
        self.meta_data:MisskeyMetaData = meta_data
