from proxy.multiprocess.FilterBroker import FilterBroker as fb
from proxy.multiprocess.Filter import Filter
from multiprocessing import Manager, Process
import logging

logging.basicConfig(level=logging.DEBUG)

manager = Manager()
broker = fb(manager.Queue())
broker.start()



# Funzione del processo
def task(broker):
    func = """
def mammt():
    return 'ueeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
"""
    f = Filter(func)
    print(f())
    fb.ask(broker, fb.add_filter, 'test', Filter(func))
    logging.debug(f"Filter added")


process = Process(target=task, args=(broker,))

process.start()
process.join()

print("Process finished")