import tkinter as tk
from tkinter import ttk, messagebox
from .db import get_db
from .crud import get_user_by_username, get_user_sessions, get_session_messages, delete_session, create_user
from sqlalchemy.orm import Session
from .models import User
from . import schemas


def load_all_users():
    db = next(get_db())
    users = db.query(User).all()
    db.close()

    # 清空表格
    for item in tree.get_children():
        tree.delete(item)

    # 填充表格
    for user in users:
        tree.insert("", "end", values=(user.id, user.username, user.password_hash, user.created_at.strftime("%Y-%m-%d %H:%M:%S")), iid=str(user.id))


def delete_selected_user():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("删除用户", "请先选择一个用户")
        return

    for item in selected_items:
        user_id = int(tree.item(item)['values'][0])
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # 先删除用户的所有会话
            sessions = get_user_sessions(db, user_id)
            for session in sessions:
                session_id = getattr(session, 'id', None)
                if session_id is not None and isinstance(session_id, int):
                    delete_session(db, session_id)
            # 再删除用户
            db.delete(user)
            db.commit()
            db.close()
            messagebox.showinfo("成功", f"已删除用户 ID 为 {user_id} 的用户")
        else:
            db.close()
            messagebox.showerror("错误", f"未找到用户 ID 为 {user_id} 的用户")
    load_all_users()


def register_user():
    # 创建注册窗口
    register_window = tk.Toplevel(root)
    register_window.title("注册用户")

    # 用户名
    ttk.Label(register_window, text="用户名:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    username_entry = ttk.Entry(register_window, width=30)
    username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

    # 密码
    ttk.Label(register_window, text="密码:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    password_entry = ttk.Entry(register_window, width=30, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

    def submit_registration():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("输入错误", "用户名和密码不能为空")
            return
        db = next(get_db())
        # 检查用户名是否已存在
        if get_user_by_username(db, username):
            messagebox.showerror("注册失败", "用户名已存在")
            return
        # 创建新用户 - 使用 UserCreate 对象
        user_data = schemas.UserCreate(username=username, password=password)
        create_user(db, user_data)
        messagebox.showinfo("注册成功", "用户注册成功")
        register_window.destroy()
        load_all_users()

    # 注册按钮
    register_button = ttk.Button(register_window, text="注册", command=submit_registration)
    register_button.grid(row=2, column=0, columnspan=2, pady=20)


# 创建主窗口
root = tk.Tk()
root.title("管理员后台管理")
root.geometry("900x600")
root.minsize(700, 400)

# 让主窗口自适应
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

# 操作按钮框架
button_frame = ttk.Frame(root)
button_frame.grid(row=0, column=0, sticky="ew", pady=10)
button_frame.columnconfigure(0, weight=1)

# 删除用户按钮
button_delete_user = ttk.Button(button_frame, text="删除用户", command=delete_selected_user)
button_delete_user.pack(side=tk.LEFT, padx=10)

# 注册用户按钮
button_register_user = ttk.Button(button_frame, text="注册用户", command=register_user)
button_register_user.pack(side=tk.LEFT, padx=10)

# 创建表格和滚动条
frame_tree = tk.Frame(root)
frame_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
frame_tree.rowconfigure(0, weight=1)
frame_tree.columnconfigure(0, weight=1)

xscroll = tk.Scrollbar(frame_tree, orient='horizontal')
xscroll.grid(row=1, column=0, sticky='ew')
yscroll = tk.Scrollbar(frame_tree, orient='vertical')
yscroll.grid(row=0, column=1, sticky='ns')

tree = ttk.Treeview(
    frame_tree,
    columns=("ID", "用户名", "密码", "注册时间"),
    show="headings",
    xscrollcommand=xscroll.set,
    yscrollcommand=yscroll.set
)
tree.grid(row=0, column=0, sticky="nsew")

xscroll.config(command=tree.xview)
yscroll.config(command=tree.yview)

tree.heading("ID", text="ID")
tree.heading("用户名", text="用户名")
tree.heading("密码", text="密码")
tree.heading("注册时间", text="注册时间")
tree.column("ID", width=100, anchor='center')
tree.column("用户名", width=150, anchor='center')
tree.column("密码", width=350, anchor='w')
tree.column("注册时间", width=200, anchor='center')

# 支持双击显示完整密码

def on_tree_double_click(event):
    selection = tree.selection()
    if selection:
        item = selection[0]
        values = tree.item(item, "values")
        messagebox.showinfo("完整密码", f"密码：{values[2]}")

tree.bind("<Double-1>", on_tree_double_click)

# 加载所有用户
load_all_users()

# 运行主循环
root.mainloop()
