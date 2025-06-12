"""
Tests for DELETE /authors and /authors/{id}, covering existing, non-existent, and invalid IDs.
"""

import pytest
from config.config import BASE_URL
from tests.authors.conftest import next_available_author_id
from schemas.bad_request_schema import bad_request_schema
from utils.schema_validator import replace_placeholder, validate_single_object
from utils.request_handler import APIClient

client = APIClient(BASE_URL)
BASE_PATH = "/Authors"

@pytest.mark.xfail(strict=True, reason="Known bug where we get 200 OK when getting an author that has been deleted")
def test_delete_existing_author(generate_author_data):
    """
    Test deleting an existing author.
    Verifies creation, retrieval, deletion, and post-deletion retrieval.
    """
    next_author_id = next_available_author_id()
    author_payload = generate_author_data(author_id=next_author_id)
    create_resp = client.post(BASE_PATH, data=author_payload)
    assert create_resp.status_code == 200, \
    f"Expected 200 status code for author creation but got {create_resp.status_code}"
    author_id = create_resp.json()["id"]

    get_resp = client.get(f"{BASE_PATH}/{author_id}")
    assert get_resp.status_code == 200, \
    f"Expected 200 status code for existing author but got {get_resp.status_code}"

    delete_resp = client.delete(f"{BASE_PATH}/{author_id}")
    assert delete_resp.status_code == 200, \
    f"Expected 200 status code for deletion but got {delete_resp.status_code}"

    get_resp = client.get(f"{BASE_PATH}/{author_id}")
    assert get_resp.status_code == 404, \
    f"Expected 404 status code after deletion but got {get_resp.status_code}"

@pytest.mark.xfail(strict=True, reason="Known bug where we are able to delete non-existent author")
def test_delete_non_existent_author():
    """
    Test deleting an author that does not exist.
    """
    response = client.delete(f"{BASE_PATH}/-100")
    assert response.status_code == 404, \
    f"Expected 404 status code for non-existent author but got {response.status_code}"

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
    """
    Test deleting authors with invalid IDs.
    """
    response = client.delete(f"{BASE_PATH}/{author_id}")
    assert response.status_code == 400, \
    f"Expected 400 status code for author_id={author_id} but got {response.status_code}"

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{author_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error, \
    f"Expected error message '{expected_error}' but got '{actual_error}'"
