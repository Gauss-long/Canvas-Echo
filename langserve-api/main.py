#!/usr/bin/env python
from fastapi import FastAPI
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
def db_login(request: LoginRequest, db: Session = Depends(db_module.get_db)):
    user = crud.authenticate_user(db, request.username, request.password)
    if user:
        return {"success": True, "username": user.username}
    else:
        return {"success": False, "message": "用户名或密码错误"}

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