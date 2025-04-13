from multiprocessing import Manager, Queue
import dill

class FilterBrokerAsker:

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def ask(self, *task):
        pickled_task = dill.dumps(task)
        response_queue = Manager().Queue()
        self.queue.put((response_queue, pickled_task))
        result = response_queue.get()
        if result:
            result = dill.loads(result)
        return result