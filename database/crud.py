import sys
import os
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "database"
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models
from . import schemas
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_user_session(db: Session, user_id: int, title: str = "New Session"):
    db_session = models.Session(user_id=user_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_user_sessions(db: Session, user_id: int):
    return db.query(models.Session).filter(models.Session.user_id == user_id).all()

def get_session_by_id(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def delete_session(db: Session, session_id: int):
    session = get_session_by_id(db, session_id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

# 修改：添加content_type参数
def add_message_to_session(
    db: Session,
    session_id: int,
    content: str,
    role: str = "user",
    content_type: str = "text"  # 新增内容类型
):
    db_message = models.Message(
        session_id=session_id,
        content=content,
        role=role,
        content_type=content_type  # 设置内容类型
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_session_messages(db: Session, session_id: int):
    return db.query(models.Message)\
        .filter(models.Message.session_id == session_id)\
        .order_by(models.Message.timestamp.asc())\
        .all()