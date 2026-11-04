"""Codes: door codes, lock combinations and passcodes, stored encrypted.

Was built into Hubra up to 0.x as the module "codes"; the module code, the
table, the API path and the permissions (codes.codes.*) stay the same, so
clubs keep their codes, their switch and their roles.
"""

from hubra.core.modules import Blueprint, Module, NavItem

module = Module(
    code="codes",
    name="Codes",
    description="Encrypted door codes and passcodes",
    default_enabled=False,
    depends_on=("members",),
    blueprints=(
        Blueprint(
            "hubra_codes.routes",
            "codes_bp",
            "/api/v1/codes",
        ),
    ),
    nav=(
        NavItem(
            "/app/operations/codes",
            "shell.nav.codes",
            "lock",
            section="more",
            order=20,
            perms=("codes.codes.read",),
        ),
    ),
    tables=("codes",),
    encrypted_columns=(("codes", "id", "code", ""),),
)
