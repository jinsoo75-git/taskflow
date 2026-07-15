"""비밀번호 해싱 및 토큰 기반 인증 유틸리티"""
import hashlib
import secrets

from fastapi import Header, HTTPException

from database import get_connection


def hash_password(password: str) -> str:
    # 표준 라이브러리만 사용 (외부 컴파일 의존성 회피)
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000)
    return f"{salt}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, _, digest_hex = stored.partition(":")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000)
    return secrets.compare_digest(digest.hex(), digest_hex)


def create_session(user_id: int) -> str:
    token = secrets.token_hex(32)
    conn = get_connection()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")

    token = authorization.removeprefix("Bearer ").strip()
    conn = get_connection()
    row = conn.execute(
        """
        SELECT users.id, users.username
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다")

    return dict(row)
