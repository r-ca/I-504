import abc
from .common import *

class MetaData(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        pass

class IPostReqData(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, post_data:PostData, meta_data:MetaData):
        post_data:PostData = post_data
        meta_data:MetaData = meta_data
