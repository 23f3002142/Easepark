import functools
from flask import request, jsonify
from marshmallow import ValidationError

def validate_schema(schema_class):
    """
    Decorator to validate request JSON body against a Marshmallow schema.
    If validation fails, returns 422 Unprocessable Entity with structured errors.
    Otherwise, passes the valid deserialized data as `valid_data` keyword argument.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
            except Exception:
                data = None
            
            if data is None:
                return jsonify({"error": "Request body must be a valid JSON object"}), 400
            
            schema = schema_class()
            try:
                valid_data = schema.load(data)
            except ValidationError as err:
                return jsonify({"errors": err.messages}), 422
            
            kwargs['valid_data'] = valid_data
            return f(*args, **kwargs)
        return wrapper
    return decorator
