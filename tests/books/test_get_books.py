import pytest
from tests.books.conftest import next_available_book_id
from utils.request_handler import APIClient
from config.config import BASE_URL
from schemas.books_schema import books_object_schema
from schemas.bad_request_schema import bad_request_schema
from utils.schema_validator import replace_placeholder, validate_single_object, validate_multiple_objects

client = APIClient(BASE_URL)
base_path = "/Books"

def test_get_all_books():
    response = client.get(base_path)
    assert response.status_code == 200
    validate_multiple_objects(response.json(), books_object_schema)

@pytest.mark.parametrize("book_id, expected_status", [(1, 200), (200, 200)])
def test_get_single_book_parametrized(book_id, expected_status):
    response = client.get(f"{base_path}/{book_id}")
    assert response.status_code == expected_status, f"Expected {expected_status} status code for book_id={book_id} but got" \
        f"{response.status_code}"
    validate_single_object(response.json(), books_object_schema)

@pytest.mark.parametrize("book_id", [0, next_available_book_id(), -1])
def test_get_single_non_existent_book_parametrized(book_id):
    expected_status_code = 404
    response = client.get(f"{base_path}/{book_id}")
    assert response.status_code == expected_status_code, f"Expected {expected_status_code} status code for book_id={book_id} but" \
         f" got {response.status_code}"

@pytest.mark.parametrize("book_id", [
                        "abc", 
                        "123abc", 
                        pytest.param("!@#$%", marks=pytest.mark.xfail(strict=False, reason="Known bug for '!@#$%'")),
                        pytest.param(" ", marks=pytest.mark.xfail(strict=False, reason="Known bug for space character")),
                        12.34, 
                        "None", 
                        "1; DROP TABLE Books;", 
                        "<script>"
    ])
def test_get_single_invalid_book_parametrized(book_id):
    expected_status_code = 400
    response = client.get(f"{base_path}/{book_id}")
    assert response.status_code == expected_status_code, f"Expected {expected_status_code} status code for book_id={book_id} but" \
         f" got {response.status_code}"
    
    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{book_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error, f"Expected error message '{expected_error}' but got '{actual_error}'"

@pytest.mark.skip(reason="This test is not applicable for the current API design")
def test_get_single_book_invalid_headers():
    print("This test is not applicable for the current API design")