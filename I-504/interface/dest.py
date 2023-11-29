## Destination interface
import abc
from ..types import *

class IDestination(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check_connection(self) -> bool: # 接続テスト
        pass

    @abc.abstractmethod
    def post(self, post_req_data:IPostReqData) -> int: # 投稿
        pass
