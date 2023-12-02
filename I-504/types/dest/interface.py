import abc
from .common import *

class MetaData(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        pass

class IPostReqData(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, post_body:str, meta_data:MetaData):
        post_data:str = post_body
        meta_data:MetaData = meta_data
