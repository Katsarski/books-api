import requests
from utils.logger import default_api_logger

class APIClient:
    def __init__(self, base_url, api_logger=default_api_logger):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.clear()
        self._api_logger = api_logger

    @default_api_logger.log_request_response("GET")
    def get(self, endpoint, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.get(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    @default_api_logger.log_request_response("POST")
    def post(self, endpoint, data=None, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.post(f"{self.base_url}{endpoint}", headers=headers, json=data, **kwargs)

    @default_api_logger.log_request_response("PUT")
    def put(self, endpoint, data=None, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.put(f"{self.base_url}{endpoint}", headers=headers, json=data, **kwargs)

    @default_api_logger.log_request_response("DELETE")
    def delete(self, endpoint, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.delete(f"{self.base_url}{endpoint}", headers=headers, **kwargs)