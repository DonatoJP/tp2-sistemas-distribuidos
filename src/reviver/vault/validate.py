def validate_key(key):
    if not key:
        raise ValueError("key must not be empty")
    ILLEGAL_CHARS = ["=", "\r", "\n"]
    if any(c in key for c in ILLEGAL_CHARS):
        raise ValueError("key contains illegal characters")

def validate_value(value):
    if not value:
        raise ValueError("value must not be empty")
    ILLEGAL_CHARS = ["\r", "\n"]
    if any(c in value for c in ILLEGAL_CHARS):
        raise ValueError("value contains illegal characters")
