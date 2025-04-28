from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from json import load, loads, dump, dumps
from typing import Optional
import logging

# Local imports
from ..service import Service, NGINXConfigurationManager
from ..multiprocess import service_manager, namespace
from ..configuration.constants import CONFIG_JSON_PATH, TITLE, DESCRIPTION, VERSION
from ..configuration.proxyConfigurationManager import ProxyConfigurationManager
from ..utils import authenticate_request
from ..service import SSHManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function to manage the lifespan of the FastAPI application.
    It initializes data on startup and cleans up on shutdown."""
    try:
        settings = ProxyConfigurationManager.load_configuration()
        # TODO: Load the configuration from a JSON file
        yield
        # TODO: Save the configuration to a JSON file
    except Exception as e:
        logging.error(f"Error during lifespan management: {e}")


app = FastAPI(lifespan=lifespan, title=TITLE, description=DESCRIPTION, version=VERSION)


@app.put("/service")
async def put_service(service: Service, request: Request, ssl_cert: Optional[str] = None):
    """
    Handles the creation of a new service by adding it to the configuration dictionary
    and saving the updated configuration to a JSON file.
    Args:
        service (Service): The service object containing details such as name, port, and type.
        request (Request): The HTTP request object, used for authentication.
    Raises:
        HTTPException: If the service name, port, or type is missing.
        HTTPException: If the service already exists in the configuration.
    Returns:
        JSONResponse: A response indicating the successful creation of the service.
    """
    # Check if the request is authenticated
    # TODO: Creare un meccanismo per invertire le modifiche in caso di errore
    # TODO: Gestire la variabile active
    
    authenticate_request(request)

    if service.type == "https" and not ssl_cert:
        raise HTTPException(status_code=400, detail="SSL certificate is required for HTTPS services")

    # Lock to avoid conflicts when multiple requests are made
    with namespace.service_lock:

        if not ProxyConfigurationManager.service_can_be_added(service):
            raise HTTPException(status_code=400, detail="There is already a service with the same name or port")
        

        # Get a port to expose the nginx proxy
        nginx_port : int = SSHManager.get_unused_port()

        # Stores the service information in the configuration file
        try:
            ProxyConfigurationManager.store_service_information(service, nginx_port)
        except Exception as e:
            ProxyConfigurationManager.remove_service_information(service)
            raise HTTPException(status_code=500, detail=f"Failed to store service information: {e}")

        # Start the service through the service manager
        service_manager.start_service(service)

        # Update the NGINX configuration to include the new service
        NGINXConfigurationManager.write_nginx_conf()

        try:
            SSHManager.add_ip_table(service.port, nginx_port)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add iptables rule: {e}")
    
    
    return JSONResponse(status_code=201, content={"message": "Service created successfully"})



@app.delete("/service/{service_name}")
async def delete_service(request: Request, service_name: str):
    authenticate_request(request)

    if not service_name:
        raise HTTPException(status_code=400, detail="Service name is required")

    with namespace.service_lock:
        # Check if the service exists in the configuration
        service_json = ProxyConfigurationManager.get_service_information(service_name)

        if not service_json:
            raise HTTPException(status_code=404, detail="Service not found")

        # Stop the service through the service manager
        # TODO: It doesn't stop the process
        service_manager.stop_service(service_name)

        try:
            ProxyConfigurationManager.remove_service_information(service_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove service information: {e}")

        # Update the NGINX configuration to remove the service
        NGINXConfigurationManager.write_nginx_conf()

        # Remove iptables rule
        try:
            SSHManager.remove_ip_table(service_json["port"], service_json["nginx_port"])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove iptables rule: {e}")
        
    return JSONResponse(status_code=200, content={"message": "Service deleted successfully"})
    

@app.get("/service")
async def get_service(request: Request, service_name: Optional[str] = None):
    """
    Handles the retrieval of service information based on the provided service name.
    Args:
        request (Request): The incoming HTTP request object.
        service_name (Optional[str], optional): The name of the service to retrieve. Defaults to None.
    Returns:
        JSONResponse: 
            - If no service_name is provided, returns a 200 response with the full list of services.
            - If the service_name exists in the configuration, returns a 200 response with the service details.
            - If the service_name does not exist, returns a 404 response with an error message.
    """

    authenticate_request(request)


@app.patch("/service")
async def patch_service(request: Request, service_name : str, service: Service):
    """
    Handles the update of an existing service in the configuration dictionary.
    Args:
        request (Request): The HTTP request object, used for authentication.
        service_name (str): The name of the service to be updated.
        service (Service): The updated service object containing new details.
    Raises:
        HTTPException: If the service name is not provided or the service does not exist.
    Returns:
        JSONResponse: A response indicating the successful update of the service.
    """

    authenticate_request(request)

    # TODO: Stop service

    return JSONResponse(status_code=200, content={"message": "Service updated successfully"})

