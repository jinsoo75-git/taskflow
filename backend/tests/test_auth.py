"""회원가입/로그인 API 테스트"""
from conftest import auth_headers, register


def test_register_creates_user_and_returns_token(client):
    data = register(client, "alice", "pass1234")
    assert data["user"]["username"] == "alice"
    assert data["token"]


def test_register_duplicate_username_rejected(client):
    register(client, "alice", "pass1234")
    res = client.post("/api/auth/register", json={"username": "alice", "password": "other"})
    assert res.status_code == 409


def test_login_with_correct_credentials(client):
    register(client, "alice", "pass1234")
    res = client.post("/api/auth/login", json={"username": "alice", "password": "pass1234"})
    assert res.status_code == 200
    assert res.json()["user"]["username"] == "alice"


def test_login_with_wrong_password_rejected(client):
    register(client, "alice", "pass1234")
    res = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert res.status_code == 401


def test_login_with_unknown_username_rejected(client):
    res = client.post("/api/auth/login", json={"username": "nobody", "password": "pass1234"})
    assert res.status_code == 401


def test_me_requires_valid_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401

    data = register(client, "alice", "pass1234")
    res = client.get("/api/auth/me", headers=auth_headers(data["token"]))
    assert res.status_code == 200
    assert res.json()["username"] == "alice"


def test_me_rejects_invalid_token(client):
    res = client.get("/api/auth/me", headers=auth_headers("not-a-real-token"))
    assert res.status_code == 401
