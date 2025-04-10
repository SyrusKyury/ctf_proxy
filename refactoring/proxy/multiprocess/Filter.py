from ..service import Service

class Filter:
    """
    Represents a filtering mechanism used within a proxy to selectively route 
    stream data to subscribed services based on a custom filtering function.

    This class applies a user-defined filter function to incoming Stream objects. 
    If the filter function returns True, the stream is considered relevant, and 
    the proxy may forward it to the subscribed services.

    Attributes:
        filterFunction (callable): A function that takes a Stream object as input 
                                   and returns a boolean indicating whether the 
                                   stream matches the filter condition.
        subscribers (list[Service]): A list of Service instances that are 
                                     subscribed to this filter.

    Methods:
        - add_subscriber(service: Service) -> None:
            Subscribes a service to this filter.

        - remove_subscriber(service: Service) -> None:
            Unsubscribes a service from this filter.

        - is_subscriber(service: Service) -> bool:
            Checks if a service is currently subscribed.

        - get_subscribers() -> list[Service]:
            Returns the list of currently subscribed services.

        - clear_subscribers() -> None:
            Removes all subscribers from the filter.

        - __call__(*args, **kwargs):
            Applies the filter function to the given arguments. Typically used
            to evaluate whether a stream should pass through the proxy.
    """


    def __init__(self, filterFunction : callable):
        """
        Initializes a filter with a filter function and an empty list of subscribers.

        Args:
            filterFunction (callable): a function that takes a Stream object and returns a boolean
        """
        self.filterFunction : callable = filterFunction
        self.subscribers : list[Service] = []

    
    def add_subscriber(self, service : Service) -> None:
        """
        Adds a service to the list of subscribers of the filter.

        Args:
            service (Service): the service to add to the list of subscribers
        """
        self.subscribers.append(service)

    
    def remove_subscriber(self, service : Service) -> None:
        """
        Removes a service from the list of subscribers of the filter.

        Args:
            service (Service): the service to remove from the list of subscribers
        """
        self.subscribers.remove(service)


    def is_subscriber(self, service : Service) -> bool:
        """
        Checks if a given service is subscribed to this filter.

        Args:
            service (Service): the service to check

        Returns:
            bool: True if the service is subscribed, False otherwise
        """
        return service in self.subscribers
    

    def __call__(self, *args, **kwds):
        """
        Calls the filter function with the given arguments and keyword arguments.

        Args:
            *args: the positional arguments to pass to the filter function
            **kwds: the keyword arguments to pass to the filter function

        Returns:
            the result of the filter function
        """
        return self.filterFunction(*args, **kwds)
    

    def get_subscribers(self) -> list[Service]:
        """
        Returns the list of currently subscribed services.

        Returns:
            list[Service]: A copy of the list of subscribers.
        """
        return self.subscribers.copy()


    def clear_subscribers(self) -> None:
        """
        Removes all subscribers from the filter.
        """
        self.subscribers.clear()