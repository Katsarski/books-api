"""
API Client Module

Defines APIClient for making HTTP requests with automatic logging of
requests and responses using a configurable logger.
"""

import requests
from utils.logger import default_api_logger

class APIClient:
    """
    Simple API client for sending HTTP requests with logging of requests and responses.
    """
    def __init__(self, base_url, api_logger=default_api_logger):
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to call (appended to base_url).
            **kwargs: Additional arguments passed to requests.Session.get (e.g., params, headers).

        Returns:
            requests.Response: The response object.
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.clear()
        self._api_logger = api_logger

    @default_api_logger.log_request_response("GET")
    def get(self, endpoint, **kwargs):
        """
        Sends a GET request to the specified endpoint.
        """
        headers = kwargs.pop("headers", {})
        return self.session.get(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    @default_api_logger.log_request_response("POST")
    def post(self, endpoint, data=None, **kwargs):
        """
        Sends a POST request with JSON payload to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to call (appended to base_url).
            data (dict, optional): The JSON-serializable payload to send. Defaults to None.
            **kwargs: Additional arguments passed to requests.Session.post (e.g., headers).

        Returns:
            requests.Response: The response object.
        """
        headers = kwargs.pop("headers", {})
        return self.session.post(f"{self.base_url}{endpoint}", headers=headers, json=data, **kwargs)

    @default_api_logger.log_request_response("PUT")
    def put(self, endpoint, data=None, **kwargs):
        """
        Sends a PUT request with JSON payload to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to call (appended to base_url).
            data (dict, optional): The JSON-serializable payload to send. Defaults to None.
            **kwargs: Additional arguments passed to requests.Session.put (e.g., headers).

        Returns:
            requests.Response: The response object.
        """
        headers = kwargs.pop("headers", {})
        return self.session.put(f"{self.base_url}{endpoint}", headers=headers, json=data, **kwargs)

    @default_api_logger.log_request_response("DELETE")
    def delete(self, endpoint, **kwargs):
        """
        Sends a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to call (appended to base_url).
            **kwargs: Additional arguments passed to requests.Session.delete (e.g., headers).

        Returns:
            requests.Response: The response object.
        """
        headers = kwargs.pop("headers", {})
        return self.session.delete(f"{self.base_url}{endpoint}", headers=headers, **kwargs)
