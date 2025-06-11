import pytest
import random
import uuid
from datetime import datetime
from utils.request_handler import APIClient
from config.config import BASE_URL

client = APIClient(BASE_URL)

@pytest.fixture
def generate_book_data():
    """Returns the standalone payload generator function."""
    return generate_book_payload

def generate_book_payload(book_id=None, overrides=None):
    """Standalone payload generator, independent of any fixture."""
    base_data = {
        "id": book_id or int(uuid.uuid4().int % 100000),
        "title": f"Book Title {uuid.uuid4().hex[:6]}",
        "description": f"Description {uuid.uuid4().hex[:10]}",
        "pageCount": random.randint(50, 1000),
        "excerpt": f"Excerpt text {uuid.uuid4().hex[:8]}",
        "publishDate": datetime.now().isoformat() + "Z",
    }
    if overrides:
        base_data.update(overrides)
    return base_data

@pytest.fixture
def next_available_book_id():
    """Returns the next available book ID."""
    response = client.get("/Books")
    assert response.status_code == 200, f"Failed to fetch books. Got {response.status_code}"
    books = response.json()
    if not books:
        return 1
    max_id = max(book.get("id", 0) for book in books if isinstance(book, dict))
    return max_id + 1

@pytest.fixture
def create_and_cleanup_book():
    """
    Fixture to create a book given a payload and clean it up after the test.
    Returns the response object from the POST call.
    """
    created_book_ids = []

    def _create_book(book_payload):
        response = client.post("/Books", data=book_payload)
        if response.status_code == 200:
            created_id = response.json().get("id", book_payload.get("id"))
            created_book_ids.append(created_id)
        return response

    yield _create_book

    # Cleanup after test finishes
    for book_id in created_book_ids:
        del_resp = client.delete(f"/Books/{book_id}")
        assert del_resp.status_code == 200, f"Failed to delete book {book_id}"