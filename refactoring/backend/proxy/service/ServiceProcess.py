from multiprocessing import Process, Value
from .ServiceClass import Service
from ..multiprocess import FilterBrokerAsker
from ..multiprocess import FilterBroker

class ServiceProcess(Process):

    def __init__(self, service : Service, asker : FilterBrokerAsker):
        super().__init__()
        self.service : Service = service
        self.asker : FilterBrokerAsker = asker

    
    def run(self):
        import time
        import logging
        filters = self.asker.ask(FilterBroker.get_subscribed_filters, self.service)
        while True:
            logging.info(f"I'm {self.service.name} : {self.service.port} {self.service.type}")
            for f in filters:
                f(1,2)
            time.sleep(5)

    
    async def check_queue(self):
        pass