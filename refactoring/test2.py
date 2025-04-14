from proxy.service import ServiceManager
from proxy.service import Service
from proxy.multiprocess import FilterBrokerAsker, FilterBroker, Filter
from multiprocessing import Manager
import time
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":

    def filter_function(x, y):
        logging.info("This is a filter function")
        return x + y
    
    fb : FilterBroker = FilterBroker(Manager().Queue())
    fba : FilterBrokerAsker = FilterBrokerAsker(fb.queue)
    sm : ServiceManager = ServiceManager(fba)
    filter : Filter.Filter = Filter.Filter(filter_function)
    fb.start()

    test_service : Service = Service(name = "Test service", port=2222, type="tcp")
    
    fba.ask(FilterBroker.add_filter, "Test filter", filter)
    logging.info(">> Filter added")

    fba.ask(FilterBroker.subscribe_service, test_service, "Test filter")
    logging.info(">> Service subscribed to filter")

    logging.info(">> Starting service")
    sm.start_service(test_service)
    logging.info(">> Service started")

    time.sleep(10)

    logging.info(">> Stopping service")
    sm.stop_service(service=test_service)
    logging.info(">> Service stopped")
    time.sleep(5)
    logging.info(">> Stopping broker")
    fb.queue.put(None)
    fb.join()
    logging.info("Broker stopped")