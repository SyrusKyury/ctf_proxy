from proxy.multiprocess.FilterBroker import FilterBroker
from proxy.multiprocess.FilterBrokerAsker import FilterBrokerAsker
from proxy.multiprocess.Filter import Filter
from proxy.service import Service
from multiprocessing import Manager
from multiprocessing import Process


def add_filter(asker : FilterBrokerAsker):
    def filter_function(x, y):
        print("This is a filter function")
        return x + y

    f = Filter(filter_function)
    asker.ask(FilterBroker.add_filter, 'test', f)



def get_filter(asker : FilterBrokerAsker):
    service = Service(name='test service', port=8080, type='http')
    for f in asker.ask(FilterBroker.get_subscribed_filters, service):
        print(f(2,3))



def subscribe(asker : FilterBrokerAsker):
    service = Service(name='test service', port=8080, type='http')
    asker.ask(FilterBroker.subscribe_service, service, 'test')



if __name__ == "__main__":
    manager = Manager()
    broker = FilterBroker(manager.Queue())
    asker = FilterBrokerAsker(broker.queue)
    broker.start()

    add_filter_process = Process(target=add_filter, args=(asker,))
    add_filter_process.start()
    add_filter_process.join()

    subscribe_process = Process(target=subscribe, args=(asker,))
    subscribe_process.start()
    subscribe_process.join()

    get_filter_process = Process(target=get_filter, args=(asker,))
    get_filter_process.start()
    get_filter_process.join()



    
    broker.queue.put(None)



