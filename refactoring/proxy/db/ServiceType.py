from enum import Enum

class ServiceType(str, Enum):
    TCP = "tcp"
    HTTP = "http"
    HTTPS = "https"