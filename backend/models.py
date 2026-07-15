"""요청/응답에 사용하는 Pydantic 모델"""
from typing import Literal, Optional
from pydantic import BaseModel

TaskStatus = Literal["todo", "in_progress", "done"]


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = "todo"
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = "todo"
    assignee_id: Optional[int] = None


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    created_at: str
    creator_id: int
    creator_username: str
    assignee_id: Optional[int] = None
    assignee_username: Optional[str] = None
