import logging
import sys
from functools import wraps

class APILogger:
    def __init__(self, logger=None):
        self.logger = logger or self._default_logger()

    def _default_logger(self):
        logger = logging.getLogger("books_api")
        logger.setLevel(logging.INFO)
        if not logger.hasHandlers():
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
            logger.addHandler(handler)
        return logger

    def log_request_response(self, method_name):
        logger = self.logger

        def decorator(func):
            @wraps(func)
            def wrapper(api_client_self, endpoint, *args, **kwargs):
                url = f"{api_client_self.base_url}{endpoint}"
                headers = kwargs.get("headers", {})
                data = kwargs.get("data", None) or kwargs.get("json", None)
                logger.info(f"Request: {method_name} {url} | Headers: {headers} | Payload: {data}")
                response = func(api_client_self, endpoint, *args, **kwargs)
                try:
                    response_body = response.json() if response.content else None
                except Exception:
                    response_body = response.text
                logger.info(f"Response [{response.status_code}]: {response_body}")
                return response
            return wrapper
        return decorator

default_api_logger = APILogger()