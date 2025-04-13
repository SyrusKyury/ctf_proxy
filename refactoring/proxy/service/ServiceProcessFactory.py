from multiprocessing import Process, Value
from .ServiceClass import Service
from ..multiprocess import FilterBrokerAsker

class ServiceProcessFactory:

    @staticmethod
    def new_process(service : Service, asker : FilterBrokerAsker) -> Process:
        return Process(
            target=ServiceProcessFactory.__main_process__,
            args=(service, asker, ),
            name=service.name,
            daemon=True
        )

    
    @staticmethod
    def __main_process__(service: Service, asker: FilterBrokerAsker):
        import time
        while True:
            print(service)
            print(f"Example!!!")
            time.sleep(60)