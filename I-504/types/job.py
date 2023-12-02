from ..enums.job import *

import pickle

from abc import ABCMeta

class IJobReqBody(metaclass=ABCMeta): # interface
    pass # TODO: ファイル分割

class JobDepend:
    """依存ジョブと仲介の設定"""
    def __init__(self, depend_job_id: str, require_mediator: bool = False, mediator_func = None):
        self.depend_job_id = depend_job_id # 依存ジョブのID
        self.require_mediator = require_mediator # 仲介が必要かどうか
        self.mediator_func = mediator_func # 仲介関数

class JobMeta:
    """Jobのメタデータ"""
    def __init__(self, job_name: str, job_desc: str, priority: JobPriority, has_depend_job:bool , job_depend: JobDepend = None):
        self.job_name = job_name # ジョブ名
        self.job_desc = job_desc # ジョブの説明
        self.priority = priority # ジョブの優先度
        self.has_depend_job = has_depend_job # 依存ジョブを持つかどうか
        self.job_depend = job_depend # 依存ジョブと仲介の設定

class Job:
    """実際に記録されるJobの型"""
    def __init__(self, job_id: str, job_meta: JobMeta, job_func, args: tuple = (), kwargs: dict = {}):
        self.job_id = job_id # ジョブID
        self.job_meta = job_meta # ジョブのメタデータ
        self.job_func = pickle.dumps(job_func) # 実行する関数
        self.args = args # 関数に渡す引数
        self.kwargs = kwargs # 関数に渡すキーワード引数

class JobReqBody_Control(IJobReqBody):
    """Job Manager自体をコントロールするリクエスト"""
    def __init__(self, command: JobManagerControlCommand):
        self.command = command

class JobReqBody_Register(IJobReqBody):
    """Job Managerにジョブを登録するリクエスト"""
    def __init__(self, job_id:str, job: Job):
        self.job_id = job_id # ジョブID(UUIDv4)
        self.job = job # ジョブの内容

class JobReqBody_Unregister(IJobReqBody):
    """Job Managerからジョブを削除するリクエスト"""
    pass # TODO

class JobReqBody_Update(IJobReqBody):
    """Job Managerのジョブを更新するリクエスト"""
    pass # TODO

class JobReqBody_Debug(IJobReqBody):
    """デバッグ用Request body(Dict型をそのまま引き渡す)"""
    def __init__(self, dict: dict):
        self.dict = dict

class JobManagerRequest:
    """Job ManagerにPipeで送るリクエスト"""
    def __init__(self, job_req_type: JobReqType, job_req_body: IJobReqBody):
        self.job_req_type = job_req_type
        self.job_req_body = job_req_body
