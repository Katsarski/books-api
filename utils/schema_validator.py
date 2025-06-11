import json
from jsonschema import validate
from schemas import *

# We do this to avoid duplicating the validation logic for single and multiple objects but reuse a single schema
#  for both cases.

def validate_single_object(response_json, schema_name):
    validate(instance=response_json, schema=schema_name)

def validate_multiple_objects(response_json, schema_name):
    assert isinstance(response_json, list), "Expected list of books"
    for book in response_json:
        validate(instance=book, schema=schema_name)

def replace_placeholder(schema, value):
    """
    Replace a placeholder in the schema with a specific value.
    """
    schema_str = json.dumps(schema)
    schema_str = schema_str.replace("{PLACEHOLDER}", value)
    return json.loads(schema_str)