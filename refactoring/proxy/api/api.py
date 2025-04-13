from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from json import load, dump
from typing import Optional

# Local imports
from ..service import Service
from ..multiprocess import namespace
from ..constants import CONFIG_JSON_PATH, TITLE, DESCRIPTION, VERSION
from ..utils import authenticate_request


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function to manage the lifespan of the FastAPI application.
    It initializes data on startup and cleans up on shutdown."""
    try:
        for key, value in load(open(CONFIG_JSON_PATH)).items():
            namespace.config_dictionary[key] = value
        yield
    except Exception as e:
        print(e)


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

    if service.name in namespace.config_dictionary['services']:
        raise HTTPException(status_code=400, detail="Service already exists")
    
    if service.port in [s['port'] for s in namespace.config_dictionary['services'].values()]:
        raise HTTPException(status_code=400, detail="Port already in use")
    
    if service.type == "https" and not ssl_cert:
        raise HTTPException(status_code=400, detail="SSL certificate is required for HTTPS services")

    with namespace.lock_config_file:
        # Add the service to the configuration dictionary
        # I must work on a copy of the dictionary because config_dictionary
        # does not support sub-dictionaries
        services = namespace.config_dictionary.get('services', {})
        services[service.name] = service.model_dump()
        namespace.config_dictionary['services'] = services

        # Save the updated configuration to the JSON file
    
        with open(CONFIG_JSON_PATH, 'w') as config_file:
            dump(dict(namespace.config_dictionary), config_file, indent=4)

    # TODO: Start service
    
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

    if not service_name:
        return JSONResponse(status_code=200, content=dict(namespace.config_dictionary['services']))
    elif service_name in namespace.config_dictionary['services']:
        return JSONResponse(status_code=200, content=dict(namespace.config_dictionary['services'][service_name]))
    else:
        return JSONResponse(status_code=404, content={"message": "Service not found"})


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

