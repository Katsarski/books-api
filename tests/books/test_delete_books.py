import pytest
from utils.request_handler import APIClient
from config.config import BASE_URL
from schemas.bad_request_schema import bad_request_schema
from utils.schema_validator import replace_placeholder, validate_single_object

client = APIClient(BASE_URL)
base_path = "/Books"

def test_delete_existing_book(next_available_book_id, generate_book_data):
    book_payload = generate_book_data(book_id=next_available_book_id)
    create_resp = client.post(base_path, data=book_payload)
    assert create_resp.status_code == 200
    book_id = create_resp.json()["id"]

    get_resp = client.get(f"{base_path}/{book_id}")
    assert get_resp.status_code == 200

    delete_resp = client.delete(f"{base_path}/{book_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"{base_path}/{book_id}")
    assert get_resp.status_code == 404

def test_delete_non_existent_book():
    response = client.delete(f"{base_path}/-100")
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
def test_delete_invalid_book_id(book_id):
    response = client.delete(f"{base_path}/{book_id}")
    assert response.status_code == 400

    bad_request_schema_modified = replace_placeholder(bad_request_schema, "id")
    validate_single_object(response.json(), bad_request_schema_modified)

    expected_error = f"The value '{book_id}' is not valid."
    actual_error = response.json().get("errors", {}).get("id")[0]
    assert expected_error in actual_error, f"Expected error message '{expected_error}' but got '{actual_error}'"