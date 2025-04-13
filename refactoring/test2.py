from threading import Thread
from multiprocessing import Queue, Manager, Process
from dataclasses import dataclass
from typing import Optional
import logging
import inspect
import dill

@dataclass
class Service:
    id: Optional[int] = None
    name: str = ""
    port: int = 0

class Filter:
    def __init__(self, filter_function: callable):
        self.filter_function: callable = filter_function
        self.subscribers: list[Service] = []

    def __call__(self, *args, **kwds):
        return self.filter_function(*args, **kwds)


class FilterBroker(Thread):
    def __init__(self, queue: Queue) -> None:
        super().__init__()
        self.queue = queue
        self.filters: dict[str, Filter] = {}

    def add_filter(self, name: str, filter: Filter):
        if len(inspect.signature(filter).parameters) != 2:
            raise TypeError("Invalid Filter: must have exactly two parameters")
        self.filters[name] = filter

    def get_filter(self, name: str) -> Optional[Filter]:
        return dill.dumps(self.filters[name])

    def run(self):
        class_name = self.__class__.__name__
        logging.info(f"[{class_name}]: Process started")
        while True:
            try:
                task = self.queue.get()
                logging.debug(f"[{class_name}]: Task received: {task}")
                if task is None:
                    break
                response_queue, pickled_task = task
                method, *args = dill.loads(pickled_task)
                response = method(self, *args)
            except Exception:
                import traceback
                traceback.print_exc()
                response = None
            finally:
                if task is not None:
                    response_queue.put_nowait(response)



class FilterBrokerAsker:

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def ask(self, *task):
        pickled_task = dill.dumps(task)
        response_queue = Manager().Queue()
        self.queue.put((response_queue, pickled_task))
        print("I put in queue")
        result = response_queue.get()
        print("I got result")
        return result



def task1(broker):
    class test:
        @staticmethod
        def test_method():
            print("running test method!")
    def function(x):
        print("running test function!")
        print(x)
        test.test_method()
        return x

    f = Filter(function)
    print(f(2))
    broker.ask(FilterBroker.add_filter, 'test', f)
    logging.debug(f"Filter added")


def task2(broker):
    f = broker.ask(FilterBroker.get_filter, 'test')
    f = dill.loads(f)
    print(f(2))
    logging.debug(f"Filter loaded")


if __name__ == "__main__":
    manager = Manager()
    broker = FilterBroker(manager.Queue())
    broker.start()

    broker_data = FilterBrokerAsker(broker.queue)

    process = Process(target=task1, args=(broker_data,))

    process.start()
    process.join()

    process2 = Process(target=task2, args=(broker_data,))
    process2.start()
    process2.join()

    print("Process finished")
    broker.queue.put(None)