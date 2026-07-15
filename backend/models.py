"""요청/응답에 사용하는 Pydantic 모델"""
from typing import Literal
from pydantic import BaseModel

TaskStatus = Literal["todo", "in_progress", "done"]


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = "todo"


class TaskUpdate(BaseModel):
    title: str
    description: str = ""
    status: TaskStatus = "todo"


class Task(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    created_at: str
