from enum import Enum

class JobReqTarget(Enum):
    """The target of a job request."""
    CONTROL = "control"
    REGISTER = "register"
    UNREGISTER = "unregister"
    UPDATE = "update"

