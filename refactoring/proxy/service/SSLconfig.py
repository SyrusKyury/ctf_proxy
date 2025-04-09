from dataclasses import dataclass

@dataclass
class SSLConfig:
    server_certificate: str
    server_key: str
    client_certificate: str = None
    client_key: str = None
    ca_file: str = None