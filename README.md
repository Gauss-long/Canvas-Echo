# Canvas Echo 聊天应用

一个基于 FastAPI + Vue3 的智能聊天应用，支持用户注册登录、会话管理和AI对话功能。

## 目录结构

```
web-project/
├── database/                    # 数据库相关文件
│   ├── app.db                  # SQLite数据库文件
│   ├── app_gui.py              # 数据库GUI应用
│   ├── crud.py                 # 数据库操作函数
│   ├── db.py                   # 数据库连接配置
│   ├── models.py               # 数据库模型定义
│   └── schemas.py              # Pydantic数据模型
├── langserve-api/              # FastAPI后端
│   ├── chain_wrapper/          # AI模型包装器
│   │   ├── chat.py            # 基础聊天功能
│   │   ├── chat_reason.py     # 推理聊天功能
│   │   ├── tagging.py         # 文本分类功能
│   │   └── tagging_pure.py    # 纯文本分类
│   ├── main.py                # FastAPI主入口
│   └── requirements.txt       # 后端依赖
├── vue-frontend/              # Vue3前端
│   ├── src/                   # 源码目录
│   │   ├── components/        # Vue组件
│   │   ├── views/            # 页面视图
│   │   ├── stores/           # Pinia状态管理
│   │   └── router/           # 路由配置
│   ├── package.json          # 前端依赖
│   ├── vite.config.ts        # Vite配置
│   └── ...
└── README.md                 # 项目说明
```

## 功能特性

- 🔐 用户注册登录系统
- 💬 智能AI对话功能
- 📝 会话管理和历史记录
- 🎨 现代化Vue3界面
- 🔄 实时流式响应
- 📱 响应式设计

## 启动方式

### 1. 启动后端
```bash
cd langserve-api
uvicorn main:app --reload
```
后端服务端口：8000

### 2. 启动前端
```bash
cd vue-frontend
npm install
npm run dev
```
前端服务端口：3000

### 3. 访问应用
浏览器打开 [http://localhost:3000](http://localhost:3000)

## API接口

### 认证接口
- `POST /db/login` - 用户登录

### 聊天接口
- `POST /api/chat` - 基础聊天功能
- `POST /api/chat_reason` - 推理聊天功能

## 技术栈

### 后端
- FastAPI - 现代Python Web框架
- SQLAlchemy - ORM数据库操作
- SQLite - 轻量级数据库
- LangServe - AI模型服务

### 前端
- Vue 3 - 渐进式JavaScript框架
- Vite - 快速构建工具
- Pinia - 状态管理
- Vue Router - 路由管理

## 数据库

项目使用SQLite数据库，包含以下表结构：
- `users` - 用户信息表
- `sessions` - 会话表
- `messages` - 消息记录表

## 开发说明

- 前后端分离架构
- 支持热重载开发
- 统一的数据库管理
- 完整的用户认证系统 