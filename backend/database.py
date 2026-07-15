"""SQLite 데이터베이스 연결 및 초기화"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "taskflow.db"


def get_connection():
    # 요청마다 새 연결을 생성하고 dict처럼 행에 접근할 수 있도록 row_factory 설정
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()
