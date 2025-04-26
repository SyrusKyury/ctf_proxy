from multiprocessing import Manager
from .FilterBroker import FilterBroker
from .FilterBrokerAsker import FilterBrokerAsker
from ..service.ServiceManager import ServiceManager

import redis
r = redis.Redis(host="redis", port=6379, decode_responses=True)

manager = Manager()
namespace = manager.Namespace()

broker = FilterBroker(manager.Queue())
asker = FilterBrokerAsker(broker.queue)
service_manager = ServiceManager(asker, manager.dict())