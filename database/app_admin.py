import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QSplitter, QListWidget,
    QTextEdit, QFileDialog, QAbstractItemView
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from .db import get_db
from .crud import get_user_by_username, get_user_sessions, get_session_messages, delete_session, create_user
from .models import User
from . import schemas
import base64

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("应用后台管理（PyQt版）")
        self.resize(1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # 左侧：用户列表
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["ID", "用户名", "注册时间"])
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setMinimumWidth(300)
        self.user_table.itemSelectionChanged.connect(self.on_user_selected)

        # 用户操作按钮
        self.add_user_btn = QPushButton("注册用户")
        self.del_user_btn = QPushButton("删除用户")
        self.add_user_btn.clicked.connect(self.register_user)
        self.del_user_btn.clicked.connect(self.delete_selected_user)
        user_btn_layout = QHBoxLayout()
        user_btn_layout.addWidget(self.add_user_btn)
        user_btn_layout.addWidget(self.del_user_btn)
        user_left_layout = QVBoxLayout()
        user_left_layout.addWidget(self.user_table)
        user_left_layout.addLayout(user_btn_layout)
        user_left_widget = QWidget()
        user_left_widget.setLayout(user_left_layout)

        # 中间：会话列表
        self.session_list = QListWidget()
        self.session_list.setMinimumWidth(250)
        self.session_list.itemSelectionChanged.connect(self.on_session_selected)
        self.session_label = QLabel("会话列表")
        session_layout = QVBoxLayout()
        session_layout.addWidget(self.session_label)
        session_layout.addWidget(self.session_list)
        session_widget = QWidget()
        session_widget.setLayout(session_layout)

        # 右侧：消息详情
        self.message_list = QListWidget()
        self.message_list.setMinimumWidth(400)
        self.message_list.itemSelectionChanged.connect(self.on_message_selected)
        self.message_label = QLabel("消息详情")
        self.message_content = QTextEdit()
        self.message_content.setReadOnly(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setVisible(False)
        msg_layout = QVBoxLayout()
        msg_layout.addWidget(self.message_label)
        msg_layout.addWidget(self.message_list)
        msg_layout.addWidget(self.message_content)
        msg_layout.addWidget(self.image_label)
        msg_widget = QWidget()
        msg_widget.setLayout(msg_layout)

        # 主分割区
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(user_left_widget)
        splitter.addWidget(session_widget)
        splitter.addWidget(msg_widget)
        self.layout.addWidget(splitter)

        # 数据状态
        self.selected_user_id = None
        self.selected_session_id = None
        self.selected_message_id = None

        self.load_all_users()

    def load_all_users(self):
        db = next(get_db())
        users = db.query(User).all()
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.created_at.strftime("%Y-%m-%d %H:%M:%S")))
        self.user_table.clearSelection()
        self.session_list.clear()
        self.message_list.clear()
        self.message_content.clear()
        self.image_label.clear()
        self.image_label.setVisible(False)
        self.selected_user_id = None
        self.selected_session_id = None
        self.selected_message_id = None

    def on_user_selected(self):
        selected = self.user_table.selectedItems()
        if not selected:
            self.session_list.clear()
            self.message_list.clear()
            self.message_content.clear()
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.selected_user_id = None
            return
        user_id = int(self.user_table.item(selected[0].row(), 0).text())
        self.selected_user_id = user_id
        self.load_sessions(user_id)

    def load_sessions(self, user_id):
        db = next(get_db())
        sessions = get_user_sessions(db, user_id)
        self.session_list.clear()
        for session in sessions:
            self.session_list.addItem(f"{session.id} | {session.title} | {session.created_at.strftime('%Y-%m-%d %H:%M')}")
        self.message_list.clear()
        self.message_content.clear()
        self.image_label.clear()
        self.image_label.setVisible(False)
        self.selected_session_id = None
        self.selected_message_id = None

    def on_session_selected(self):
        selected = self.session_list.currentItem()
        if not selected:
            self.message_list.clear()
            self.message_content.clear()
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.selected_session_id = None
            return
        session_id = int(selected.text().split("|")[0].strip())
        self.selected_session_id = session_id
        self.load_messages(session_id)

    def load_messages(self, session_id):
        db = next(get_db())
        messages = get_session_messages(db, session_id)
        self.message_list.clear()
        for msg in messages:
            label = f"{msg.id} | {msg.role} | {msg.timestamp.strftime('%H:%M:%S')}"
            self.message_list.addItem(label)
        self.message_content.clear()
        self.image_label.clear()
        self.image_label.setVisible(False)
        self.selected_message_id = None

    def on_message_selected(self):
        selected = self.message_list.currentItem()
        if not selected:
            self.message_content.clear()
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.selected_message_id = None
            return
        msg_id = int(selected.text().split("|")[0].strip())
        self.selected_message_id = msg_id
        self.show_message_detail(msg_id)

    def show_message_detail(self, msg_id):
        db = next(get_db())
        session_id = self.selected_session_id
        messages = get_session_messages(db, session_id)
        msg = next((m for m in messages if m.id == msg_id), None)
        if not msg:
            self.message_content.clear()
            self.image_label.clear()
            self.image_label.setVisible(False)
            return
        if msg.content_type == "image":
            # 解析base64图片
            if msg.content.startswith("[图片:") and msg.content.endswith("]"):
                parts = msg.content[4:-1].split(":", 1)
                if len(parts) == 2:
                    filename, encoded_string = parts
                    try:
                        image_data = base64.b64decode(encoded_string)
                        image = QImage.fromData(image_data)
                        pixmap = QPixmap.fromImage(image)
                        self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
                        self.image_label.setVisible(True)
                        self.message_content.setText(f"图片: {filename}")
                    except Exception as e:
                        self.image_label.clear()
                        self.image_label.setVisible(False)
                        self.message_content.setText("图片解析失败")
                else:
                    self.image_label.clear()
                    self.image_label.setVisible(False)
                    self.message_content.setText("图片格式错误")
            else:
                self.image_label.clear()
                self.image_label.setVisible(False)
                self.message_content.setText("图片内容格式不正确")
        else:
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.message_content.setText(msg.content)

    def register_user(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("注册用户")
        layout = QFormLayout(dialog)
        username_edit = QLineEdit()
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        layout.addRow("用户名:", username_edit)
        layout.addRow("密码:", password_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted:
            username = username_edit.text().strip()
            password = password_edit.text().strip()
            if not username or not password:
                QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
                return
            db = next(get_db())
            if get_user_by_username(db, username):
                QMessageBox.warning(self, "注册失败", "用户名已存在")
                return
            user_data = schemas.UserCreate(username=username, password=password)
            create_user(db, user_data)
            QMessageBox.information(self, "注册成功", "用户注册成功")
            self.load_all_users()

    def delete_selected_user(self):
        selected = self.user_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "删除用户", "请先选择一个用户")
            return
        user_id = int(self.user_table.item(selected[0].row(), 0).text())
        reply = QMessageBox.question(self, "确认删除", f"确定要删除用户ID {user_id} 吗？该用户所有会话和消息也会被删除。", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                sessions = get_user_sessions(db, user_id)
                for session in sessions:
                    session_id = getattr(session, 'id', None)
                    if session_id is not None and isinstance(session_id, int):
                        delete_session(db, session_id)
                db.delete(user)
                db.commit()
                QMessageBox.information(self, "成功", f"已删除用户 ID 为 {user_id} 的用户")
            else:
                QMessageBox.critical(self, "错误", f"未找到用户 ID 为 {user_id} 的用户")
            self.load_all_users()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminApp()
    window.show()
    sys.exit(app.exec_()) 