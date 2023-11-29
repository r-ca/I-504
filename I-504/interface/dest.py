## Destination interface
import abc
from ..types import *

class IDestinationActions(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check_connection(self) -> bool: # 接続テスト
        pass

    @abc.abstractmethod
    def post(self, post_req_data:IPostReqData) -> int: # 投稿
        pass

    # @abc.abstractmethod
    # def getInfo(self, get_req_data:IGetReqData): # 取得
    #     pass

