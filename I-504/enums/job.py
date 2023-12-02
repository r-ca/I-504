from enum import Enum

class JobReqType(Enum):
    """The target of a job request."""
    CONTROL = "control"
    REGISTER = "register"
    UNREGISTER = "unregister"
    UPDATE = "update"

class JobManagerControlCommand(Enum):
    """The command of a job manager."""
    STOP = "stop"
