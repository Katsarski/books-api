authors_object_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "idBook": {"type": "integer", "minimum": 1},
        "firstName": {"type": ["string", "null"]},
        "lastName": {"type": ["string", "null"]}
    },
    "required": ["id", "idBook", "firstName", "lastName"],
    "additionalProperties": False
}