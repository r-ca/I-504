from ..enums.job import *

from abc import ABCMeta

class IJobReqBody(metaclass=ABCMeta): # interface
    pass # TODO: ファイル分割

class JobReqBody_Control(IJobReqBody):
    def __init__(self, command: JobManagerControlCommand):
        self.command = command

class JobReqBody_Register(IJobReqBody):
    pass # TODO

class JobReqBody_Unregister(IJobReqBody):
    pass # TODO

class JobReqBody_Update(IJobReqBody):
    pass # TODO

class JmRequest:
    def __init__(self, job_req_type: JobReqType, job_req_body: IJobReqBody):
        self.job_req_type = job_req_type
        self.job_req_body = job_req_body
