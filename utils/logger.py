"""
API Logger Module

Logs HTTP requests and responses for API clients to aid debugging.
"""

import json
import logging
import sys
from functools import wraps

class APILogger:
    """
    A logger class to log HTTP requests and responses for API clients.

    This class provides a decorator to wrap API client methods, automatically logging
    the request details (method, URL, headers, payload) and the response details
    (status code and body).

    Attributes:
        logger (logging.Logger): The underlying logger instance.
    """

    def __init__(self, logger=None):
        """
        Initialize the APILogger with an optional custom logger.

        Args:
            logger (logging.Logger, optional): A pre-configured logger instance.
                If not provided, a default logger named 'books_api' is created.
        """
        self.logger = logger or self._default_logger()

    def _default_logger(self):
        """
        Create and configure the default logger instance.

        Sets the log level to INFO and adds a stream handler to output logs
        to standard output (console) with a specific format.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger("books_api")
        logger.setLevel(logging.INFO)
        if not logger.hasHandlers():
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
            logger.addHandler(handler)
        return logger

    def log_request_response(self, method_name):
        """
        Decorator to log details of an HTTP request and its response.

        Wraps an API client method to log the HTTP method, URL, headers,
        payload (data or JSON), response status code, and response body.

        Args:
            method_name (str): The HTTP method name (e.g., 'GET', 'POST', 'PUT', 'DELETE')
                used in the logged message.

        Returns:
            function: The wrapped function with logging enabled.
        """
        logger = self.logger

        def decorator(func):
            """
            Decorator function that wraps an API client method to log the HTTP request and response.

            Args:
                func (function): The API client method to wrap (e.g., get, post, put).

            Returns:
                function: The wrapped function that logs request and response details.
            """
            @wraps(func)
            def wrapper(api_client_self, endpoint, *args, **kwargs):
                """
                Wrapper function that logs request details before calling the original method,
                then logs response details afterward.

                Args:
                    api_client_self: The instance of the API client making the request.
                    endpoint (str): The API endpoint being called.
                    *args: Additional positional arguments to pass to the original method.
                    **kwargs: Additional keyword arguments to pass, may include headers, data, json, etc.

                Returns:
                    Response: The response object returned by the original API client method.
                """
                url = f"{api_client_self.base_url}{endpoint}"
                headers = kwargs.get("headers", {})
                data = kwargs.get("data", None) or kwargs.get("json", None)
                logger.info(f"Request: {method_name} {url} | Headers: {headers} | Payload: {data}")
                response = func(api_client_self, endpoint, *args, **kwargs)
                try:
                    response_body = response.json() if response.content else None
                except json.JSONDecodeError:
                    response_body = response.text
                logger.info(f"Response [{response.status_code}]: {response_body}")
                return response
            return wrapper
        return decorator

default_api_logger = APILogger()
