import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
from dotenv import load_dotenv,find_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import base64
import re
import requests
from langchain_core.messages import HumanMessage
from database.function import get_messages_by_session_id
_ = load_dotenv(find_dotenv())

model = ChatTongyi(
    streaming=True,
    name="qwen-vl-max"
)

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system","你是一位乐于助人的HTML设计师，尽你所能为用户进行设计。您每次回答，要么只生成文本，要么只生成HTML代码，多余的部分不要生成，谢谢。"),
        ("system","您每次回答，要么只生成文本，要么只生成HTML代码，多余的部分不要生成，谢谢！"),       MessagesPlaceholder(variable_name="messages"),
        ("system","如果您已经生成了文字，那么就不要再生成HTML代码；如果您已经生成了HTML代码，那么就不要再生成其他文字消息。"),
        ("system","用户给您发送的图片是参考图片，如果您收到了类似“生成图片”的信息，生成您设计的HTML代码即可。"),
        ("system","您需要做的是生成对应文本或HTML代码，不是在互联网上寻找图片。"),
    ]
)

from database.db import SessionLocal
from database.crud import add_message_to_session

def extract_html_only(text):
    """提取第一个<html>、<table>或<img>标签及其内容"""
    html_match = re.search(r'(<html[\s\S]*?</html>)', text, re.IGNORECASE)
    if html_match:
        return html_match.group(1)
    table_match = re.search(r'(<table[\s\S]*?</table>)', text, re.IGNORECASE)
    if table_match:
        return table_match.group(1)
    img_match = re.search(r'(<img[^>]*>)', text, re.IGNORECASE)
    if img_match:
        return img_match.group(1)
    return None

def extract_text_only(text):
    """去除所有HTML标签，仅保留纯文本"""
    return re.sub(r'<[^>]+>', '', text).strip()

def call_model(state: MessagesState, session_id: int, only_html: bool = False):
    db = SessionLocal()
    try:
        # 动态组装prompt
        if only_html:
            sys_msgs = [
                ("system", "您是一位乐于助人的HTML设计师，只能生成HTML代码，不能生成任何解释、说明或文本。"),
                ("system", "请严格只输出HTML代码，不要输出任何其他内容。"),
            ]
        else:
            sys_msgs = [
                ("system", "您是一位乐于助人的设计师，只能生成纯文本，不能生成任何HTML代码。"),
                ("system", "请严格只输出文本，不要输出任何HTML代码或标签。"),
            ]
        # 组装完整上下文
        messages = []
        for sys_msg in sys_msgs:
            messages.append({"role": sys_msg[0], "content": sys_msg[1]})
        for msg in state["messages"]:
            if msg["role"] == "user":
                msg_content = []
                if msg.get("content"):
                    msg_content.append({"text": msg["content"]})
                if msg.get("image"):
                    msg_content.append({"image": msg["image"]})
                messages.append(HumanMessage(content=msg_content))
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
        response = model.invoke(messages)
        assistant_content = response.content
        html_code = extract_html_only(assistant_content)
        text_only = extract_text_only(assistant_content)
        # 删除：AI回复写入数据库逻辑
        # 只返回内容，由前端负责写入数据库
    finally:
        db.close()
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

#全局 memory 字典
memory_dict = {}

def get_app_for_session(session_id):
    sid = str(session_id)
    if sid not in memory_dict:
        memory_dict[sid] = MemorySaver()
    memory = memory_dict[sid]
    return workflow.compile(checkpointer=memory)

def image_file_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

def image_url_to_base64(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode("utf-8")
    except Exception as e:
        print(f"下载图片失败: {e}")
        return None

config = {
    "configurable":{
        "session_id":time.time(),
        "thread_id":time.time()
    }
}


def run_chat_console():
    session_id = input("请输入session_id（数字）：").strip()
    if not session_id.isdigit():
        print("session_id必须为数字！")
        return
    session_id = int(session_id)
    app = get_app_for_session(session_id)
    messages = []  # 用于存储本 session 的历史消息
    while True:
        user_message = input("请输入文本：").strip()
        if not user_message:
            print("已退出。")
            break
        img_path = input("请输入本地图片路径或图片URL（直接回车跳过）：").strip()
        image_val = None
        if img_path:
            if img_path.startswith("http://") or img_path.startswith("https://"):
                image_val = image_url_to_base64(img_path)
            else:
                image_val = image_file_to_base64(img_path)
            if not image_val:
                print("图片读取失败，将跳过图片。")
        while True:
            only_html_input = input("生成HTML代码输入1，生成文本输入0：").strip()
            if only_html_input in ("0", "1"):
                only_html = only_html_input == "1"
                break
            else:
                print("请输入0或1。"); continue
        # 追加本轮 user 消息
        messages.append({"role": "user", "content": user_message, "image": image_val})
        state = MessagesState(messages=messages)
        result = call_model(state, session_id, only_html=only_html)
        response = result["messages"]
        # 追加本轮 assistant 消息
        messages.append({"role": "assistant", "content": response.content, "image": None})
        print(f"助手: {response.content}")

def get_AI_response(session_id: int, flag: int, user_message: str, img_path: str = None):
    """
    支持多轮上下文的对话函数。参数：
    - session_id: 会话ID（int）
    - flag: 0=输出文本，1=输出HTML代码
    - user_message: 用户输入的文字（不可为空）
    - img_path: 图片路径或URL（可为空）
    返回：模型输出内容
    """
    if not user_message or not user_message.strip():
        print("用户输入不能为空。")
        return None

    image_val = None
    if img_path:
        if img_path.startswith("http://") or img_path.startswith("https://"):
            image_val = image_url_to_base64(img_path)
        else:
            image_val = image_file_to_base64(img_path)
        if not image_val:
            print("图片读取失败，将跳过图片。")

    # 1. 获取历史消息
    db = SessionLocal()
    try:
        db_messages = get_messages_by_session_id(session_id)
        # 只取最近10条
        db_messages = db_messages[-10:]
        messages = []
        for m in db_messages:
            messages.append({
                "role": m.role,
                "content": m.content,
                "image": m.image if hasattr(m, 'image') else None
            })
        # 2. 追加本轮 user 消息
        messages.append({"role": "user", "content": user_message, "image": image_val})
        state = MessagesState(messages=messages)
        only_html = (flag == 1)
        result = call_model(state, session_id, only_html=only_html)
        response = result["messages"]
        return response.content
    finally:
        db.close()     