from .constants import CONFIG_JSON_PATH
from ..service import Service
import json

class ProxyConfigurationManager:
    
    @staticmethod
    def load_configuration():
        """
        Load the configuration from the JSON file.
        """
        try:
            with open(CONFIG_JSON_PATH, 'r') as file:
                config = json.load(file)
            return config
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {CONFIG_JSON_PATH}")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from configuration file: {CONFIG_JSON_PATH}")
        except Exception as e:
            raise Exception(f"An error occurred while loading the configuration: {e}")
        

    @staticmethod
    def store_service_information(service : Service, nginx_port : int):
        """
        Store the service information in the configuration file.
        """
        # TODO: Add support for ssl
        try:
            config = ProxyConfigurationManager.load_configuration()
            config['services'][service.name] = service.json_dump_for_settings()
            config['services'][service.name]['nginx_port'] = nginx_port
            with open(CONFIG_JSON_PATH, 'w') as file:
                json.dump(config, file, indent=4)
        except Exception as e:
            raise Exception(f"An error occurred while storing service information: {e}")
        

    @staticmethod
    def remove_service_information(service_name : str):
        """
        Remove the service information from the configuration file.
        """
        try:
            config = ProxyConfigurationManager.load_configuration()
            if service_name in config['services']:
                del config['services'][service_name]
                with open(CONFIG_JSON_PATH, 'w') as file:
                    json.dump(config, file, indent=4)
            else:
                raise Exception(f"Service {service_name} not found in configuration.")
        except Exception as e:
            raise Exception(f"An error occurred while removing service information: {e}")
        
    
    @staticmethod
    def service_can_be_added(service : Service):
        """
        Check if the service can be added to the configuration.
        This checks if the service name and port are unique.
        """
        try:
            config = ProxyConfigurationManager.load_configuration()
            if service.name in config['services'] or service.port in [s['port'] for s in config['services'].values()]:
                return False
            else:
                return True
        except Exception as e:
            raise Exception(f"An error occurred while checking service: {e}")
        

    @staticmethod
    def service_exists(service_name : str):
        """
        Check if the service exists in the configuration.
        """
        try:
            config = ProxyConfigurationManager.load_configuration()
            return service_name in config['services']
        except Exception as e:
            raise Exception(f"An error occurred while checking service existence: {e}")
        
    
    @staticmethod
    def get_service_information(service_name : str):
        """
        Get the service information from the configuration.
        """
        try:
            config = ProxyConfigurationManager.load_configuration()
            if service_name in config['services']:
                return config['services'][service_name]
            else:
                return None
        except Exception as e:
            raise Exception(f"An error occurred while getting service information: {e}")
        
    
    @staticmethod
    def get_all_services():
        """
        Get all services from the configuration.
        """
        try:
            config = ProxyConfigurationManager.load_configuration()
            return config['services']
        except Exception as e:
            raise Exception(f"An error occurred while getting all services: {e}")
        

    @staticmethod
    def update_service_information(service_name : str, service : Service, nginx_port : int):
        """
        Update the service information in the configuration.
        """
        try:
            config = ProxyConfigurationManager.load_configuration()
            if service_name in config['services']:
                config['services'][service_name] = service.json_dump_for_settings()
                config['services'][service_name]['nginx_port'] = nginx_port
                with open(CONFIG_JSON_PATH, 'w') as file:
                    json.dump(config, file, indent=4)
            else:
                raise Exception(f"Service {service_name} not found in configuration.")
        except Exception as e:
            raise Exception(f"An error occurred while updating service information: {e}")
