from ..constants import NGINX_CONF_PATH, HOST, PROXY_IP
from ..multiprocess import redis_connection
import logging


class NGINXConfigurationManager:

    @staticmethod
    def __get_listen_port__(port : int):
        """
        Get the port to listen on. If the port is 0, it will be replaced with a random port.
        """
        #TODO: Cambialo per l'amor di dio
        return port + 30000
    

    def write_nginx_conf():
        nginx_conf = redis_connection.hgetall("nginx")
        service_keys = redis_connection.keys("services:*")
        services = {}
        for key in service_keys:
            service_data = redis_connection.hgetall(key)
            logging.debug(f"Service data: {service_data}")
            services[service_data["name"]] = {
                "port": service_data["port"],
                "type": service_data["type"]
            }

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
                                    listen_port = NGINXConfigurationManager.__get_listen_port__(int(service["port"])),
                                    connect_timeout = connect_timeout,
                                    max_fails = max_fails,
                                    fail_timeout = fail_timeout,
                                    host_callback_ip = HOST,
                                    proxy_ip = PROXY_IP,
                                    )
            
        with open(NGINX_CONF_PATH, "w") as f:
            f.write(nginx_conf.format(config))
