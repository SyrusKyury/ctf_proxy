from multiprocessing import Manager, Lock
from multiprocessing.managers import SyncManager, DictProxy


manager : SyncManager = Manager()
config_dictionary : DictProxy = manager.dict()
lock_config_file = Lock()