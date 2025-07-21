import datetime
from sqlite3 import Date
from .db import get_db, init_db
from .crud import (
    create_user, get_user_by_username, authenticate_user,
    create_user_session, get_user_sessions, delete_user_session,
    add_message_to_session, get_session_messages, get_session_by_id,
    get_max_message_id_database, download_all_versions
)   
from . import schemas, models
from typing import Optional


def register_user(username: str, password: str):
    """
    注册新用户，返回用户对象或 None（已存在）
    """
    db = next(get_db())
    if get_user_by_username(db, username):
        return None
    user_data = schemas.UserCreate(username=username, password=password)
    return create_user(db, user_data)


def login_user(username: str, password: str):
    """
    校验登录，返回用户对象或 None
    """
    db = next(get_db())
    return authenticate_user(db, username, password)


def create_session(user_id: int, title: Optional[str] = None):
    """
    为用户创建新会话，返回会话对象
    """
    db = next(get_db())
    if title is None:
        title = "New Session"
    return create_user_session(db, user_id, title=title)

def delete_session(session_id: int):
    """
    删除指定会话，返回 True/False
    """
    db = next(get_db())
    return delete_user_session(db, session_id)


def get_user_history(username: str):
    db = next(get_db())
    user = get_user_by_username(db, username)
    if not user:
        return None
    user_id = int(getattr(user, 'id', user.id))
    sessions = get_user_sessions(db, user_id)
    result = []
    for s in sessions:
        session_id = int(getattr(s, 'id', s.id))
        messages = get_session_messages(db, session_id)
        result.append({
            "id": session_id,
            "user_id": user_id,
            "title": s.title,
            "created_at": s.created_at,
            "messages": [
                {
                    "id": m.id,
                    "session_id": m.session_id,
                    "content": m.content,
                    "image": m.image if m.image else "",
                    "role": m.role,
                    "timestamp": m.timestamp
                } for m in messages
            ]
        })
    return result



def create_message(session_id: int, content: str, role: str,image:str):
    db = next(get_db())
    sid = int(session_id)
    add_message_to_session(db, sid, content,role, image)

def get_max_message_id():
    db = next(get_db())
    return get_max_message_id_database(db)

def update_session_title(session_id: int, title: str):
    db = next(get_db())
    session = get_session_by_id(db, session_id)
    if session:
        session.title = title
        db.commit()
def get_all_versions(session_id: int):
    db = next(get_db())
    return download_all_versions(db, session_id)