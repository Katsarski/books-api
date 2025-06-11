bad_request_schema = {
"type": "object",
    "properties": {
        "type": {"type": "string", "format": "uri"},
        "title": {"type": "string"},
        "status": {"type": "integer"},
        "traceId": {"type": "string"},
        "errors": {
            "type": "object",
            "properties": {
                "{PLACEHOLDER}": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["{PLACEHOLDER}"],
            "additionalProperties": False
        }
    },
    "required": ["type", "title", "status", "traceId", "errors"],
    "additionalProperties": False
}