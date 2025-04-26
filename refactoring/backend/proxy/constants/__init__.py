import os

CONFIG_JSON_PATH : str = os.sep + os.path.join(*os.path.dirname(__file__).split(os.sep)[:-2], 'data', 'config.json')
EXPOSED_PORT : int = int(os.getenv('EXPOSED_PORT', 6543))
DEBUG : bool = True

AUTHENTICATION_TOKEN : str = os.getenv('AUTHENTICATION_TOKEN', 'change_this_token')

# SSH
SSH_PRIVATE_KEY_PATH : str = os.getenv('SSH_PRIVATE_KEY_PATH')
HOST : str = "172.17.0.1" 
PORT : int = 22
USERNAME : str = "root"
NGINX_IP : str = "172.30.0.2"
HOST_CALLBACK_IP : str = "198.18.0.42"
PROXY_IP : str = "172.30.0.3"

NGINX_CONF_PATH : str = "/app/nginx.conf"

# Metadata
TITLE : str = "CTF Proxy"
DESCRIPTION : str = "An Intrusion Prevention System for Attack-Defense CTFs"
VERSION : str = "0.1.0"