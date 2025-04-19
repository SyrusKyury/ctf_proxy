import inspect
import logging
import dill
from .Filter import Filter
from ..service import Service

from threading import Thread
from multiprocessing import Queue, Manager

class FilterBroker(Thread):
    """
    A broker for managing filters and their subscriptions.

    The FilterBroker class is responsible for storing filters and managing 
    the subscription of services to those filters. Filters are stored in a 
    dictionary with the filter name as the key and the filter object as the 
    value. Services can subscribe or unsubscribe to specific filters.

    Attributes:
        filters (dict[str, Filter]): A dictionary storing filters by their names.

    Methods:
        - __init__(): Initializes an empty filter broker.
        - add_filter(name: str, filter: Filter): Adds a filter to the broker.
        - remove_filter(name: str): Removes a filter from the broker.
        - get_filter(name: str): Retrieves a filter by its name.
        - get_subscribed_filters(service: Service): Returns a list of filters the 
            given service is subscribed to.
        - subscribe_service(service: Service, filter_name: str = None, filter: Filter = None): 
            Subscribes a service to a filter.
        - unsubscribe_service(service: Service, filter_name: str = None, filter: Filter = None): 
            Unsubscribes a service from a filter.
        - unsubscribe_all(service: Service): Unsubscribes a service from all filters.
        - list_filters(): Returns a list of all filter names.
        - get_subscribers_count(filter_name: str): Returns the number of subscribers 
            for a specific filter.
        - is_service_subscribed(service: Service, filter_name: str): Checks if a service is 
            subscribed to a given filter.
        - get_all_subscribed_services(): Retrieves all unique services subscribed to any filter.
        - clear_all_filters(): Clears all filters from the broker and unsubscribes all services.
        - filter_exists(name: str): Checks if a filter with the specified name exists in the broker.
    """


    def __init__(self, queue : Queue) -> None:
        super().__init__()
        self.queue = queue
        self.filters: dict[str, Filter] = {}


    def add_filter(self, name: str, filter: Filter):
        """
        Adds a filter to the filter broker.

        Args:
            name (str): The name of the filter.
            filter (Filter): The filter object to be added.

        Raises:
            TypeError: If the filter does not have exactly two parameters.
        """
        # Check if the filter function has exactly two parameters
        if len(inspect.signature(filter).parameters) != 2:
            raise TypeError("Invalid Filter: must have exactly two parameters")
        
        # Add the filter to the dictionary of filters
        self.filters[name] = filter


    def remove_filter(self, name: str):
        """
        Removes a filter from the filter broker.

        Args:
            name (str): The name of the filter to remove.

        Raises:
            KeyError: If the filter with the given name does not exist.
        """
        if name in self.filters:
            del self.filters[name]
        else:
            raise KeyError(f"Filter '{name}' not found.")
    

    def get_filter(self, name: str):
        """
        Returns the filter with the given name.

        Args:
            name (str): The name of the filter to retrieve.

        Returns:
            Filter: The filter with the given name.

        Raises:
            KeyError: If the filter with the given name does not exist.
        """
        if name in self.filters:
            return self.filters[name]
        else:
            raise KeyError(f"Filter '{name}' not found.")
    

    def get_subscribed_filters(self, service: Service):
        """
        Returns a list of filters that the given service is subscribed to.

        Args:
            service (Service): The service to check for subscriptions.

        Returns:
            list[Filter]: A list of filters that the given service is subscribed to.
        """
        return [filter for filter in self.filters.values() if filter.is_subscriber(service)]
    

    def subscribe_service(self, service: Service, filter_name: str = None, filter: Filter = None):
        """
        Subscribes a service to a specified filter.

        Args:
            service (Service): The service to subscribe.
            filter_name (str, optional): The name of the filter to subscribe to. Defaults to None.
            filter (Filter, optional): The filter object to subscribe to. Defaults to None.

        Raises:
            TypeError: If neither filter_name nor filter instance is provided.
        """
        if filter_name:
            self.filters[filter_name].add_subscriber(service)
        elif filter:
            filter.add_subscriber(service)
        else:
            raise TypeError("Filter name or filter instance must be provided")
    
    
    def unsubscribe_service(self, service: Service, filter_name: str = None, filter: Filter = None):
        """
        Unsubscribes a service from a specified filter.

        Args:
            service (Service): The service to unsubscribe.
            filter_name (str, optional): The name of the filter to unsubscribe from. Defaults to None.
            filter (Filter, optional): The filter object to unsubscribe from. Defaults to None.

        Raises:
            TypeError: If neither filter_name nor filter instance is provided.
        """
        if filter_name:
            self.filters[filter_name].remove_subscriber(service)
        elif filter:
            filter.remove_subscriber(service)
        else:
            raise TypeError("Filter name or filter instance must be provided")
    
    
    def unsubscribe_all(self, service: Service):
        """
        Unsubscribes the given service from all filters.
        """
        for filter in self.filters.values():
            filter.remove_subscriber(service)

    
    def list_filters(self):
        """
        Returns a list of all filter names currently managed by the filter broker.

        Returns:
            list[str]: A list of filter names.
        """
        return list(self.filters.keys())


    def get_subscribers_count(self, filter_name: str):
        """
        Returns the number of subscribers for a given filter.

        Args:
            filter_name (str): The name of the filter to retrieve subscriber count for.

        Returns:
            int: The number of subscribers associated with the specified filter.

        Raises:
            KeyError: If the filter with the given name does not exist.
        """
        if filter_name in self.filters:
            return len(self.filters[filter_name].subscribers)
        else:
            raise KeyError(f"Filter '{filter_name}' not found.")
    

    def is_service_subscribed(self, service: Service, filter_name: str):
        """
        Checks if a given service is subscribed to a given filter.

        Args:
            service (Service): The service to check for subscription.
            filter_name (str): The name of the filter to check for subscription.

        Returns:
            bool: True if the service is subscribed to the filter, False otherwise.

        Raises:
            KeyError: If the filter with the given name does not exist.
        """
        
        if filter_name in self.filters:
            return self.filters[filter_name].is_subscriber(service)
        return False


    def get_all_subscribed_services(self):
        """
        Retrieves a list of all unique services subscribed to any filter.

        Returns:
            list[Service]: A list of unique services that are subscribed to at least one filter.
        """
        services = set()
        for filter in self.filters.values():
            services.update(filter.subscribers)
        return list(services)
    
    
    def clear_all_filters(self):
        """
        Clears all filters from the broker, unsubscribing all services from all filters.
        
        This method is used when resetting the proxy to its initial state.
        """
        self.filters.clear()


    def filter_exists(self, name: str):
        """
        Checks if a filter with the given name exists in the broker.

        Args:
            name (str): The name of the filter to check.

        Returns:
            bool: True if the filter exists, False otherwise.
        """
        return name in self.filters
    
    def print(*args):
        """
        Prints the provided arguments to the console.
        
        Args:
            *args: The arguments to print.
        """
        print("TEST")
    

    def run(self):
        """
        Executes tasks from the queue in a loop until a termination signal is received.
        This method continuously retrieves tasks from the queue and processes them.
        Each task is expected to be a tuple containing a callable method, a response
        queue, and optional arguments. The callable method is executed with the
        current instance (`self`) and the provided arguments, and its result is
        placed into the response queue.
        The loop terminates when a `None` task is retrieved from the queue.
        Exceptions during task execution are caught and can be handled (e.g., logged).
        Raises:
            Exception: If an error occurs during task execution it returns None
        """
        class_name = self.__class__.__name__
        logging.info(f"[{class_name}]: Process started")
        while True:
            try:
                task = self.queue.get()
                if task is None:
                    break
                
                response_queue, pickled_task = task
                method, *args = dill.loads(pickled_task)
                response = method(self, *args)

                if response:
                    response = dill.dumps(response)

            except Exception as e:
                response = None
            finally:
                if task is not None:
                    response_queue.put_nowait(response)



    @staticmethod
    def ask(fb : 'FilterBroker', *task):
        response_queue = Manager().Queue()
        fb.queue.put((response_queue, *task))
        print("I put in queue")
        result = response_queue.get()
        print("I got result")
        return result
        

        
