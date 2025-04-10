from proxy.multiprocess.FilterBroker import FilterBroker as fb
from proxy.multiprocess.Filter import Filter
from multiprocessing import Queue, Process
import logging

logging.basicConfig(level=logging.DEBUG)

_filter = Filter(lambda x : x + 1)
broker = fb(Queue())
broker.start()


# Funzione del processo
def task(broker):
    result = fb.ask(broker, fb.add_filter, 'test', _filter)
    logging.debug(f"Filter added: {result}")


process = Process(target=task, args=(broker,))

process.start()
process.join()
