from .ServiceClass import Service
from .ServiceProcessFactory import ServiceProcessFactory as spf
from multiprocessing import Process, Event
from ..multiprocess import FilterBrokerAsker
import logging
import time

class ServiceManager:
    def __init__(self, filter_broker_asker: FilterBrokerAsker) -> None:
        self.running_services: dict[Service, Process] = {}
        self.filter_broker_asker = filter_broker_asker
        self.process_death_notifier = Event()  # To notify the class when a process dies
        self.logger = logging.getLogger(__name__)


    def start_service(self, service: Service) -> None:
        process = spf.new_process(service, self.filter_broker_asker)
        self.running_services[service] = process
        process.start()
        self.logger.info(f"Started service: {service}")


    def stop_service(self, service: Service) -> None:
        if service in self.running_services:
            process = self.running_services[service]
            process.terminate()  # or process.kill() depending on how you want to stop it
            process.join()  # Wait for process to terminate
            self.logger.info(f"Stopped service: {service}")
            del self.running_services[service]


    def is_running(self, service: Service) -> bool:
        return service in self.running_services and self.running_services[service].is_alive()


    def check_processes(self):
        """Periodically check if any running process has died."""
        for service, process in list(self.running_services.items()):
            if not process.is_alive():  # If the process is not alive
                self.logger.warning(f"Service {service} has stopped unexpectedly.")
                # Notify the manager or handle process death
                self.handle_process_death(service)


    def handle_process_death(self, service: Service):
        """Handle a service process death."""
        # Here you can implement any cleanup or notifications
        self.logger.error(f"Process for service {service} died unexpectedly.")
        # Optionally, restart the service or take other actions
        # You can restart the service or notify another system
        del self.running_services[service]  # Remove the dead process from the manager


    async def monitor_services(self):
        """Monitor the services to check for any dying processes."""
        while True:
            self.check_processes()
            # Sleep to avoid too frequent checks (optional)
            time.sleep(5)  # Wait for 5 seconds before checking again
