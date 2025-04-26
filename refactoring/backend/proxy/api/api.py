from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from json import load, loads, dump
from typing import Optional
import logging

# Local imports
from ..service import Service, NGINXConfigurationManager
from ..multiprocess import redis_connection, service_manager
from ..constants import CONFIG_JSON_PATH, TITLE, DESCRIPTION, VERSION
from ..utils import authenticate_request
from ..service import SSHManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function to manage the lifespan of the FastAPI application.
    It initializes data on startup and cleans up on shutdown."""
    try:
        settings = load(open(CONFIG_JSON_PATH))
        for key, value in settings["services"].items():
            redis_connection.hset(key, mapping=value)
        

        for key, value in settings["global_config"].items():
            logging.debug(f"Setting {key} to {value}")
            if isinstance(value, dict):
                redis_connection.hset(key, mapping=value)
            else:
                redis_connection.set(key, value)
            logging.debug(f"Set {key} to {value} in Redis")
        
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
    authenticate_request(request)

    # Validate the service object
    service_keys = redis_connection.keys("services:*")

    for key in service_keys:
        service_data = redis_connection.hgetall(key)
        logging.debug(f"Service data: {service_data}")
        if service_data.get("name") == service.name:
            raise HTTPException(status_code=400, detail="Service already exists")
        
        if service_data.get("port") == str(service.port):
            raise HTTPException(status_code=400, detail="Port already in use")
        
    
    if service.type == "https" and not ssl_cert:
        raise HTTPException(status_code=400, detail="SSL certificate is required for HTTPS services")


    # TODO: Creare un meccanismo per invertire le modifiche in caso di errore
    redis_connection.hset(f"services:{service.name}", mapping=loads(service.model_dump_json()))

    service_manager.start_service(service)
    #NGINXConfigurationManager.write_nginx_conf()

    try:
        pass
        #SSHManager.add_ip_table(service.port)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add iptables rule: {e}")
    
    
    
    return JSONResponse(status_code=201, content={"message": "Service created successfully"})



@app.delete("/service/{service_name}")
async def delete_service(service_name: str, request: Request):
    authenticate_request(request)

    if not service_name:
        raise HTTPException(status_code=400, detail="Service name is required")
    
    # TODO: Stop service
    

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

