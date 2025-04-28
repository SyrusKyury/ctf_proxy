from .ServiceClass import Service
from .ServiceProcess import ServiceProcess
from multiprocessing import Process, Event
from ..multiprocess import FilterBrokerAsker
import logging
import os
import signal

class ServiceManager:
    def __init__(self, filter_broker_asker: FilterBrokerAsker, shared_dictionary) -> None:
        self.running_services: dict[str, int] = shared_dictionary
        self.filter_broker_asker = filter_broker_asker
        self.process_death_notifier = Event()  # To notify the class when a process dies
        self.logger = logging.getLogger(__name__)


    def start_service(self, service: Service) -> None:
        process = ServiceProcess(service, self.filter_broker_asker)
        process.start()
        self.running_services[service.name] = process.pid
        logging.error(f"Started service: {process}")


    def stop_service(self, service_name: str) -> None:
        pid = self.running_services.get(service_name)
        if pid is None:
            self.logger.error(f"Service {service_name} not running")
            return

        try:
            os.kill(pid, signal.SIGTERM)  # Send SIGTERM to the process
            del self.running_services[service_name]
            self.logger.info(f"Killed service {service_name} (PID: {pid})")
        except ProcessLookupError:
            self.logger.warning(f"Process {pid} already dead")
            del self.running_services[service_name]
        except Exception as e:
            self.logger.error(f"Failed to kill {service_name}: {str(e)}")

    
    