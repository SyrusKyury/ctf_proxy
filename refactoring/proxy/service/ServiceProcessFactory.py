from multiprocessing import Process, Value
from .ServiceClass import Service

class ServiceProcessFactory:

    @staticmethod
    def new_process(service : Service) -> Process:
        Process()

    
    @staticmethod
    def __main_process__(service: Service, count):
        pass