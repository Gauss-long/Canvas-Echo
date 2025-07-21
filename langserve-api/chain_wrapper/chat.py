from dotenv import load_dotenv,find_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time

_ = load_dotenv(find_dotenv())

model = ChatTongyi(
    streaming=True,
    name="qwen-turbo"
)

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system","你是一位乐于助人的助手。尽你所能回答所有问题。"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# 新增：全局 memory 字典
memory_dict = {}

def get_app_for_session(session_id):
    sid = str(session_id)
    if sid not in memory_dict:
        memory_dict[sid] = MemorySaver()
    memory = memory_dict[sid]
    return workflow.compile(checkpointer=memory)

config = {
    "configurable":{
        "session_id":time.time(),
        "thread_id":time.time()
    }
}

