from uvicorn import run
from .proxy.configuration.constants import EXPOSED_PORT

if __name__ == "__main__":
    run("proxy:app", host="0.0.0.0", port=EXPOSED_PORT, log_level="debug")