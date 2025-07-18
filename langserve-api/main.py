#!/usr/bin/env python
from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import StreamingResponse
import asyncio
import json
from chain_wrapper import chat as chat_chain
from fastapi import Depends, HTTPException
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import crud, db as db_module
from sqlalchemy.orm import Session
from database import function as db_func  # 新增：引入 function.py

# 创建FastAPI应用
app = FastAPI(
    title="Canvas Echo API",
    version="1.0",
    description="简化的Canvas Echo API服务器"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    content: str

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
    print(f"收到聊天请求：{request.content}")
    # 构造消息格式
    input_messages = [{"role": "user", "content": request.content}]
    # 调用chat_chain.app的astream方法，流式返回
    async def stream_llm():
        async for chunk, meta in chat_chain.app.astream({"messages": input_messages}, config=chat_chain.config, stream_mode="messages"):
            # chunk是AI回复内容
            if hasattr(chunk, 'content'):
                yield chunk.content
            elif isinstance(chunk, dict) and 'content' in chunk:
                yield chunk['content']
            else:
                yield str(chunk)
    return StreamingResponse(stream_llm(), media_type="text/event-stream")

@app.post("/api/chat_reason")
async def chat_reason(request: ChatRequest):
    """推理型聊天API"""
    print(f"收到推理请求：{request.content}")
    return StreamingResponse(
        generate_response(f"[推理模式] {request.content}"),
        media_type="text/event-stream"
    )

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
        "created_at": session.created_at,"messages":[]}
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