from ..types.dest.interface import *


class JobUtils:

    def notify(dest_type:str, dest_id:str, notify_body:str):
        if dest_type == "misskey":
            JobUtilsMisskey.notify_misskey(dest_id=dest_id, notify_data=notify_body)
        #else:

class JobUtilsMisskey:

    def notify_misskey(dest_id:str, notify_body:str, meta_data:MetaData):
        ## MisskeyMetaData
        from ..types.dest.misskey import MisskeyPostReqData

        misskeyPostReqData = MisskeyPostReqData(post_body=notify_body, meta_data=meta_data)


