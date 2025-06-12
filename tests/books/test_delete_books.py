"""
Tests for DELETE /books and /books/{id}, covering existing, non-existent, and invalid IDs.
"""

import pytest
from tests.books.conftest import next_available_book_id
from config.config import BASE_URL
from schemas.bad_request_schema import bad_request_schema
from utils.schema_validator import replace_placeholder, validate_single_object
from utils.request_handler import APIClient

client = APIClient(BASE_URL)
BASE_PATH = "/Books"

@pytest.mark.xfail(strict=True, reason="Known bug where we get 200 OK when getting a book that has been deleted")
def test_delete_existing_book(generate_book_data):
    """Test deleting an existing book and verify it is no longer accessible."""
    book_payload = generate_book_data(book_id=next_available_book_id())
    create_resp = client.post(BASE_PATH, data=book_payload)
    assert create_resp.status_code == 200, \
    f"Expected 200 status code for book creation but got {create_resp.status_code}"

    book_id = create_resp.json()["id"]

    get_resp = client.get(f"{BASE_PATH}/{book_id}")
    assert get_resp.status_code == 200, \
    f"Expected 200 status code for existing book but got {get_resp.status_code}"

    delete_resp = client.delete(f"{BASE_PATH}/{book_id}")
    assert delete_resp.status_code == 200, \
    f"Expected 200 status code for deletion but got {delete_resp.status_code}"

    get_resp = client.get(f"{BASE_PATH}/{book_id}")
    assert get_resp.status_code == 404, \
    f"Expected 404 status code after deletion but got {get_resp.status_code}"

@pytest.mark.xfail(strict=True, reason="Known bug where we are able to delete non-existent book")
def test_delete_non_existent_book():
    """Test deleting a non-existent book returns 404 status code."""
    response = client.delete(f"{BASE_PATH}/-100")
    assert response.status_code == 404, \
    f"Expected 404 status code for non-existent book but got {response.status_code}"

@pytest.mark.parametrize("book_id", [
    "abc",
    "123abc",
    pytest.param("!@#$%", marks=pytest.mark.xfail(strict=False, reason="Known bug for '!@#$%'")),
    pytest.param(" ", marks=pytest.mark.xfail(strict=False, reason="Known bug for space character")),
    12.34,
    "None",
    "1; DROP TABLE Books;",
    "<script>",
    9999999999999999
])
def test_delete_invalid_book_id(book_id):
    """
    Test deleting a book with invalid IDs returns a 400 status code 
    and the proper error message.
    """
    response = client.delete(f"{BASE_PATH}/{book_id}")
    assert response.status_code == 400, \
    f"Expected 400 status code for book_id={book_id} but got {response.status_code}"

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{book_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error, \
    f"Expected error message '{expected_error}' but got '{actual_error}'"
