"""
Helpers and fixtures for creating and cleaning up author test data.
"""

import random
import uuid
import pytest
from utils.request_handler import APIClient
from config.config import BASE_URL

client = APIClient(BASE_URL)

@pytest.fixture
def generate_author_data():
    """Returns the standalone payload generator function for authors."""
    return generate_author_payload

def generate_author_payload(author_id=None, overrides=None):
    """Creates and returns a fake author payload."""
    base_data = {
        "id": author_id or int(uuid.uuid4().int % 100000),
        "idBook": random.randint(1, 1000),
        "firstName": f"First{uuid.uuid4().hex[:6]}",
        "lastName": f"Last{uuid.uuid4().hex[:6]}"
    }
    if overrides:
        base_data.update(overrides)
    return base_data

@pytest.fixture
def create_and_cleanup_author():
    """
    Creates an author and deletes it after the test.
    Returns a function that takes a payload and posts it.
    """
    created_author_ids = []

    def _create_author(author_payload):
        """Sends POST request to create an author and stores the ID for later cleanupp."""
        response = client.post("/Authors", data=author_payload)
        if response.status_code == 200:
            created_id = response.json().get("id", author_payload.get("id"))
            created_author_ids.append(created_id)
        return response

    yield _create_author

    # Cleanup after test finishes
    for author_id in created_author_ids:
        del_resp = client.delete(f"/Authors/{author_id}")
        assert del_resp.status_code == 200, f"Failed to delete author {author_id}"

def next_available_author_id():
    """Fetches authors and returns the next available author ID."""
    response = client.get("/Authors")
    assert response.status_code == 200, f"Failed to fetch authors. Got {response.status_code}"
    authors = response.json()
    if not authors:
        return 1
    max_id = max(author.get("id", 0) for author in authors if isinstance(author, dict))
    return max_id + 1
