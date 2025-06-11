import pytest
from utils.request_handler import APIClient
from config.config import BASE_URL
from tests.authors.conftest import next_available_author_id
from schemas.bad_request_schema import bad_request_schema
from utils.schema_validator import replace_placeholder, validate_single_object

client = APIClient(BASE_URL)
base_path = "/Authors"

@pytest.mark.xfail(strict=True, reason="Known bug where we get 200 OK when getting an author that has been deleted")
def test_delete_existing_author(generate_author_data):
    next_author_id = next_available_author_id()
    author_payload = generate_author_data(author_id=next_author_id)
    create_resp = client.post(base_path, data=author_payload)
    assert create_resp.status_code == 200
    author_id = create_resp.json()["id"]

    get_resp = client.get(f"{base_path}/{author_id}")
    assert get_resp.status_code == 200

    delete_resp = client.delete(f"{base_path}/{author_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"{base_path}/{author_id}")
    assert get_resp.status_code == 404

@pytest.mark.xfail(strict=True, reason="Known bug where we are able to delete non-existent author")
def test_delete_non_existent_author():
    response = client.delete(f"{base_path}/-100")
    assert response.status_code == 404

@pytest.mark.parametrize("author_id", [
    "abc", 
    "123abc", 
    pytest.param("!@#$%", marks=pytest.mark.xfail(strict=False, reason="Known bug for '!@#$%'")),
    pytest.param(" ", marks=pytest.mark.xfail(strict=False, reason="Known bug for space character")),
    12.34, 
    "None", 
    "1; DROP TABLE Authors;", 
    "<script>", 9999999999999999
])
def test_delete_invalid_author_id(author_id):
    response = client.delete(f"{base_path}/{author_id}")
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{author_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error