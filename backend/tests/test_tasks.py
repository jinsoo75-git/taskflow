"""업무(Task) CRUD 및 팀 공유 보드 테스트"""
from conftest import auth_headers, register


def test_list_tasks_requires_auth(client):
    res = client.get("/api/tasks")
    assert res.status_code == 401


def test_create_and_list_task(client):
    alice = register(client, "alice", "pass1234")
    headers = auth_headers(alice["token"])

    res = client.post("/api/tasks", json={"title": "보고서 작성", "description": "월간 보고서"}, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "보고서 작성"
    assert body["creator_username"] == "alice"
    assert body["assignee_id"] is None

    res = client.get("/api/tasks", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_task_assigned_to_other_user_is_visible_on_shared_board(client):
    alice = register(client, "alice", "pass1234")
    bob = register(client, "bob", "pass1234")

    client.post(
        "/api/tasks",
        json={"title": "디자인 검토", "assignee_id": bob["user"]["id"]},
        headers=auth_headers(alice["token"]),
    )

    res = client.get("/api/tasks", headers=auth_headers(bob["token"]))
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["assignee_username"] == "bob"
    assert tasks[0]["creator_username"] == "alice"


def test_update_task_changes_status_and_assignee(client):
    alice = register(client, "alice", "pass1234")
    bob = register(client, "bob", "pass1234")
    headers = auth_headers(alice["token"])

    created = client.post("/api/tasks", json={"title": "기획서"}, headers=headers).json()

    res = client.put(
        f"/api/tasks/{created['id']}",
        json={"title": "기획서", "status": "done", "assignee_id": bob["user"]["id"]},
        headers=headers,
    )
    assert res.status_code == 200
    updated = res.json()
    assert updated["status"] == "done"
    assert updated["assignee_username"] == "bob"


def test_update_nonexistent_task_returns_404(client):
    alice = register(client, "alice", "pass1234")
    res = client.put(
        "/api/tasks/999",
        json={"title": "없는 업무"},
        headers=auth_headers(alice["token"]),
    )
    assert res.status_code == 404


def test_delete_task(client):
    alice = register(client, "alice", "pass1234")
    headers = auth_headers(alice["token"])
    created = client.post("/api/tasks", json={"title": "삭제될 업무"}, headers=headers).json()

    res = client.delete(f"/api/tasks/{created['id']}", headers=headers)
    assert res.status_code == 204

    res = client.get("/api/tasks", headers=headers)
    assert res.json() == []


def test_delete_nonexistent_task_returns_404(client):
    alice = register(client, "alice", "pass1234")
    res = client.delete("/api/tasks/999", headers=auth_headers(alice["token"]))
    assert res.status_code == 404
