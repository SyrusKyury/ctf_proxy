from multiprocessing import Manager
from .FilterBroker import FilterBroker
from .FilterBrokerAsker import FilterBrokerAsker

manager = Manager()

namespace = manager.Namespace()

namespace.config_dictionary = manager.dict()
namespace.lock_config_file = manager.Lock()

namespace.process_list = manager.list()

broker = FilterBroker(manager.Queue())
asker = FilterBrokerAsker(broker.queue)
