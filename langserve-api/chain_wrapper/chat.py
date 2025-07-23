import sys
import os
import re
from typing import List, Dict, Any, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.graph import MessagesState  # 只保留仍在使用的 MessagesState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import dashscope
from dashscope import MultiModalConversation

_ = load_dotenv(find_dotenv())

# ============================ 基础模型初始化 ============================
model = ChatTongyi(
    streaming=True,
    name="qwen-vl-plus"
)

# ============================ 工具函数 ============================

def make_image_part(data_uri_or_b64: str, default_mime: str = "png") -> Dict[str, str]:
    """根据输入自动生成 DashScope 所需的 image 块。"""
    if data_uri_or_b64.startswith("data:image"):
        image_val = data_uri_or_b64  # 已经是完整的 Data‑URI
    else:
        image_val = f"data:image/{default_mime};base64,{data_uri_or_b64}"
    return {"type": "image", "image": image_val}


def extract_html_only(text: str) -> Union[str, None]:
    """提取首个 <html>/<table>/<img> 代码块。"""
    html_match = re.search(r"(<html[\s\S]*?</html>)", text, re.IGNORECASE)
    if html_match:
        return html_match.group(1)
    table_match = re.search(r"(<table[\s\S]*?</table>)", text, re.IGNORECASE)
    if table_match:
        return table_match.group(1)
    img_match = re.search(r"(<img[^>]*>)", text, re.IGNORECASE)
    if img_match:
        return img_match.group(1)
    return None


def extract_text_only(text: str) -> str:
    """去除所有 HTML 标签，返回纯文本。"""
    return re.sub(r"<[^>]+>", "", text).strip()


def call_model_with_dashscope(messages: List[Dict[str, Any]]) -> str:
    """调用 DashScope 多模态模型。"""
    dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

    ds_messages = []
    for msg in messages:
        if isinstance(msg["content"], list):
            ds_messages.append({"role": msg["role"], "content": msg["content"]})
        else:
            ds_messages.append({"role": msg["role"], "content": [{"text": msg["content"]}]})

    try:
        response = MultiModalConversation.call(model="qwen-vl-plus", messages=ds_messages)
        print("[DashScope返回]", response)

        choices = response.get("output", {}).get("choices", [])
        content = choices[0]["message"]["content"] if choices else ""

        if isinstance(content, dict) and "text" in content:
            return content["text"]
        if isinstance(content, list):
            return "".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in content
            )
        return str(content)
    except Exception as e:
        print(f"[DashScope调用异常]: {e}")
        return "AI接口调用失败，请稍后重试"

# ============================ 主调用链 ============================

def call_model(state: MessagesState, only_html: bool = False) -> str:
    """根据当前会话 state 调用相应模型，返回文本或 HTML。"""

    # ---------- 检测历史消息里是否包含图片 ----------
    has_image = False
    for msg in state["messages"]:
        content = msg["content"]
        if isinstance(content, list):
            if any("image" in part for part in content):
                has_image = True
                break

    # ---------- 组装 system prompt ----------
    if only_html:
        sys_prompt = f"""
你是一名 **资深前端工程师**。请依据下方「设计说明」生成 **完整、可直接打开的 HTML5 文档**，禁止输出除代码外的任何文字！

### 设计说明
{state['messages'][-1].get('content', '')}

### 必须遵循
1. `<!DOCTYPE html>`, `<html lang=\"zh-CN\">`, `<meta charset=\"utf-8\">`, `<meta name=\"viewport\">` 必须存在。
2. 语义化标签 (`header` `main` `section` `nav` `footer`) 且采用 **BEM** 命名。
3. 所有样式写在 `<style>` 内：使用 CSS 变量管理颜色，媒介查询以 768px 为断点。
4. 按钮 `:hover` 使用 scale(1.03)，卡片阴影渐变。
5. 若需图片，请使用占位符 <img src='/assets/placeholder/宽x高.svg' ...>，切勿引用外站 URL。
6. 关键代码块需中文注释解释意图。
7. 生成的代码需要在某个网页的iframe中展示，请防止该代码影响整体网页的样式（一定注意）。
8. 只允许使用不需要依赖包的符号，其他符号如fas禁用
"""
    else:
        sys_prompt = f"""
你是 **顶级 UI/UX 设计师**，请根据「用户需求」与（可选）「参考图片」给出 **结构化 UI 设计说明**，以 **Markdown** 返回。

### 用户需求
{state['messages'][-1].get('content', '')}

### 参考图片
{'已上传，请结合图片风格。' if has_image else '无'}

### 输出格式（严格遵守）
# 对最近一张图片的描述(内容，布局，颜色，风格)
# 整体设计概述 <!-- 50~80 字，突出风格关键词 -->
# 目标受众与场景 <!-- 20~40 字 -->
# 颜色 & 视觉语言
- 主色：`#RRGGBB` – 使用场景
- 辅色：`#RRGGBB` – 使用场景
- 中性色 & 反馈色…
# 版式与网格
1. 布局模式（如 12 栅格 / CSS Grid）
2. 关键断点 (px)
3. 间距体系（间隔 / 圆角基数）
# 核心组件
| 组件 | 交互状态 | 说明 |
|------|----------|------|
| 按钮 | 默认 / Hover / Disabled | … |
| 卡片 | 默认 / 选中 | … |
# 动效与可访问性
- 动效节奏（ease‑in‑out, 200 ms…）
- 键盘导航 / ARIA 标签
"""

    # ---------- 拼接消息列表 ----------
    messages: List[Dict[str, Any]] = [{"role": "system", "content": sys_prompt}]
    for msg in state["messages"]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # ---------- 调用模型 ----------
    if has_image:
        assistant_content = call_model_with_dashscope(messages)
    else:
        lc_messages = []
        for msg in messages:
            if isinstance(msg["content"], list):
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            else:
                lc_messages.append(AIMessage(content=msg["content"]))
        response = model.invoke(lc_messages)
        assistant_content = response.content

    # ---------- 后处理 ----------
    if isinstance(assistant_content, list):
        assistant_content = "".join(str(x) for x in assistant_content)

    html_code = extract_html_only(assistant_content)
    text_only = extract_text_only(assistant_content)

    return html_code if only_html and html_code else text_only if not only_html else assistant_content

# ============================ API 给上层调用 ============================

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database'))
from database.db import get_db
from database.crud import get_session_messages, add_message_to_session


def get_AI_response(session_id: int, flag: int, user_message: str, img_url: str | None = None) -> str:
    """对外统一调用入口。"""

    # 1. 处理用户当次输入
    content: Union[str, List[Dict[str, str]]] = user_message
    if img_url:
        content = [make_image_part(img_url), {"type": "text", "text": user_message}]

    # 2. 读取历史消息
    db = next(get_db())
    db_messages = get_session_messages(db, session_id)
    messages: List[Dict[str, Any]] = []
    for m in db_messages:
        msg_content = m.content
        if m.image:
            msg_content = [{"image": m.image}, {"text": m.content}]
        messages.append({"role": m.role, "content": msg_content})

    # 3. 加入本次用户消息
    messages.append({"role": "user", "content": content})

    # 4. 构造 state ➜ 调用链
    state = MessagesState(messages=messages, session_id=session_id)
    only_html = (flag == 1)
    assistant_reply = call_model(state, only_html=only_html)

    # 5. 持久化 AI 回复
    #add_message_to_session(db, session_id, assistant_reply, "assistant", None)

    return assistant_reply


if __name__ == "__main__":
    # 简单本地测试
    session_id_demo = 0
    print(get_AI_response(session_id_demo, flag=0, user_message="请帮我设计一个健身 App 的首页"))
