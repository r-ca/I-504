from ..enums.job import *

from abc import ABCMeta

class IJobReqBody(metaclass=ABCMeta): # interface
    pass # TODO: ファイル分割

class JobReqBody_Control(IJobReqBody):
    """Job Manager自体をコントロールするリクエスト"""
    def __init__(self, command: JobManagerControlCommand):
        self.command = command

class JobReqBody_Register(IJobReqBody):
    """Job Managerにジョブを登録するリクエスト"""
    pass # TODO

class JobReqBody_Unregister(IJobReqBody):
    """Job Managerからジョブを削除するリクエスト"""
    pass # TODO

class JobReqBody_Update(IJobReqBody):
    """Job Managerのジョブを更新するリクエスト"""
    pass # TODO

class JobManagerRequest:
    """Job ManagerにPipeで送るリクエスト"""
    def __init__(self, job_req_type: JobReqType, job_req_body: IJobReqBody):
        self.job_req_type = job_req_type
        self.job_req_body = job_req_body
