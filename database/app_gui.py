import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
from .db import init_db, get_db
from .crud import (
    create_user, get_user_by_username, authenticate_user,
    create_user_session, get_user_sessions, delete_session,
    add_message_to_session, get_session_messages, get_session_by_id
)
from . import schemas
from . import models
import base64
import os
import tempfile
import webbrowser
import sys
from passlib.context import CryptContext

if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "database"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("我也不知道我到底是啥")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # 初始化数据库
        init_db()

        # 当前用户和会话状态
        self.current_user = None
        self.current_session = None

        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 显示登录界面
        self.show_login_screen()

    def clear_frame(self):
        """清除当前框架内容"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """显示登录界面"""
        self.clear_frame()
        self.current_user = None
        self.current_session = None
        # 登录表单
        login_frame = ttk.LabelFrame(self.main_frame, text="用户登录")
        login_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        # 用户名
        ttk.Label(login_frame, text="用户名:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        # 密码
        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        # 按钮框架
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        # 登录按钮
        login_button = ttk.Button(button_frame, text="登录", command=self.login)
        login_button.pack(side=tk.LEFT, padx=10)
        # 注册按钮
        register_button = ttk.Button(button_frame, text="注册", command=self.show_register_screen)
        register_button.pack(side=tk.LEFT, padx=10)
        # 设置初始焦点
        self.username_entry.focus_set()

    def show_register_screen(self):
        """显示注册界面"""
        self.clear_frame()
        # 注册表单
        register_frame = ttk.LabelFrame(self.main_frame, text="用户注册")
        register_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        # 用户名
        ttk.Label(register_frame, text="用户名:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.reg_username_entry = ttk.Entry(register_frame, width=30)
        self.reg_username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        # 密码
        ttk.Label(register_frame, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.reg_password_entry = ttk.Entry(register_frame, width=30, show="*")
        self.reg_password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        # 确认密码
        ttk.Label(register_frame, text="确认密码:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.reg_confirm_entry = ttk.Entry(register_frame, width=30, show="*")
        self.reg_confirm_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        # 按钮框架
        button_frame = ttk.Frame(register_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        # 注册按钮
        register_button = ttk.Button(button_frame, text="注册", command=self.register)
        register_button.pack(side=tk.LEFT, padx=10)
        # 返回按钮
        back_button = ttk.Button(button_frame, text="返回登录", command=self.show_login_screen)
        back_button.pack(side=tk.LEFT, padx=10)
        # 设置初始焦点
        self.reg_username_entry.focus_set()
    def login(self):
        """处理用户登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("输入错误", "用户名和密码不能为空")
            return
        db = next(get_db())
        user = authenticate_user(db, username, password)
        if user:
            self.current_user = user
            self.show_main_screen()
        else:
            messagebox.showerror("登录失败", "用户名或密码不正确")
    def register(self):
        """处理用户注册"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm = self.reg_confirm_entry.get().strip()
        if not username or not password:
            messagebox.showerror("输入错误", "用户名和密码不能为空")
            return
        if password != confirm:
            messagebox.showerror("输入错误", "两次输入的密码不一致")
            return
        db = next(get_db())
        # 检查用户名是否已存在
        if get_user_by_username(db, username):
            messagebox.showerror("注册失败", "用户名已存在")

            return
        # 创建新用户 - 使用 UserCreate 对象
        user_data = schemas.UserCreate(username=username, password=password)
        create_user(db, user_data)
        messagebox.showinfo("注册成功", "用户注册成功，请登录")
        self.show_login_screen()

    def show_main_screen(self):
        """显示主界面（会话列表）"""
        self.clear_frame()
        self.root.title(f"欢迎 {self.current_user.username}")

        # 主框架
        main_frame = ttk.Frame(self.main_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧会话列表
        session_frame = ttk.LabelFrame(main_frame, text="会话列表")
        session_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # 会话列表
        self.session_tree = ttk.Treeview(session_frame, columns=("created"), show="headings")
        self.session_tree.heading("#0", text="标题")
        self.session_tree.heading("created", text="创建时间")
        self.session_tree.column("#0", width=150)
        self.session_tree.column("created", width=150)
        self.session_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 会话列表按钮
        button_frame = ttk.Frame(session_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        new_button = ttk.Button(button_frame, text="新建会话", command=self.create_session)
        new_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text="删除会话", command=self.delete_session)
        delete_button.pack(side=tk.LEFT, padx=5)

        logout_button = ttk.Button(button_frame, text="退出登录", command=self.show_login_screen)
        logout_button.pack(side=tk.RIGHT, padx=5)

        # 右侧会话详情
        self.detail_frame = ttk.LabelFrame(main_frame, text="会话详情")
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 初始加载会话
        self.load_sessions()
        # 绑定选择事件
        self.session_tree.bind("<<TreeviewSelect>>", self.on_session_select)

        # 添加提示文本
        if not self.session_tree.get_children():
            ttk.Label(self.detail_frame, text="请选择一个会话或创建新会话").pack(expand=True)

    def load_sessions(self):
        """加载用户会话"""
        db = next(get_db())
        sessions = get_user_sessions(db, self.current_user.id)
        # 清除现有会话
        for item in self.session_tree.get_children():
            self.session_tree.delete(item)
        # 添加新会话
        for session in sessions:
            self.session_tree.insert("", "end",
                                     iid=session.id,
                                     text=session.title,
                                     values=(session.created_at.strftime("%Y-%m-%d %H:%M"),))
        # 如果没有会话，显示提示
        if not sessions:
            self.detail_frame.config(text="会话详情")
            ttk.Label(self.detail_frame, text="没有可显示的会话，请创建新会话").pack(expand=True)
    def create_session(self):
        """创建新会话"""
        db = next(get_db())
        session = create_user_session(db, self.current_user.id, title=f"会话 {datetime.now().strftime('%m-%d %H:%M')}")
        self.load_sessions()
        # 选择新创建的会话
        self.session_tree.selection_set(str(session.id))
        self.on_session_select()

    def delete_session(self):
        """删除选中的会话"""
        selected = self.session_tree.selection()
        if not selected:
            messagebox.showwarning("删除会话", "请先选择一个会话")
            return

        session_id = int(selected[0])
        db = next(get_db())

        # 获取会话消息数量
        messages = get_session_messages(db, session_id)

        # 确认对话框
        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除这个会话吗?\n会话包含 {len(messages)} 条消息"
        )
        if not confirm:
            return

        # 删除会话
        if delete_session(db, session_id):
            self.load_sessions()
            self.detail_frame.config(text="会话详情")
            # 清除详情区域
            for widget in self.detail_frame.winfo_children():
                widget.destroy()

            # 添加提示文本
            ttk.Label(self.detail_frame, text="请选择一个会话或创建新会话").pack(expand=True)

            messagebox.showinfo("删除成功", "会话已成功删除")
        else:
            messagebox.showerror("删除失败", "无法删除会话")

    def on_session_select(self, event=None):
        """处理会话选择事件"""
        selected = self.session_tree.selection()
        if not selected:
            return
        session_id = int(selected[0])
        db = next(get_db())
        session = get_session_by_id(db, session_id)
        if not session:
            return
        self.current_session = session
        self.detail_frame.config(text=f"会话: {session.title}")

        # 清除详情区域

        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # 创建聊天界面

        self.create_chat_interface()

    def create_chat_interface(self):
        """创建聊天界面"""
        # 消息显示区域
        msg_frame = ttk.Frame(self.detail_frame)
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 使用PanedWindow实现可调整的分割
        self.paned_window = tk.PanedWindow(msg_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=4)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 文本消息区域
        text_frame = ttk.Frame(self.paned_window)
        self.text_scrollbar = ttk.Scrollbar(text_frame)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.msg_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=self.text_scrollbar.set,
            state=tk.DISABLED
        )
        self.msg_text.pack(fill=tk.BOTH, expand=True)
        self.text_scrollbar.config(command=self.msg_text.yview)

        # HTML预览区域
        self.html_frame = ttk.LabelFrame(self.paned_window, text="HTML预览")
        self.html_text = scrolledtext.ScrolledText(
            self.html_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED
        )
        self.html_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # HTML预览按钮
        html_button_frame = ttk.Frame(self.html_frame)
        html_button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.view_html_button = ttk.Button(
            html_button_frame,
            text="在浏览器中查看",
            command=self.view_html_in_browser,
            state=tk.DISABLED
        )
        self.view_html_button.pack(side=tk.RIGHT, padx=5)

        # 添加区域到分割窗口
        self.paned_window.add(text_frame)
        self.paned_window.add(self.html_frame)

        # 初始设置分割比例
        self.paned_window.paneconfigure(text_frame, height=400)
        self.paned_window.paneconfigure(self.html_frame, height=150)

        # 输入区域
        input_frame = ttk.Frame(self.detail_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # 多行文本输入框
        self.input_text = scrolledtext.ScrolledText(input_frame, height=4)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.input_text.bind("<Control-Return>", self.send_message)

        # 按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # 图片上传按钮
        image_button = ttk.Button(button_frame, text="上传图片", command=self.upload_image)
        image_button.pack(side=tk.LEFT, padx=5)

        # 发送按钮
        send_button = ttk.Button(button_frame, text="发送消息", command=self.send_message)
        send_button.pack(side=tk.RIGHT, padx=5)

        # 加载历史消息
        self.load_messages()

        # 设置输入焦点
        self.input_text.focus_set()

    def upload_image(self):
        """上传图片并转换为base64"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )

        if not file_path:
            return

        try:
            # 读取图片并转换为base64
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # 获取文件名
            filename = os.path.basename(file_path)

            # 在输入框中添加图片标记
            self.input_text.insert(tk.END, f"[图片:{filename}:{encoded_string}]\n")
            messagebox.showinfo("上传成功", f"图片 '{filename}' 已添加到消息中")
        except Exception as e:
            messagebox.showerror("上传失败", f"无法处理图片: {str(e)}")

    def load_messages(self):
        """加载会话消息"""
        if not self.current_session:
            return

        db = next(get_db())
        messages = get_session_messages(db, self.current_session.id)

        # 清空消息区域
        self.msg_text.config(state=tk.NORMAL)
        self.msg_text.delete(1.0, tk.END)
        self.html_text.config(state=tk.NORMAL)
        self.html_text.delete(1.0, tk.END)
        self.view_html_button.config(state=tk.DISABLED)

        # 添加消息
        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M")
            role = "用户" if msg.role == "user" else "助手"

            # 根据内容类型处理
            if msg.content_type == "image":
                # 提取图片信息
                if msg.content.startswith("[图片:") and msg.content.endswith("]"):
                    parts = msg.content[4:-1].split(":", 1)
                    if len(parts) == 2:
                        filename, encoded_string = parts
                        display_content = f"[图片: {filename}]"
                    else:
                        display_content = "[图片]"
                else:
                    display_content = "[图片]"

                self.msg_text.insert(tk.END, f"[{timestamp}] {role}: {display_content}\n\n")

            elif msg.content_type == "html":
                self.msg_text.insert(tk.END, f"[{timestamp}] {role}: [HTML内容]\n\n")

                # 如果是助手的最新HTML消息，显示在预览区域
                if role == "助手":
                    self.html_text.config(state=tk.NORMAL)
                    self.html_text.delete(1.0, tk.END)
                    self.html_text.insert(tk.END, msg.content)
                    self.html_text.config(state=tk.DISABLED)
                    self.view_html_button.config(state=tk.NORMAL)

            else:  # 文本消息
                self.msg_text.insert(tk.END, f"[{timestamp}] {role}: {msg.content}\n\n")

        self.msg_text.config(state=tk.DISABLED)
        self.msg_text.yview(tk.END)  # 滚动到底部

    def view_html_in_browser(self):
        """在浏览器中查看HTML内容"""
        html_content = self.html_text.get("1.0", tk.END).strip()
        if not html_content:
            return

        try:
            # 创建临时HTML文件
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name

            # 在浏览器中打开
            webbrowser.open(f"file://{temp_file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法查看HTML: {str(e)}")

    def send_message(self, event=None):
        """发送消息"""
        if not self.current_session:
            return

        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            return

        # 保存用户消息
        db = next(get_db())
        add_message_to_session(
            db,
            self.current_session.id,
            content,
            "user",
            "text"  # 统一为文本类型，图片作为文本的一部分
        )

        # 生成助手回复
        assistant_response, response_type = self.generate_response(content, "text")

        # 保存助手回复
        add_message_to_session(
            db,
            self.current_session.id,
            assistant_response,
            "assistant",
            response_type
        )

        # 重新加载消息
        self.load_messages()

        # 清空输入框
        self.input_text.delete("1.0", tk.END)

    def generate_response(self, user_message, user_content_type):
        """生成助手回复（支持图片和HTML）"""
        if user_content_type == "image":
            # 提取图片信息
            if user_message.startswith("[图片:") and user_message.endswith("]"):
                parts = user_message[4:-1].split(":", 1)
                if len(parts) == 2:
                    filename, encoded_string = parts

                    # 生成包含图片的HTML回复
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>图片分析结果</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; padding: 20px; }}
                            .container {{ max-width: 800px; margin: 0 auto; }}
                            .image-box {{ text-align: center; margin: 20px 0; }}
                            .analysis {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h2>图片分析结果</h2>
                            <div class="image-box">
                                <img src="data:image/png;base64,{encoded_string}" alt="{filename}" style="max-width: 100%;">
                                <p>上传图片: {filename}</p>
                            </div>
                            <div class="analysis">
                                <h3>分析结果:</h3>
                                <p>系统已成功接收您上传的图片，并进行了以下分析：</p>
                                <ul>
                                    <li>图片尺寸: 800x600 (示例)</li>
                                    <li>主要颜色: #FF5733, #33FF57, #3357FF</li>
                                    <li>检测到对象: 人物(85%), 建筑(72%), 天空(68%)</li>
                                </ul>
                                <p>如需进一步分析，请提供更多细节要求。</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    return html_content, "html"

        # 默认文本回复
        responses = [
            "您的问题已收到，正在处理中...",
            "根据您的查询，我找到以下信息...",
            "分析完成，以下是详细结果:",
            "建议您考虑以下方案:",
            "系统处理完成，请查看以下回复:"
        ]

        # 随机选择一个响应
        import random
        response = random.choice(responses)

        # 20%的概率生成HTML回复
        if random.random() < 0.2:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>分析报告</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 15px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .result {{ background-color: #f9f9f9; border-left: 4px solid #4CAF50; padding: 10px 15px; margin: 15px 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>数据分析报告</h1>
                        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>

                    <div class="content">
                        <h2>查询内容:</h2>
                        <p>{user_message}</p>

                        <h2>分析结果:</h2>
                        <div class="result">
                            <p>系统已分析您的查询，以下是详细结果:</p>
                            <ul>
                                <li>相关性评分: 87%</li>
                                <li>主要关键词: "开发", "数据库", "管理"</li>
                                <li>建议操作: 数据备份, 性能优化</li>
                            </ul>
                        </div>

                        <h2>详细数据:</h2>
                        <table>
                            <tr>
                                <th>指标</th>
                                <th>当前值</th>
                                <th>建议值</th>
                                <th>状态</th>
                            </tr>
                            <tr>
                                <td>数据库负载</td>
                                <td>72%</td>
                                <td>&lt;60%</td>
                                <td>⚠️ 偏高</td>
                            </tr>
                            <tr>
                                <td>查询响应时间</td>
                                <td>320ms</td>
                                <td>&lt;200ms</td>
                                <td>⚠️ 偏慢</td>
                            </tr>
                            <tr>
                                <td>缓存命中率</td>
                                <td>64%</td>
                                <td>&gt;80%</td>
                                <td>⚠️ 不足</td>
                            </tr>
                        </table>

                        <h2>建议:</h2>
                        <ol>
                            <li>优化数据库索引结构</li>
                            <li>增加缓存服务器资源</li>
                            <li>执行查询语句优化</li>
                            <li>考虑分库分表策略</li>
                        </ol>
                    </div>
                </div>
            </body>
            </html>
            """
            return html_content, "html"

        return response, "text"


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()