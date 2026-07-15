"""업무관리 API 서버 (팀 공유 보드 + 로그인)"""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from auth import create_session, get_current_user, hash_password, verify_password
from database import get_connection, init_db
from models import Task, TaskCreate, TaskUpdate, TokenOut, UserCreate, UserOut

app = FastAPI(title="업무관리 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


TASK_SELECT = """
    SELECT
        tasks.*,
        creator.username AS creator_username,
        assignee.username AS assignee_username
    FROM tasks
    JOIN users AS creator ON creator.id = tasks.creator_id
    LEFT JOIN users AS assignee ON assignee.id = tasks.assignee_id
"""


@app.post("/api/auth/register", response_model=TokenOut, status_code=201)
def register(payload: UserCreate):
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (payload.username,)
    ).fetchone()
    if existing is not None:
        conn.close()
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다")

    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (payload.username, hash_password(payload.password)),
    )
    conn.commit()
    user_id = cursor.lastrowid
    token = create_session(user_id)
    conn.close()
    return {"token": token, "user": {"id": user_id, "username": payload.username}}


@app.post("/api/auth/login", response_model=TokenOut)
def login(payload: UserCreate):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (payload.username,),
    ).fetchone()
    conn.close()

    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다")

    token = create_session(row["id"])
    return {"token": token, "user": {"id": row["id"], "username": row["username"]}}


@app.get("/api/auth/me", response_model=UserOut)
def me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/api/users", response_model=list[UserOut])
def list_users(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    rows = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/api/tasks", response_model=list[Task])
def list_tasks(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    rows = conn.execute(TASK_SELECT + " ORDER BY tasks.id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description, status, creator_id, assignee_id) VALUES (?, ?, ?, ?, ?)",
        (task.title, task.description, task.status, current_user["id"], task.assignee_id),
    )
    conn.commit()
    row = conn.execute(TASK_SELECT + " WHERE tasks.id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다")

    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, status = ?, assignee_id = ? WHERE id = ?",
        (task.title, task.description, task.status, task.assignee_id, task_id),
    )
    conn.commit()
    row = conn.execute(TASK_SELECT + " WHERE tasks.id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="업무를 찾을 수 없습니다")

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


# 프론트엔드 정적 파일 서빙
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
