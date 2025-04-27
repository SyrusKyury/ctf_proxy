from ..configuration.constants import NGINX_CONF_PATH, HOST, PROXY_IP
from ..configuration.proxyConfigurationManager import ProxyConfigurationManager
import logging


class NGINXConfigurationManager:

    

    def write_nginx_conf():
        nginx_conf = ProxyConfigurationManager.load_configuration()["global_config"]["nginx"]
        services = ProxyConfigurationManager.load_configuration()["services"]
        
        logging.debug(f"Services: {services}")
        logging.debug(f"Global config: {nginx_conf}")
        
        fail_timeout = nginx_conf.get("fail_timeout", 5)
        max_fails = nginx_conf.get("max_fails", 5)
        connect_timeout = nginx_conf.get("connect_timeout", 5)

        nginx_conf = '''worker_processes auto;

        events {{ 
            worker_connections 1024; 
        }}

        stream {{
            {}
        }}
        '''

        template = """
            upstream {service_name} {{
                server {proxy_ip}:{target_port} fail_timeout={fail_timeout}s max_fails={max_fails};
                server 127.0.0.1:{target_port} backup;
            }}
            server {{
                proxy_connect_timeout {connect_timeout}s;
                listen {listen_port};
                listen [::]:{listen_port};
                proxy_pass {service_name};
            }}
        """

        config = ""

        for service_name, service in services.items():
            config += template.format(service_name = service_name + "_upstream",
                                    target_port = service["port"],
                                    listen_port = service["nginx_port"],
                                    connect_timeout = connect_timeout,
                                    max_fails = max_fails,
                                    fail_timeout = fail_timeout,
                                    host_callback_ip = HOST,
                                    proxy_ip = PROXY_IP,
                                    )
            
        with open(NGINX_CONF_PATH, "w") as f:
            f.write(nginx_conf.format(config))
