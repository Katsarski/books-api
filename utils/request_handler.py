import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.clear()  # Remove all default headers

    def get(self, endpoint, **kwargs):
        headers = kwargs.pop("headers", {})  # allow for sendingcustom headers
        return self.session.get(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    def post(self, endpoint, data=None, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.post(f"{self.base_url}{endpoint}", headers=headers, json=data, **kwargs)

    def put(self, endpoint, data=None, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.put(f"{self.base_url}{endpoint}", headers=headers, json=data, **kwargs)

    def delete(self, endpoint, **kwargs):
        headers = kwargs.pop("headers", {})
        return self.session.delete(f"{self.base_url}{endpoint}", headers=headers, **kwargs)
