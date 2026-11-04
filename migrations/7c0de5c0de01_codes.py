"""codes

Databases that ran Hubra before Codes became a plugin have the table already
(Hubra's baseline revision e5a32bbb8ef5); it is kept as it is, codes and all.

Revision ID: 7c0de5c0de01
Revises:
Create Date: 2026-11-02 14:00:00

"""

from alembic import op
import sqlalchemy as sa

from hubra.core.plugins.ops import has_table

revision = "7c0de5c0de01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    if has_table("codes"):
        return
    op.create_table(
        "codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["members.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_id"], ["members.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("codes")
