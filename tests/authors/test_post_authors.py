import pytest
from tests.authors.conftest import next_available_author_id
from utils.request_handler import APIClient
from config.config import BASE_URL
from schemas.authors_schema import authors_object_schema
from schemas.bad_request_schema import bad_request_schema
from schemas.unsupported_media_type_schema import unsupported_media_type_schema
from utils.schema_validator import replace_placeholder, validate_single_object

client = APIClient(BASE_URL)
base_path = "/Authors"

def test_post_available_author_id(generate_author_data, create_and_cleanup_author):
    next_author_id = next_available_author_id()
    author_payload = generate_author_data(author_id=next_author_id)
    response = create_and_cleanup_author(author_payload)
    assert response.json()['id'] == next_author_id
    assert response.status_code == 200
    validate_single_object(response.json(), authors_object_schema)

@pytest.mark.xfail(strict=True, reason="Known bug where we get 200 OK when trying to create an author with an unavailable/already used id")
def test_post_unavailable_author_id(generate_author_data, create_and_cleanup_author):
    unavailable_author_id = next_available_author_id() - 1
    author_payload = generate_author_data(author_id=unavailable_author_id)
    response = create_and_cleanup_author(author_payload)
    assert response.status_code == 400, f"Expected 400 status code for author with unavailable ID but got {response.status_code}"

@pytest.mark.parametrize("property_name, value, expected_type", [
    ("id", "not_a_number", "System.Int32"),
    ("idBook", "not_a_number", "System.Int32"),
    ("firstName", 123, "System.String"),
    ("lastName", 123, "System.String")
])
def test_post_invalid_author_data(property_name, value, expected_type, generate_author_data, create_and_cleanup_author):
    overrides = {property_name: value}
    author_payload = generate_author_data(author_id=next_available_author_id(), overrides=overrides)
    response = create_and_cleanup_author(author_payload)
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, f"$.{property_name}")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The JSON value could not be converted to {expected_type}. Path: $.{property_name}"
    actual_error = response.json().get("errors", {}).get(f"$.{property_name}")[0]
    assert expected_error in actual_error

def test_post_author_invalid_content_type(generate_author_data):
    author_payload = generate_author_data()
    invalid_headers = {"Content-Type": "text/plain"}
    response = client.post("/Authors", data=author_payload, headers=invalid_headers)
    validate_single_object(response.json(), unsupported_media_type_schema)
    assert response.status_code == 415