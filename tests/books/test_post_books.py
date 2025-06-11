import pytest
from utils.request_handler import APIClient
from config.config import BASE_URL
from schemas.books_schema import books_object_schema
from schemas.bad_request_schema import bad_request_schema
from schemas.unsupported_media_type_schema import unsupported_media_type_schema
from utils.schema_validator import replace_placeholder, validate_single_object

client = APIClient(BASE_URL)
base_path = "/Books"

def test_post_available_book_id(next_available_book_id, generate_book_data, create_and_cleanup_book):
    book_payload = generate_book_data(book_id=next_available_book_id)
    response = create_and_cleanup_book(book_payload)
    assert response.json()['id'] == next_available_book_id
    assert response.status_code == 200
    validate_single_object(response.json(), books_object_schema)

def test_post_unavailable_book_id(next_available_book_id, generate_book_data, create_and_cleanup_book):
    unavailable_book_id = next_available_book_id - 1
    book_payload = generate_book_data(book_id=unavailable_book_id)
    response = create_and_cleanup_book(book_payload)
    assert response.status_code in (400, 409), f"Expected 400 or 409 status code for book with unavailable ID but got {response.status_code}"

@pytest.mark.parametrize("property_name, value, expected_type", [
                        ("id", "not_a_number", "System.Int32"),
                        ("title", 123, "System.String"),
                        ("description", 123, "System.String"),
                        ("excerpt", 123, "System.String"),
                        ("pageCount", "not_a_number", "System.Int32"),
                        ("publishDate", "not_a_number", "System.DateTime")
    ])
def test_post_invalid_book_data(property_name, value, expected_type, next_available_book_id, generate_book_data, create_and_cleanup_book):
    overrides = {
        property_name: value
    }
    book_payload = generate_book_data(book_id=next_available_book_id, overrides=overrides)
    response = create_and_cleanup_book(book_payload)
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, f"$.{property_name}")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The JSON value could not be converted to {expected_type}. Path: $.{property_name}"
    actual_error = response.json().get("errors", {}).get(f"$.{property_name}")[0]
    assert expected_error in actual_error, f"Expected error message '{expected_error}' but got '{actual_error}'"

@pytest.mark.parametrize("property_to_remove, expected_default_value", [
    ("id", 0),
    ("title", None),
    ("description", None),
    ("pageCount", 0),
    ("excerpt", None),
    ("publishDate", "0001-01-01T00:00:00")
])
def test_post_book_with_missing_field(property_to_remove, expected_default_value, generate_book_data):
    book_payload = generate_book_data()
    book_payload.pop(property_to_remove, None)
    response = client.post("/Books", data=book_payload)
    
    assert response.status_code == 200, f"Expected success for missing field '{property_to_remove}' but got {response.status_code}"
    response_data = response.json()

    # Ensure the missing field now exists with a default or fallback value
    assert property_to_remove in response_data, f"{property_to_remove} not present in response"
    assert response_data[property_to_remove] == expected_default_value, f"Expected {property_to_remove} to be {expected_default_value}, but got {response_data[property_to_remove]}"

def test_post_book_invalid_content_type(generate_book_data):
    book_payload = generate_book_data()
    invalid_headers = {"Content-Type": "text/plain"}
    response = client.post("/Books", data=book_payload, headers=invalid_headers)
    validate_single_object(response.json(), unsupported_media_type_schema)
    assert response.status_code == 415, f"Expected 400 or 415 status code but got {response.status_code}"
