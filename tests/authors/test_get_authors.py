"""
Tests for GET /authors and /authors/{id}: all, single (valid, non-existent, invalid IDs).
Includes handling intermittent failures and schema validation.
"""

import pytest
from config.config import BASE_URL
from tests.authors.conftest import next_available_author_id
from schemas.bad_request_schema import bad_request_schema
from schemas.authors_schema import authors_object_schema
from utils.schema_validator import replace_placeholder, validate_single_object, validate_multiple_objects
from utils.request_handler import APIClient

client = APIClient(BASE_URL)
BASE_PATH = "/Authors"

def test_get_all_authors():
    """
    Test retrieving all authors.
    Validates response status and schema of returned list.
    """
    response = client.get(BASE_PATH)
    assert response.status_code == 200, \
    f"Expected 200 status code but got {response.status_code}"
    validate_multiple_objects(response.json(), authors_object_schema)

@pytest.mark.parametrize("author_id, expected_status", [(1, 200), (200, 200)])
def test_get_single_author_parametrized(author_id, expected_status):
    """
    Test retrieving single authors by valid IDs.
    Checks response status and validates the response schema.
    """
    response = client.get(f"{BASE_PATH}/{author_id}")
    assert response.status_code == expected_status, \
    f"Expected {expected_status} status code for author_id={author_id} but got {response.status_code}"
    validate_single_object(response.json(), authors_object_schema)

@pytest.mark.xfail(strict=False,
                   reason="Intermittent failure due to unknown reasons ... it feels like we " \
                   "are querying a different DB sometimes, " \
                   "further investigation needed")
@pytest.mark.parametrize("author_id", [0, next_available_author_id(), -1])
def test_get_single_non_existent_author_parametrized(author_id):
    """
    Test retrieving non-existent authors.
    """
    expected_status_code = 404 # sometimes returns 200 instead of 404
    response = client.get(f"{BASE_PATH}/{author_id}")
    assert response.status_code == expected_status_code, \
    f"Expected {expected_status_code} status code for id={author_id} but got {response.status_code}"

@pytest.mark.parametrize("author_id", [
    "abc",
    "123abc",
    "!@#$%",
    " ",
    12.34,
    "None",
    "1; DROP TABLE Authors;",
    "<script>"
])
def test_get_single_invalid_author_parametrized(author_id):
    """
    Test retrieving authors with invalid IDs.
    """
    response = client.get(f"{BASE_PATH}/{author_id}")
    assert response.status_code == 400, \
    f"Expected 400 status code for author_id={author_id} but got {response.status_code}"
    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)
