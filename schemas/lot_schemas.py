from marshmallow import Schema, fields, validate

class AddLotSchema(Schema):
    parking_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100, error="Parking name must be between 1 and 100 characters."),
        error_messages={"required": "Parking name is required."}
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="Price must be a positive float."),
        error_messages={"required": "Price is required."}
    )
    address = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255, error="Address must be between 1 and 255 characters."),
        error_messages={"required": "Address is required."}
    )
    pin_code = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{6}$', error="Pin code must be exactly 6 digits."),
        error_messages={"required": "Pin code is required."}
    )
    max_spots = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Max spots must be at least 1."),
        error_messages={"required": "Max spots count is required."}
    )
    latitude = fields.Float(
        allow_none=True,
        validate=validate.Range(min=-90.0, max=90.0, error="Latitude must be between -90 and 90.")
    )
    longitude = fields.Float(
        allow_none=True,
        validate=validate.Range(min=-180.0, max=180.0, error="Longitude must be between -180 and 180.")
    )
    lot_type = fields.String(allow_none=True)
    amenities = fields.String(allow_none=True)

class EditLotSchema(Schema):
    parking_name = fields.String(
        validate=validate.Length(min=1, max=100, error="Parking name must be between 1 and 100 characters.")
    )
    price = fields.Float(
        validate=validate.Range(min=0.01, error="Price must be a positive float.")
    )
    address = fields.String(
        validate=validate.Length(min=1, max=255, error="Address must be between 1 and 255 characters.")
    )
    pin_code = fields.String(
        validate=validate.Regexp(r'^\d{6}$', error="Pin code must be exactly 6 digits.")
    )
    max_spots = fields.Integer(
        validate=validate.Range(min=1, error="Max spots must be at least 1.")
    )
    latitude = fields.Float(
        allow_none=True,
        validate=validate.Range(min=-90.0, max=90.0, error="Latitude must be between -90 and 90.")
    )
    longitude = fields.Float(
        allow_none=True,
        validate=validate.Range(min=-180.0, max=180.0, error="Longitude must be between -180 and 180.")
    )
    lot_type = fields.String(allow_none=True)
    amenities = fields.String(allow_none=True)
