"""SQLite 데이터베이스 연결 및 초기화"""
import os
import sqlite3
from pathlib import Path

# 테스트에서는 TASKFLOW_DB_PATH로 별도 DB 파일을 지정해 격리한다
DB_PATH = Path(os.environ.get("TASKFLOW_DB_PATH", Path(__file__).parent / "taskflow.db"))


def get_connection():
    # 요청마다 새 연결을 생성하고 dict처럼 행에 접근할 수 있도록 row_factory 설정
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo',
            creator_id INTEGER NOT NULL REFERENCES users(id),
            assignee_id INTEGER REFERENCES users(id),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()
