"""What Codes offers others (Hubra docs/contracts.md).

Codes are moving into the Keys plugin as keys of the kind "code" (stored
encrypted there, assignable to members and groups, shown in the inventory).
Keys reads the codes through ``codes.codes.export`` and takes them over; it
never reads this plugin's table. Once Keys has them, Codes can be switched
off and uninstalled.
"""

from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import select

from hubra.core.extensions import db

from .models import Code


class ExportIn(BaseModel):
    pass


class ExportedCode(BaseModel):
    id: int
    name: str
    code: str
    description: str | None = None
    is_active: bool = True


def export_codes(ctx, data: ExportIn) -> list[ExportedCode]:
    """Every code in clear text (one that no longer decrypts has "")."""
    rows = db.session.scalars(select(Code).order_by(Code.id)).all()
    return [
        ExportedCode(
            id=r.id,
            name=r.name,
            code=r.plain_code,
            description=r.description,
            is_active=bool(r.is_active),
        )
        for r in rows
    ]
