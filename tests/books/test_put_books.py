from datetime import datetime
import random
import pytest
from schemas.unsupported_media_type_schema import unsupported_media_type_schema
from utils.request_handler import APIClient
from config.config import BASE_URL
from schemas.books_schema import books_object_schema
from schemas.bad_request_schema import bad_request_schema
from utils.schema_validator import replace_placeholder, validate_single_object

client = APIClient(BASE_URL)
base_path = "/Books"

@pytest.mark.parametrize("property_to_update, new_value", [
    ("id", 999),
    ("title", "new title"),
    ("description", "new description"),
    ("pageCount", random.randint(1, 1000)),
    ("excerpt", "new excerpt"),
    ("publishDate", datetime.now().isoformat() + "Z")
])
def test_put_update_existing_book(property_to_update, new_value, next_available_book_id, generate_book_data, create_and_cleanup_book):
    book_payload = generate_book_data(book_id=next_available_book_id)
    create_and_cleanup_book(book_payload)

    updated_payload = book_payload.copy()
    updated_payload[property_to_update] = new_value

    response = client.put(f"{base_path}/{next_available_book_id}", data=updated_payload)
    assert response.status_code == 200
    validate_single_object(response.json(), books_object_schema)
    assert response.json()[property_to_update] == new_value

    get_resp = client.get(f"{base_path}/{next_available_book_id}")
    assert get_resp.status_code == 200
    assert response.json()[property_to_update] == new_value

def test_put_non_existent_book(next_available_book_id, generate_book_data):
    
    get_resp = client.get(f"{base_path}/{next_available_book_id}")
    assert get_resp.status_code == 404

    response = client.put(f"{base_path}/{next_available_book_id}", data=generate_book_data(next_available_book_id))
    assert response.status_code == 404

@pytest.mark.parametrize("book_id", [
    "abc",
    "123abc",
    "!@#$%",
    " ",
    12.34,
    "None",
    "1; DROP TABLE Books;",
    "<script>",
    9999999999999999
])
def test_put_invalid_book_id(book_id, generate_book_data):
    book_payload = generate_book_data()
    response = client.put(f"{base_path}/{book_id}", data=book_payload)
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{book_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error, f"Expected error message '{expected_error}' but got '{actual_error}'"

@pytest.mark.parametrize("property_name, value, expected_type", [
    ("id", "not_a_number", "System.Int32"),
    ("title", 123, "System.String"),
    ("description", 123, "System.String"),
    ("excerpt", 123, "System.String"),
    ("pageCount", "not_a_number", "System.Int32"),
    ("publishDate", "not_a_number", "System.DateTime")
])
def test_put_invalid_book_data(property_name, value, expected_type, next_available_book_id, generate_book_data, create_and_cleanup_book):
    # Create a book to update using fixture
    book_payload = generate_book_data(book_id=next_available_book_id)
    response = create_and_cleanup_book(book_payload)
    book_id = response.json()["id"]

    overrides = {property_name: value}
    updated_payload = book_payload.copy()
    updated_payload.update(overrides)

    response = client.put(f"{base_path}/{book_id}", data=updated_payload)
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, f"$.{property_name}")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The JSON value could not be converted to {expected_type}. Path: $.{property_name}"
    actual_error = response.json().get("errors", {}).get(f"$.{property_name}")[0]
    assert expected_error in actual_error, f"Expected error message '{expected_error}' but got '{actual_error}'"

def test_put_book_invalid_content_type(next_available_book_id, generate_book_data, create_and_cleanup_book):
    book_payload = generate_book_data(book_id=next_available_book_id)
    create_and_cleanup_book(book_payload)

    updated_payload = book_payload.copy()
    updated_payload["title"] = "Updated Title"

    invalid_headers = {"Content-Type": "text/plain"}
    response = client.put(f"{base_path}/{next_available_book_id}", data=updated_payload, headers=invalid_headers)
    validate_single_object(response.json(), unsupported_media_type_schema)
    assert response.status_code == 415, f"Expected 400 or 415 status code but got {response.status_code}"
