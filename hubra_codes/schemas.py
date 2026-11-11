"""Code schemas — Marshmallow serialization/validation."""

from __future__ import annotations

from marshmallow import EXCLUDE, RAISE, Schema, ValidationError, fields, validate

from hubra.core.extensions import ma
from .models import Code

# Upper bounds, so one request can't park megabytes in the table (the page
# allows 16 characters; Wi-Fi keys and passphrases need more room).
CODE_MAX = 255
DESCRIPTION_MAX = 5000


def _not_blank(value: str) -> bool:
    if not value.strip():
        raise ValidationError("Must not be blank.")
    return True


class CodeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Code
        load_instance = True
        unknown = EXCLUDE
        # The code itself is never in a list or detail answer: it comes only
        # from POST /codes/<id>/reveal, which writes an audit entry.
        exclude = ("code", "created_by_id", "updated_by_id")

    created_by = fields.Method("get_created_by", dump_only=True)
    updated_by = fields.Method("get_updated_by", dump_only=True)

    @staticmethod
    def get_created_by(obj: Code) -> str | None:
        return obj.created_by.name if obj.created_by else None

    @staticmethod
    def get_updated_by(obj: Code) -> str | None:
        return obj.updated_by.name if obj.updated_by else None


class CodeCreateSchema(Schema):
    class Meta:
        unknown = RAISE

    name = fields.Str(
        required=True, validate=[validate.Length(min=1, max=255), _not_blank]
    )
    code = fields.Str(
        required=True, validate=[validate.Length(min=1, max=CODE_MAX), _not_blank]
    )
    description = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=DESCRIPTION_MAX),
    )


class CodeUpdateSchema(Schema):
    class Meta:
        unknown = RAISE

    name = fields.Str(validate=[validate.Length(min=1, max=255), _not_blank])
    code = fields.Str(validate=[validate.Length(min=1, max=CODE_MAX), _not_blank])
    description = fields.Str(
        allow_none=True, validate=validate.Length(max=DESCRIPTION_MAX)
    )
    is_active = fields.Bool()
