import os

CONFIG_JSON_PATH : str = os.sep + os.path.join(*os.path.dirname(__file__).split(os.sep)[:-2], 'data', 'config.json')
EXPOSED_PORT : int = os.getenv('EXPOSED_PORT', 65432)

AUTHENTICATION_TOKEN : str = os.getenv('AUTHENTICATION_TOKEN', 'change_this_token')

TITLE : str = "CTF Proxy"
DESCRIPTION : str = "An Intrusion Prevention System for Attack-Defense CTFs"
VERSION : str = "0.1.0"