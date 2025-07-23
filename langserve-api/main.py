#!/usr/bin/env python
from fastapi import FastAPI,Response
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse
import json
from  chain_wrapper import chat as chat_chain
from chain_wrapper import title as title_chain
from fastapi import Depends, HTTPException
import os
import sys
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import crud, db as db_module
from sqlalchemy.orm import Session
from database import function as db_func  # 新增：引入 function.py

# 创建FastAPI应用
app = FastAPI(
    title="Canvas Echo API",
    version="4.5",
    description="高级的Canvas Echo API服务器"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ HTML→PNG 路由 --------------------------
class Html2PngReq(BaseModel):
    html: str
    width: int = 1280
    height: int = 720
    scale: float = 1.0
    full_page: bool = True

class Input(BaseModel):
    content: str

class ChatRequest(BaseModel):
    session_id: int  # 新增字段
    flag: int
    user_message: str
    img_url: str
    
    

class LoginRequest(BaseModel):
    username: str
    password: str

class MessageRequest(BaseModel):
    session_id: int
    content: str
    role: str
    image: str
class MessagePairRequest(BaseModel):
    session_id1: int
    content1: str
    role1: str
    image1: str   
    session_id2: int
    content2: str
    role2: str
    image2: str 

class CreateSessionRequest(BaseModel):
    user_id: int
    title: str = "新对话"
class DeleteSessionRequest(BaseModel):
    session_id: int

class UpdateSessionTitleRequest(BaseModel):
    session_id: int
    title: str

class MarkStartedRequest(BaseModel):
       session_id: int

async def generate_response(content: str):
    """生成模拟的AI回复"""
    # 模拟AI思考过程
    responses = [
        "111",  # 统一回复111
        f"您说：{content}，我的回复是：111",
        "这是一个很好的问题！答案是：111",
        "根据我的分析，结果是：111",
        "让我为您详细解释：111"
    ]
    
    import random
    response = random.choice(responses)
    
    # 模拟流式响应
    for char in response:
        yield char
        await asyncio.sleep(0.05)  # 50ms延迟

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """调用真实大模型的API"""
    print(f"收到聊天请求：{request.user_message}，session_id={request.session_id}")
    return {"success": True, "message": chat_chain.get_AI_response(request.session_id, request.flag, request.user_message, request.img_url)}

@app.post("/api/title")
async def title(request: Input):
    """生成标题"""
    print(f"收到标题请求：{request.content}")
    return {"success": True, "title": title_chain.get_title(request.content)}

@app.post("/db/login")
def db_login(request: LoginRequest):
    user = db_func.login_user(request.username, request.password)
    if user:
        return {"success": True, "username": user.username, "user_id": user.id}
    else:
        return {"success": False, "message": "用户名或密码错误"}

@app.get("/db/history")
def db_history(username: str = Query(...)):
    sessions = db_func.get_user_history(username)
    if sessions is None:
        return {"success": False, "message": "用户不存在"}
    return {"success": True, "sessions": sessions}


@app.post("/db/create_session")
def create_session_api(request: CreateSessionRequest):
    session = db_func.create_session(request.user_id, request.title)
    if session:
        return {"success": True, "session_id": session.id,"user_id": session.user_id,"title": session.title,
        "created_at": session.created_at,"messages":[],"is_started": getattr(session, 'is_started', 0)  }
    else:
        return {"success": False, "message": "创建会话失败"}

@app.delete("/db/delete_session")
def delete_session_api(req: DeleteSessionRequest):
    db_func.delete_session(req.session_id)
    return {"success": True}

@app.post("/db/create_message")
def create_message_api(req: MessageRequest):
    db_func.create_message(
        req.session_id,
        req.content,
        req.role,
        req.image
    )
    return {"success": True}
@app.post("/db/create_message_pair")
def create_message_pair_api(req: MessagePairRequest):
    db_func.create_message(
        req.session_id1,
        req.content1,
        req.role1,
        req.image1
    )
    db_func.create_message(
        req.session_id2,
        req.content2,
        req.role2,
        req.image2
    )
    return {"success": True}

@app.get("/db/get_max_message_id")
def get_max_message_id_api():
    max_id = db_func.get_max_message_id()
    return {"success": True, "max_id": max_id}

@app.post("/db/update_session_title")
def update_session_title_api(request: UpdateSessionTitleRequest):
    db_func.update_session_title(request.session_id, request.title)
    return {"success": True}

@app.get("/db/get_all_versions")
def get_all_versions_api(session_id: int):
    versions = db_func.get_all_versions(session_id)
    # 只返回 content 字段组成的数组
    html_list = [v.content for v in versions]
    #print(html_list)
    return {"success": True, "versions": html_list}

@app.post("/db/mark_started")
def mark_started_api(request: MarkStartedRequest):
    db_func.mark_started(request.session_id)
    return {"success": True}



@app.get("/")
async def root():
    """根路径"""
    return {"message": "Canvas Echo API 服务器运行正常"}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "Canvas Echo API"}

if __name__ == "__main__":
    import uvicorn
    print("启动Canvas Echo API服务器...")
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 