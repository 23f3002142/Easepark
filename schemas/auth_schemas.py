from marshmallow import Schema, fields, validate, validates, ValidationError

class SendOtpSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required."})

class VerifyRegistrationOtpSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required."})
    otp = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{6}$', error="OTP must be exactly 6 digits."),
        error_messages={"required": "OTP is required."}
    )

class RegisterSchema(Schema):
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error="Username must be between 3 and 80 characters."),
            validate.Regexp(
                r'^[a-zA-Z0-9.\-_]+$',
                error="Username must contain only letters, numbers, dots, dashes, and underscores."
            )
        ],
        error_messages={"required": "Username is required."}
    )
    email = fields.Email(required=True, error_messages={"required": "Email is required."})
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters."),
        error_messages={"required": "Password is required."}
    )

class LoginSchema(Schema):
    username = fields.String(required=True, error_messages={"required": "Username or Email is required."})
    password = fields.String(required=True, error_messages={"required": "Password is required."})

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required."})

class ResetPasswordSchema(Schema):
    email = fields.Email(required=True, error_messages={"required": "Email is required."})
    otp = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{6}$', error="OTP must be exactly 6 digits."),
        error_messages={"required": "OTP is required."}
    )
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters."),
        error_messages={"required": "New password is required."}
    )

class ChangePasswordSchema(Schema):
    current_password = fields.String(required=True, error_messages={"required": "Current password is required."})
    new_password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="New password must be at least 6 characters."),
        error_messages={"required": "New password is required."}
    )
    confirm_password = fields.String(required=True, error_messages={"required": "Confirm password is required."})
