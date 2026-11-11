"""Tests for the access codes API (/api/v1/codes)."""

import pytest

from hubra.core.models.audit import AuditEntry
from hubra_codes.models import Code


def _create(client, auth_headers, **overrides):
    body = {"name": "Haustür", "code": "4711", "description": "Hinten"}
    body.update(overrides)
    return client.post("/api/v1/codes/", json=body, headers=auth_headers)


def test_create_stores_the_code_encrypted(client, auth_headers, db):
    resp = _create(client, auth_headers)
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    assert body["code"] == "4711"
    assert body["created_by"]

    stored = db.session.get(Code, body["id"])
    assert stored.code != "4711"
    assert stored.plain_code == "4711"


def test_create_is_audited_with_its_id(client, auth_headers, db):
    code_id = _create(client, auth_headers).get_json()["id"]

    entry = db.session.query(AuditEntry).filter_by(action="create_code").one()
    assert entry.target_id == code_id


def test_create_needs_name_and_code(client, auth_headers):
    assert _create(client, auth_headers, code="").status_code == 400
    assert _create(client, auth_headers, name="").status_code == 400
    assert _create(client, auth_headers, extra=1).status_code == 400


def test_list_get_update_delete(client, auth_headers, db):
    code_id = _create(client, auth_headers).get_json()["id"]
    _create(client, auth_headers, name="Archiv", code="0000")

    listed = client.get("/api/v1/codes/", headers=auth_headers).get_json()
    assert [c["name"] for c in listed] == ["Archiv", "Haustür"]

    resp = client.patch(
        f"/api/v1/codes/{code_id}",
        json={"code": "1234", "is_active": False},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["code"] == "1234"
    assert resp.get_json()["is_active"] is False

    got = client.get(f"/api/v1/codes/{code_id}", headers=auth_headers)
    assert got.get_json()["code"] == "1234"

    assert client.delete(
        f"/api/v1/codes/{code_id}", headers=auth_headers
    ).status_code in (200, 204)
    assert (
        client.get(f"/api/v1/codes/{code_id}", headers=auth_headers).status_code == 404
    )
    entry = db.session.query(AuditEntry).filter_by(action="delete_code").one()
    assert (entry.target_id, entry.target_label) == (code_id, "Haustür")


def test_unknown_code_is_404(client, auth_headers):
    assert client.get("/api/v1/codes/999", headers=auth_headers).status_code == 404
    assert (
        client.patch(
            "/api/v1/codes/999", json={"name": "x"}, headers=auth_headers
        ).status_code
        == 404
    )


def test_codes_need_a_sign_in(client):
    # Without a sign-in there is no club, so the module check answers first.
    assert client.get("/api/v1/codes/").status_code in (401, 403)


def test_a_code_that_no_longer_decrypts_does_not_break_the_list(
    client, auth_headers, db
):
    """After a key change old codes cannot be read; the rest still can."""
    _create(client, auth_headers)
    db.session.add(Code(name="Alt", code="encrypted-with-an-old-key"))
    db.session.commit()

    resp = client.get("/api/v1/codes/", headers=auth_headers)
    assert resp.status_code == 200
    by_name = {c["name"]: c["code"] for c in resp.get_json()}
    assert by_name == {"Haustür": "4711", "Alt": ""}


def test_codes_are_part_of_key_rotation():
    """FERNET_KEY rotation and the key check find the plugin's column."""
    from hubra.core.services.secret_store import columns

    assert ("codes", "id", "code", "") in columns()


def test_deleting_a_member_keeps_their_codes(client, auth_headers, db, seeded_db):
    from hubra.api.members.services import MemberService
    from hubra.core.models.member import Member
    from hubra.core.models.user import User

    user = User(email="leaving@test.ch", first_name="Lea", last_name="Leaving")
    user.set_password("password123")
    db.session.add(user)
    db.session.flush()
    from datetime import datetime, timezone

    other = Member(
        user_id=user.id,
        status="active",
        tier_id=seeded_db["tier"].id,
        archived_at=datetime.now(timezone.utc),
    )
    db.session.add(other)
    db.session.flush()
    code = Code(name="Keller", code="x", created_by_id=other.id, updated_by_id=other.id)
    db.session.add(code)
    db.session.commit()

    MemberService.delete_permanent(other.id, seeded_db["admin"].id)
    db.session.commit()
    kept = db.session.get(Code, code.id)
    assert (
        kept is not None and kept.created_by_id is None and kept.updated_by_id is None
    )


def test_codes_are_offered_for_keys_to_take_over(app, db, seeded_db):
    from hubra.core import contracts
    from hubra.core.crypto import encrypt_code

    db.session.add_all([
        Code(name="Gate", code=encrypt_code("1234", "codes.code"), description="Back"),
        Code(name="Old", code=encrypt_code("9", "codes.code"), is_active=False),
    ])
    db.session.commit()
    out = contracts.query("codes.codes.export", actor=contracts.SYSTEM)
    assert [(c["name"], c["code"], c["is_active"]) for c in out] == [
        ("Gate", "1234", True), ("Old", "9", False),
    ]
    with pytest.raises(contracts.ActionForbidden):
        contracts.query("codes.codes.export", actor=None)


def test_blank_and_oversized_input_is_refused(client, auth_headers):
    from hubra_codes.schemas import CODE_MAX, DESCRIPTION_MAX

    assert _create(client, auth_headers, code="   ").status_code == 400
    assert _create(client, auth_headers, name="  ").status_code == 400
    assert _create(client, auth_headers, code="1" * (CODE_MAX + 1)).status_code == 400
    assert (
        _create(client, auth_headers, description="x" * (DESCRIPTION_MAX + 1)).status_code
        == 400
    )
    code_id = _create(client, auth_headers).get_json()["id"]
    for body in ({"code": " "}, {"code": "1" * (CODE_MAX + 1)}, {"name": ""}):
        resp = client.patch(f"/api/v1/codes/{code_id}", json=body, headers=auth_headers)
        assert resp.status_code == 400, body
