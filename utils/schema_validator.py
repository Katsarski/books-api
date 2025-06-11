"""
Validation Utilities Module

Helpers to validate JSON responses against schemas and replace schema placeholders.
"""

import json
from jsonschema import validate

def validate_single_object(response_json, schema_name, custom_validator=None):
    """
    Validate a single JSON object against the provided JSON schema.

    Args:
        response_json (dict): The JSON object to validate.
        schema_name (dict): The JSON schema to validate against.
        custom_validator (callable, optional): Additional custom validation function
            that accepts the JSON object.

    Raises:
        jsonschema.exceptions.ValidationError: If the JSON does not conform to the schema.
    """
    validate(instance=response_json, schema=schema_name)
    if custom_validator:
        custom_validator(response_json)

def validate_multiple_objects(response_json, schema_name):
    """
    Validate a list of JSON objects against the provided JSON schema.

    Args:
        response_json (list): The list of JSON objects to validate.
        schema_name (dict): The JSON schema to validate each object against.

    Raises:
        AssertionError: If the input is not a list.
        jsonschema.exceptions.ValidationError: If any object does not conform to the schema.
    """
    assert isinstance(response_json, list), "Response JSON is not a list"
    for book in response_json:
        validate(instance=book, schema=schema_name)

def replace_placeholder(schema, value):
    """
    Replace the placeholder string '{PLACEHOLDER}' in a JSON schema with a specified value.

    Args:
        schema (dict): The JSON schema containing the placeholder.
        value (str): The value to replace the placeholder with.

    Returns:
        dict: The modified JSON schema with the placeholder replaced.
    """
    schema_str = json.dumps(schema)
    schema_str = schema_str.replace("{PLACEHOLDER}", value)
    return json.loads(schema_str)
