"""
Tests for PUT /books and /books/{id} with valid, invalid, and non-existent IDs.
Includes data validation and content-type handling.
"""

from datetime import datetime
import random
import pytest
from config.config import BASE_URL
from tests.books.conftest import next_available_book_id
from schemas.bad_request_schema import bad_request_schema
from schemas.books_schema import books_object_schema
from schemas.unsupported_media_type_schema import unsupported_media_type_schema
from utils.schema_validator import replace_placeholder, validate_single_object
from utils.request_handler import APIClient

client = APIClient(BASE_URL)
BASE_PATH = "/Books"

@pytest.mark.xfail(strict=True, reason="Known bug where the API doesn't seem to handle updates correctly")
@pytest.mark.parametrize("property_to_update, new_value", [
    ("title", "new title"),
    ("description", "new description"),
    ("pageCount", random.randint(1, 1000)),
    ("excerpt", "new excerpt"),
    ("publishDate", datetime.now().isoformat(timespec='microseconds').rstrip('0') + 'Z')
])
def test_put_update_existing_book(property_to_update, new_value, generate_book_data, create_and_cleanup_book):
    """Test updating an existing book's property succeeds and validates the response schema."""
    next_book_id = next_available_book_id()
    book_payload = generate_book_data(book_id=next_book_id)
    create_and_cleanup_book(book_payload)

    updated_payload = book_payload.copy()
    updated_payload[property_to_update] = new_value

    response = client.put(f"{BASE_PATH}/{next_book_id}", data=updated_payload)
    assert response.status_code == 200, \
    f"Expected 200 status code for updating book but got {response.status_code}"
    validate_single_object(response.json(), books_object_schema)

    assert response.json()[property_to_update] == new_value, \
    f"Expected {property_to_update} to be updated to {new_value} but got {response.json()[property_to_update]}"

    get_resp = client.get(f"{BASE_PATH}/{next_book_id}")
    assert get_resp.status_code == 200, \
    f"Expected 200 status code for retrieving updated book but got {get_resp.status_code}"

    assert response.json()[property_to_update] == new_value, \
    f"Expected {property_to_update} to be {new_value} after update but got {response.json()[property_to_update]}"

@pytest.mark.xfail(strict=True, reason="Known bug where we are able to update non-existent books")
def test_put_non_existent_book(generate_book_data):
    """Test updating a non-existent book returns 404 status code."""
    next_book_id = next_available_book_id()
    get_resp = client.get(f"{BASE_PATH}/{next_book_id}")
    assert get_resp.status_code == 404, \
    f"Expected 404 status code for non-existent book but got {get_resp.status_code}"

    response = client.put(f"{BASE_PATH}/{next_book_id}", data=generate_book_data(next_book_id))
    assert response.status_code == 404, \
    f"Expected 404 status code for updating non-existent book but got {response.status_code}"

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
def test_put_invalid_book_id(book_id, generate_book_data):
    """Test updating a book with invalid book ID returns 400 status code with appropriate error schema and message."""
    book_payload = generate_book_data()
    response = client.put(f"{BASE_PATH}/{book_id}", data=book_payload)
    assert response.status_code == 400, \
    f"Expected 400 status code for book_id={book_id} but got {response.status_code}"

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{book_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error, \
    f"Expected error message '{expected_error}' but got '{actual_error}'"

@pytest.mark.parametrize("property_name, value, expected_type", [
    ("id", "not_a_number", "System.Int32"),
    ("title", 123, "System.String"),
    ("description", 123, "System.String"),
    ("excerpt", 123, "System.String"),
    ("pageCount", "not_a_number", "System.Int32"),
    ("publishDate", "not_a_number", "System.DateTime")
])
def test_put_invalid_book_data(property_name, value, expected_type, generate_book_data, create_and_cleanup_book):
    """
    Test updating a book with invalid property data returns 400 status code, 
    validates error schema, and checks for expected error message.
    """
    next_book_id = next_available_book_id()
    book_payload = generate_book_data(book_id=next_book_id)
    response = create_and_cleanup_book(book_payload)
    book_id = response.json()["id"]

    overrides = {property_name: value}
    updated_payload = book_payload.copy()
    updated_payload.update(overrides)

    response = client.put(f"{BASE_PATH}/{book_id}", data=updated_payload)
    assert response.status_code == 400, \
    f"Expected 400 status code for book with invalid {property_name} but got {response.status_code}"

    bad_request_schema_modified = replace_placeholder(bad_request_schema, f"$.{property_name}")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The JSON value could not be converted to {expected_type}. Path: $.{property_name}"
    actual_error = response.json().get("errors", {}).get(f"$.{property_name}")[0]
    assert expected_error in actual_error, \
    f"Expected error message '{expected_error}' but got '{actual_error}'"

def test_put_book_invalid_content_type(generate_book_data, create_and_cleanup_book):
    """Test updating a book with invalid Content-Type header returns 415 status code and validates error schema."""
    next_book_id = next_available_book_id()
    book_payload = generate_book_data(book_id=next_book_id)
    create_and_cleanup_book(book_payload)

    updated_payload = book_payload.copy()
    updated_payload["title"] = "Updated Title"

    invalid_headers = {"Content-Type": "text/plain"}
    response = client.put(f"{BASE_PATH}/{next_book_id}", data=updated_payload, headers=invalid_headers)
    validate_single_object(response.json(), unsupported_media_type_schema)
    assert response.status_code == 415, \
    f"Expected 400 or 415 status code but got {response.status_code}"
