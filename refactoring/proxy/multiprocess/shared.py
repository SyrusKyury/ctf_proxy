from multiprocessing import Manager


manager = Manager()
namespace = manager.Namespace()
namespace.config_dictionary = manager.dict()
namespace.lock_config_file = manager.Lock()
namespace.filter_broker_queue = manager.Queue()