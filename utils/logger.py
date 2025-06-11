import logging
import sys

logger = logging.getLogger("books_api")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
console_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(console_handler)

from functools import wraps

def log_request_response(method_name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, endpoint, *args, **kwargs):
            url = f"{self.base_url}{endpoint}"
            headers = kwargs.get("headers", {})
            data = kwargs.get("data", None) or kwargs.get("json", None)

            print(f"Request: {method_name} {url}")
            print(f"Headers: {headers}")
            if data:
                print(f"Payload: {data}")

            response = func(self, endpoint, *args, **kwargs)

            try:
                response_body = response.json() if response.content else None
            except Exception:
                response_body = response.text

            print(f"Response [{response.status_code}]: {response_body}")

            return response
        return wrapper
    return decorator
