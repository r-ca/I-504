from enum import Enum

class JobReqType(Enum):
    """The target of a job request."""
    CONTROL = "control"
    REGISTER = "register"
    UNREGISTER = "unregister"
    UPDATE = "update"

