import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from .db import get_db
from .models import User, Session, Message
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("账号管理系统")
        self.resize(800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 标题
        title_label = QLabel("用户账号管理")
        title_label.setStyleSheet("font-size: 24 font-weight: bold; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # 用户列表表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["ID", "用户名", "注册时间", "会话数量"])
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setStyleSheet("""
            QTableWidget[object Object] {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section[object Object] {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        self.layout.addWidget(self.user_table)

        # 操作按钮区域
        button_layout = QHBoxLayout()

        self.add_user_btn = QPushButton("添加用户")
        self.add_user_btn.setStyleSheet("""
            QPushButton[object Object] {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover[object Object] {
                background-color: #45a049;
            }
        """)
        self.add_user_btn.clicked.connect(self.register_user)

        self.del_user_btn = QPushButton("删除用户")
        self.del_user_btn.setStyleSheet("""
            QPushButton[object Object] {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover[object Object] {
                background-color: #da190b;
            }
        """)
        self.del_user_btn.clicked.connect(self.delete_selected_user)

        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.setStyleSheet("""
            QPushButton[object Object] {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover[object Object] {
                background-color: #1976D2;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_all_users)

        button_layout.addWidget(self.add_user_btn)
        button_layout.addWidget(self.del_user_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()  # 添加弹性空间

        self.layout.addLayout(button_layout)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; padding: 10px;")
        self.layout.addWidget(self.status_label)

        # 加载用户数据
        self.load_all_users()

    def load_all_users(self):
        """加载所有用户"""
        try:
            db = next(get_db())
            users = db.query(User).all()

            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                # 获取用户的会话数量
                session_count = db.query(Session).filter(Session.user_id == user.id).count()

                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.username))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.created_at.strftime("%Y-%m-%d %H:%M:%S")))
                self.user_table.setItem(row, 3, QTableWidgetItem(str(session_count)))

            self.user_table.clearSelection()
            self.status_label.setText(f"已加载 {len(users)} 个用户")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载用户数据失败: {str(e)}")
            self.status_label.setText("加载失败")

    def register_user(self):
        """用户"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加新用户")
        dialog.setFixedSize(400, 200)
        layout = QFormLayout(dialog)

        username_edit = QLineEdit()
        username_edit.setPlaceholderText("请输入用户名")
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("请输入密码")
        password_edit.setEchoMode(QLineEdit.Password)
        confirm_password_edit = QLineEdit()
        confirm_password_edit.setPlaceholderText("请确认密码")
        confirm_password_edit.setEchoMode(QLineEdit.Password)

        layout.addRow("用户名:", username_edit)
        layout.addRow("密码:", password_edit)
        layout.addRow("确认密码:", confirm_password_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            username = username_edit.text().strip()
            password = password_edit.text().strip()
            confirm_password = confirm_password_edit.text().strip()

            # 验证输入
            if not username or not password:
                QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
                return

            if password != confirm_password:
                QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
                return

            if len(password) < 6:
                QMessageBox.warning(self, "输入错误", "密码长度不能少于6位")
                return

            try:
                db = next(get_db())
                # 检查用户名是否已存在
                existing_user = db.query(User).filter(User.username == username).first()
                if existing_user:
                    QMessageBox.warning(self, "注册失败", "用户名已存在")
                    return

                # 创建新用户
                hashed_password = get_password_hash(password)
                new_user = User(username=username, password_hash=hashed_password)
                db.add(new_user)
                db.commit()
                db.refresh(new_user)

                QMessageBox.information(self, "成功", f"用户 '{username}' 创建成功")
                self.load_all_users()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建用户失败: {str(e)}")

    def delete_selected_user(self):
        """删除选中的用户"""
        selected = self.user_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "删除用户", "请先选择一个用户")
            return

        user_id = int(self.user_table.item(selected[0].row(), 0).text())
        username = self.user_table.item(selected[0].row(), 1).text()
        session_count = int(self.user_table.item(selected[0].row(), 3).text())

        # 确认删除
        message = f"确定要删除用户 '{username}' 吗？\n\n"
        message += f"用户ID: {user_id}\n"
        message += f"会话数量: {session_count}\n\n"
        message += "删除后，该用户的所有会话和消息也将被永久删除！"
        reply = QMessageBox.question(
            self,
            "确认删除",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # 默认选择"否"
        )

        if reply == QMessageBox.Yes:
            try:
                db = next(get_db())
                user = db.query(User).filter(User.id == user_id).first()

                if not user:
                    QMessageBox.critical(self, "错误", f"未找到用户 ID 为 {user_id} 的用户")
                    return

                # 删除用户的所有会话（消息会通过级联删除自动删除）
                sessions = db.query(Session).filter(Session.user_id == user_id).all()
                session_count = len(sessions)

                for session in sessions:
                    db.delete(session)

                # 删除用户
                db.delete(user)
                db.commit()

                QMessageBox.information(
                    self,
                    "删除成功",
                    f"已删除用户 '{username}'\n"
                    f"同时删除了 {session_count} 个会话及其所有消息"
                )

                self.load_all_users()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除用户失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # 使用现代风格

    window = AdminApp()
    window.show()

    sys.exit(app.exec_()) 