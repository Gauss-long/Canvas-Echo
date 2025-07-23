import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
from dotenv import load_dotenv,find_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import base64
import re
import requests
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid
import dashscope
from dashscope import MultiModalConversation
_ = load_dotenv(find_dotenv())

model = ChatTongyi(
    streaming=True,
    name="qwen-vl-plus"
)

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system","你是一名专业的UI设计师。请根据用户的需求和参考图片生成详细的设计方案描述。用户需求: {requirements}参考图片描述: {image_description}请提供以下内容:1. 整体设计风格：100字以内。2. 色彩方案（提供具体色值）。3. 主要布局结构：100字以内。4. 关键UI元素及其样式设计方案描述:"),
        ("system","您每次回答，要么只生成文本，要么只生成HTML代码，多余的部分不要生成，谢谢！"),
        MessagesPlaceholder(variable_name="messages"),
        ("system","如果您已经生成了文字，那么就不要再生成HTML代码；如果您已经生成了HTML代码，那么就不要再生成其他文字消息。"),
        ("system","用户给您发送的图片是参考图片，如果您收到了类似“生成图片”的信息，生成您设计的HTML代码即可。"),
        ("system","您需要做的是生成对应文本或HTML代码，不是在互联网上寻找图片。"),
    ]
)

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

def call_model_with_dashscope(messages):
    dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
    ds_messages = []
    for msg in messages:
        if isinstance(msg["content"], list):
            ds_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        else:
            ds_messages.append({
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            })
    response = MultiModalConversation.call(
        model='qwen-vl-plus',
        messages=ds_messages
    )
    content = response['output']['choices'][0]['message']['content']
    # 新增处理：如果内容是dict且有'text'字段，只取text；如果是list且元素为dict且有text字段，拼接所有text字段
    if isinstance(content, dict) and "text" in content:
        return content["text"]
    elif isinstance(content, list):
        # 拼接所有text字段，如果没有text字段则转为字符串
        return "".join(item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in content)
    return content


def call_model(state: MessagesState, only_html: bool = False):
    # 动态组装prompt
    if only_html:
        sys_prompt = (
            "你是一名专业的前端工程师。根据以下UI设计方案描述生成一个完整的HTML文件："
            f"{state['messages'][-1].get('content', '')}。\n"
            "要求：1. 使用内联CSS样式。2. 实现描述中的所有关键UI元素。3. 使用现代、响应式的布局。4. 确保颜色方案完全匹配。5. 包含所有必要的交互元素。6. 添加适当的注释说明。7. 如果设计方案中包含图片元素，请使用占位符图片（https://via.placeholder.com/尺寸?text=描述）。8. 添加细腻的阴影、圆角、渐变、hover 动效等现代 UI 细节。请只输出HTML代码，不要包含任何额外解释或标记。"
        )
    else:
        sys_prompt = (
            "你是一名专业的UI设计师。请根据用户的需求和参考图片生成详细的设计方案描述，注意应该严格生成markdown格式！ \n"
            f"用户需求: {state['messages'][-1].get('content', '')} "
            f"{'图片已上传。' if state['messages'][-1].get('image') else ''}"
            "请提供以下内容: 1. 整体设计风格（100字以内）。2. 色彩方案（提供具体色值）。3. 主要布局结构（100字以内）。4. 关键UI元素布局及其样式设计方案描述。"
        )
    # 组装消息
    messages = [{"role": "system", "content": sys_prompt}]
    has_image = False
    for msg in state["messages"]:
        content = msg["content"]
        if isinstance(content, list):
            for part in content:
                if "image" in part:
                    has_image = True
            messages.append({"role": msg["role"], "content": content})
        else:
            messages.append({"role": msg["role"], "content": content})

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

    # 后处理：只保留HTML或只保留文本
    # 修复：dashscope有时返回list（多段内容），需拼接为字符串
    if isinstance(assistant_content, list):
        assistant_content = "".join(str(x) for x in assistant_content)
    html_code = extract_html_only(assistant_content)
    text_only = extract_text_only(assistant_content)
    if only_html:
        return html_code if html_code else assistant_content
    else:
        return text_only if text_only else assistant_content

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

def image_file_to_base64(path):
    try:
        import mimetypes
        # 检测文件类型
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            mime_type = "image/jpeg"  # 默认值

        with open(path, "rb") as f:
            base64_data = base64.b64encode(f.read()).decode("utf-8")
            print(f"图片文件: {path}, 检测到的MIME类型: {mime_type}")
            return base64_data
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

def image_url_to_base64(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        # 从响应头获取MIME类型
        mime_type = resp.headers.get('content-type', 'image/jpeg')
        base64_data = base64.b64encode(resp.content).decode("utf-8")
        print(f"图片URL: {url}, 检测到的MIME类型: {mime_type}")
        return base64_data
    except Exception as e:
        print(f"下载图片失败: {e}")
        return None

def save_base64_image_to_file(data_url, save_dir="uploaded_images"):
    match = re.match(r"data:image/(.*?);base64,(.*)", data_url)
    if not match:
        return None
    ext, b64data = match.groups()
    ext = ext.split(';')[0]
    filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(b64data))
    return file_path


# 全局会话消息存储
SESSION_CONTEXTS = {}

def get_AI_response(session_id: int, flag: int, user_message: str, img_base64: str | None = None):
    import base64, uuid, os

    content = user_message
    if img_base64:
        # 只处理 base64 编码，直接保存为本地图片
        ext = "png"
        filename = f"{uuid.uuid4().hex}.{ext}"
        save_dir = "uploaded_images"
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(img_base64))
        content = [
            {"image": file_path},
            {"text": user_message}
        ]

    messages = SESSION_CONTEXTS.get(session_id, []).copy()
    messages.append({"role": "user", "content": content})
    SESSION_CONTEXTS[session_id] = messages

    state = MessagesState(messages=messages, session_id=session_id)
    only_html = (flag == 1)
    return call_model(state, only_html=only_html)


if __name__ == "__main__":
    print("=== 测试图片+上下文记忆功能 ===")
    session_img = 303
    test_img_path = r"C:\Users\68078\Pictures\Screenshots\pvz.png" # 修改为你的本地图片路径

    print("\n[Session-图片] 用户: 请描述一下这张图片")
    result1 = get_AI_response(session_img, 0, "请描述一下这张图片", test_img_path)
    print("[Session-图片-回复1]:", result1)

    print("\n[Session-图片] 用户: 请参考这张图片设计一个界面")
    result2 = get_AI_response(session_img, 1, "请参考这张图片设计一个界面")
    print("[Session-图片-回复2]:", result2)


