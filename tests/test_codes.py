"""Tests for the access codes API (/api/v1/codes)."""

import pytest

from hubra.core.models.audit import AuditEntry
from hubra_codes.models import Code


def _create(client, auth_headers, **overrides):
    body = {"name": "Haustür", "code": "4711", "description": "Hinten"}
    body.update(overrides)
    return client.post("/api/v1/codes/", json=body, headers=auth_headers)


def _reveal(client, auth_headers, code_id):
    return client.post(f"/api/v1/codes/{code_id}/reveal", headers=auth_headers)


def test_create_stores_the_code_encrypted(client, auth_headers, db):
    resp = _create(client, auth_headers)
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    assert "code" not in body
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
    assert resp.get_json()["is_active"] is False
    assert _reveal(client, auth_headers, code_id).get_json()["code"] == "1234"

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
    by_name = {c["name"]: c["id"] for c in resp.get_json()}
    assert set(by_name) == {"Haustür", "Alt"}
    plain = {
        name: _reveal(client, auth_headers, i).get_json()["code"]
        for name, i in by_name.items()
    }
    assert plain == {"Haustür": "4711", "Alt": ""}


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
        _create(
            client, auth_headers, description="x" * (DESCRIPTION_MAX + 1)
        ).status_code
        == 400
    )
    code_id = _create(client, auth_headers).get_json()["id"]
    for body in ({"code": " "}, {"code": "1" * (CODE_MAX + 1)}, {"name": ""}):
        resp = client.patch(f"/api/v1/codes/{code_id}", json=body, headers=auth_headers)
        assert resp.status_code == 400, body


def test_list_and_detail_never_carry_the_code(client, auth_headers):
    code_id = _create(client, auth_headers).get_json()["id"]
    listed = client.get("/api/v1/codes/", headers=auth_headers).get_json()
    got = client.get(f"/api/v1/codes/{code_id}", headers=auth_headers).get_json()
    patched = client.patch(
        f"/api/v1/codes/{code_id}", json={"name": "Neu"}, headers=auth_headers
    ).get_json()
    for body in (*listed, got, patched):
        assert "code" not in body
        assert "4711" not in str(body)


def test_reveal_gives_the_code_and_audits_who_saw_it(client, auth_headers, db):
    code_id = _create(client, auth_headers).get_json()["id"]

    resp = _reveal(client, auth_headers, code_id)
    assert resp.status_code == 200
    assert resp.get_json() == {"id": code_id, "code": "4711"}
    assert resp.headers["Cache-Control"] == "no-store"

    entry = db.session.query(AuditEntry).filter_by(action="reveal_code").one()
    assert (entry.target_id, entry.target_label) == (code_id, "Haustür")
    assert entry.actor_id is not None
    assert _reveal(client, auth_headers, 999).status_code == 404


def test_reveal_needs_the_read_right(client, auth_headers, app, db, seeded_db):
    from tests.settings.test_settings_kv import _login, _make_role_and_member

    code_id = _create(client, auth_headers).get_json()["id"]
    app.test_cli_runner().invoke(args=["sync-permissions"])
    _make_role_and_member(db, seeded_db["tier"], name="Max")
    _make_role_and_member(
        db, seeded_db["tier"], name="Rita", permission_keys=["codes.codes.read"]
    )

    _login(client, "max@test.ch")
    assert client.post(f"/api/v1/codes/{code_id}/reveal").status_code == 403
    _login(client, "rita@test.ch")
    assert client.post(f"/api/v1/codes/{code_id}/reveal").get_json()["code"] == "4711"
    assert db.session.query(AuditEntry).filter_by(action="reveal_code").count() == 1
