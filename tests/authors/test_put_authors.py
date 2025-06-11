import random
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

@pytest.mark.xfail(strict=False, 
                   reason="Intermittent failure due to unknown reasons ... for whatever reason sometimes the state is persisted and " \
                   "sometimes it is not, further investigation needed")
@pytest.mark.parametrize("property_to_update, new_value", [
    ("idBook", random.randint(1, 200)),
    ("firstName", "UpdatedFirst"),
    ("lastName", "UpdatedLast")
])
def test_put_update_existing_author(property_to_update, new_value, generate_author_data, create_and_cleanup_author):
    next_author_id = next_available_author_id()
    author_payload = generate_author_data(author_id=next_author_id)
    create_and_cleanup_author(author_payload)

    updated_payload = author_payload.copy()
    updated_payload[property_to_update] = new_value

    response = client.put(f"{base_path}/{next_author_id}", data=updated_payload)
    assert response.status_code == 200
    validate_single_object(response.json(), authors_object_schema)
    assert response.json()[property_to_update] == new_value

    get_resp = client.get(f"{base_path}/{next_author_id}")
    assert get_resp.status_code == 200
    assert response.json()[property_to_update] == new_value

@pytest.mark.xfail(strict=True, reason="Known bug where we are able to update non-existent author")
def test_put_non_existent_author(generate_author_data):
    next_author_id = next_available_author_id()
    get_resp = client.get(f"{base_path}/{next_author_id}")
    assert get_resp.status_code == 404

    response = client.put(f"{base_path}/{next_author_id}", data=generate_author_data(next_author_id))
    assert response.status_code == 404

@pytest.mark.parametrize("author_id", [
    "abc", 
    "123abc", 
    pytest.param("!@#$%", marks=pytest.mark.xfail(strict=False, reason="Known bug for '!@#$%'")),
    pytest.param(" ", marks=pytest.mark.xfail(strict=False, reason="Known bug for space character")),
    12.34, 
    "None", 
    "1; DROP TABLE Authors;", 
    "<script>", 
    9999999999999999
])
def test_put_invalid_author_id(author_id, generate_author_data):
    author_payload = generate_author_data()
    response = client.put(f"{base_path}/{author_id}", data=author_payload)
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{author_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error

@pytest.mark.parametrize("property_name, value, expected_type", [
    ("id", "not_a_number", "System.Int32"),
    ("idBook", "not_a_number", "System.Int32"),
    ("firstName", 123, "System.String"),
    ("lastName", 123, "System.String")
])
def test_put_invalid_author_data(property_name, value, expected_type, generate_author_data, create_and_cleanup_author):
    author_payload = generate_author_data(author_id=next_available_author_id())
    response = create_and_cleanup_author(author_payload)
    author_id = response.json()["id"]

    overrides = {property_name: value}
    updated_payload = author_payload.copy()
    updated_payload.update(overrides)

    response = client.put(f"{base_path}/{author_id}", data=updated_payload)
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, f"$.{property_name}")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The JSON value could not be converted to {expected_type}. Path: $.{property_name}"
    actual_error = response.json().get("errors", {}).get(f"$.{property_name}")[0]
    assert expected_error in actual_error

def test_put_author_invalid_content_type(generate_author_data, create_and_cleanup_author):
    next_author_id = next_available_author_id()
    author_payload = generate_author_data(author_id=next_author_id)
    create_and_cleanup_author(author_payload)

    updated_payload = author_payload.copy()
    updated_payload["firstName"] = "UpdatedFirst"

    invalid_headers = {"Content-Type": "text/plain"}
    response = client.put(f"{base_path}/{next_author_id}", data=updated_payload, headers=invalid_headers)
    validate_single_object(response.json(), unsupported_media_type_schema)
    assert response.status_code == 415