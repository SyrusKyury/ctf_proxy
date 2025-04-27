from multiprocessing import Manager
from .FilterBroker import FilterBroker
from .FilterBrokerAsker import FilterBrokerAsker
from ..service.ServiceManager import ServiceManager

manager = Manager()
namespace = manager.Namespace()

# This lock is used to synchronize access to the API that
# modifies the configuration of the services
namespace.service_lock = manager.Lock()

broker = FilterBroker(manager.Queue())
asker = FilterBrokerAsker(broker.queue)
service_manager = ServiceManager(asker, manager.dict())