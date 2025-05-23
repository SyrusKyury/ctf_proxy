from pydantic import BaseModel, Field

class Service(BaseModel):
    """
    Represents a network service configuration, including both listening and target information.

    Attributes:
        name (str): A unique name identifying the service.
        target_ip (str): The IP address of the target service to forward traffic to.
        port (int): The port on which the service listens for incoming traffic and forwards to the target.
        type (str): The service type, which can be 'http', 'https', or 'tcp'.
        active (bool): Indicates whether the service is currently proxied.
    """

    name: str
    port: int
    type: str = Field(..., pattern="^(http|https|tcp)$")
    active: bool

    def __hash__(self):
        """
        Computes a hash value for the Service object based on its attributes.

        Returns:
            int: The computed hash value.
        """
        return hash((
            self.name, self.port,
            self.type, self.active
        ))


    def __eq__(self, other):
        """
        Compares two Service objects for equality.

        Args:
            other (Service): The other service instance to compare.

        Returns:
            bool: True if both objects are equal, False otherwise.
        """
        return isinstance(other, Service) and hash(self) == hash(other)


    def json_dump_for_settings(self) -> dict:
        """
        Converts the Service object to a dictionary format suitable for JSON serialization.

        Returns:
            dict: The dictionary representation of the Service object.
        """
        return {
            "port": self.port,
            "type": self.type,
            "active": self.active
        }