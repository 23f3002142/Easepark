from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class ProfileEditSchema(Schema):
    full_name = fields.String(
        allow_none=True,
        validate=validate.Length(max=100, error="Full name cannot exceed 100 characters.")
    )
    username = fields.String(
        allow_none=True,
        validate=[
            validate.Length(min=3, max=80, error="Username must be between 3 and 80 characters."),
            validate.Regexp(
                r'^[a-zA-Z0-9.\-_]+$',
                error="Username must contain only letters, numbers, dots, dashes, and underscores."
            )
        ]
    )
    email = fields.Email(allow_none=True)
    phone_number = fields.String(
        allow_none=True,
        validate=validate.Regexp(
            r'^\+?[0-9]{10,13}$',
            error="Phone number must be between 10 and 13 digits, optionally starting with '+'."
        )
    )
    pin_code = fields.String(
        allow_none=True,
        validate=validate.Regexp(
            r'^\d{6}$',
            error="Pin code must be exactly 6 digits."
        )
    )
    address = fields.String(allow_none=True)

class BookingSchema(Schema):
    vehicle_number = fields.String(
        allow_none=True,
        validate=validate.Regexp(
            r'^[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{1,3}[0-9]{4}$',
            error="Vehicle number must match Indian vehicle number format (e.g., DL01CA1234)."
        )
    )
    vehicle_id = fields.Integer(allow_none=True)

    @validates_schema
    def validate_booking_input(self, data, **kwargs):
        if not data.get('vehicle_number') and not data.get('vehicle_id'):
            raise ValidationError("Either vehicle_number or vehicle_id must be provided.", field_name="vehicle_number")

class VehicleSchema(Schema):
    vehicle_number = fields.String(
        required=True,
        validate=validate.Regexp(
            r'^[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{1,3}[0-9]{4}$',
            error="Vehicle number must match Indian vehicle number format (e.g., DL01CA1234)."
        ),
        error_messages={"required": "Vehicle number is required."}
    )
    nickname = fields.String(
        allow_none=True,
        validate=validate.Length(max=50, error="Nickname cannot exceed 50 characters.")
    )
    is_default = fields.Boolean(load_default=False)

