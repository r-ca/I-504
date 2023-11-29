## Interface for the I-504 system

import abc
from ..types.common import *

class IConfigLoader(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self) -> CoreConfig:
        pass

    
