from .ServiceClass import Service
from multiprocessing import Process

class ServiceManager:
    def __init__(self) -> None:
        self.running_services : dict[Service, Process] = {}

    
    def start_service(self, service: Service) -> None:
        pass

    
    def stop_service(self, service: Service) -> None:
        pass


    def is_running(self, service: Service) -> bool:
        if service in self.running_services:
            return True
        return False