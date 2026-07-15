"""테스트용 격리된 SQLite DB와 TestClient를 제공하는 fixture"""
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture()
def client():
    # 테스트마다 새 임시 DB 파일을 사용해 상태가 섞이지 않도록 격리
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["TASKFLOW_DB_PATH"] = path

    import importlib
    import database
    import auth
    import main

    importlib.reload(database)
    importlib.reload(auth)
    importlib.reload(main)

    from fastapi.testclient import TestClient

    with TestClient(main.app) as test_client:
        yield test_client

    Path(path).unlink(missing_ok=True)
    os.environ.pop("TASKFLOW_DB_PATH", None)


def register(client, username="alice", password="pass1234"):
    res = client.post("/api/auth/register", json={"username": username, "password": password})
    assert res.status_code == 201, res.text
    return res.json()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
