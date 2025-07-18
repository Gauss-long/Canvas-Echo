import os
from .db import get_db
from .models import User, Session, Message

def print_db():
    db = next(get_db())
    print("=== 用户列表 ===")
    users = db.query(User).all()
    for user in users:
        print(f"用户ID: {user.id}, 用户名: {user.username}, 注册时间: {user.created_at}")
        sessions = db.query(Session).filter(Session.user_id == user.id).all()
        print(f"  会话数: {len(sessions)}")
        for session in sessions:
            print(f"    会话ID: {session.id}, 标题: {session.title}, 创建时间: {session.created_at}")
            messages = db.query(Message).filter(Message.session_id == session.id).order_by(Message.timestamp.asc()).all()
            print(f"      消息数: {len(messages)}")
            for msg in messages:
                print(f"        消息ID: {msg.id}, 角色: {msg.role}, 时间: {msg.timestamp}")
                print(f"          内容: {msg.content}")
                if bool(msg.image):
                    print(f"          图片/HTML: {msg.image[:60]}... (省略)")
    print("=== 打印完毕 ===")

if __name__ == "__main__":
    print_db() 