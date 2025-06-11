"""
Schema for checking books data format.
"""

books_object_schema = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "minimum": 1
        },
        "title": {
            "type": ["string", "null"]
        },
        "description": {
            "type": ["string", "null"]
        },
        "pageCount": {
            "type": "integer",
            "minimum": 1
        },
        "excerpt": {
            "type": ["string", "null"]
        },
        "publishDate": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": [
        "id", "title", "description", "pageCount", "excerpt", "publishDate"
    ],
    "additionalProperties": False
}
