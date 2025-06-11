"""
Schema for unsupported media type response.
"""

unsupported_media_type_schema = {
  "type": "object",
  "properties": {
    "type": {
      "type": "string",
      "format": "uri",
      "const": "https://tools.ietf.org/html/rfc7231#section-6.5.13"
    },
    "title": {
      "type": "string",
      "const": "Unsupported Media Type"
    },
    "status": {
      "type": "integer",
      "const": 415
    },
    "traceId": {
      "type": "string"
    }
  },
  "required": ["type", "title", "status", "traceId"],
  "additionalProperties": False
}
