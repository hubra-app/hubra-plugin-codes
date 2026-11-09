"""Codes: door codes, lock combinations and passcodes, stored encrypted.

Was built into Hubra up to 0.x as the module "codes"; the module code, the
table, the API path and the permissions (codes.codes.*) stay the same, so
clubs keep their codes, their switch and their roles.

Codes are moving into Keys as keys of the kind "code": Keys takes them over
through the query ``codes.codes.export`` (hubra_codes.contracts).
"""

from hubra.core.contracts import query_contract
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
    provides=(
        query_contract(
            "codes.codes.export",
            "hubra_codes.contracts:export_codes",
            input="hubra_codes.contracts:ExportIn",
            output="hubra_codes.contracts:ExportedCode",
            perm="codes.codes.read",
            description="Every code in clear text, for Keys to take over",
        ),
    ),
    encrypted_columns=(("codes", "id", "code", ""),),
)
