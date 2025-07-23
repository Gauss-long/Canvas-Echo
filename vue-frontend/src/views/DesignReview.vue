<template>
  <!-- 顶层容器 -->
  <div class="design-review-container">
    <!-- 遮罩层（未登录时禁用交互） -->
    <div v-if="showLoginModal" class="modal-mask"></div>

    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="button-group">
        <!-- 顶部只保留返回 -->
        <button class="back-btn" @click="goBack">
          ‹ 返回
        </button>
      </div>
      <div class="auth-section">
        <button
          v-if="!userStore.isLoggedIn"
          class="login-btn"
          @click="showLoginModal = true"
        >
          <span> 登录</span>
        </button>
        <div v-else class="user-info">
          <span>{{ userAbbr }}</span>
          <button @click="logout">注销</button>
        </div>
      </div>
    </header>

    <!-- ============ 主体区域：左侧按钮列 + 旧 main-content ============ -->
    <div class="content-wrapper">
      <!-- 左侧细长按钮面板：永远显示 -->
      <aside class="toggle-column">
    <button class="toggle-sidebar-btn" @click="toggleSidebar">
          <!-- isSidebarOpen 为真 ⇒ 显示左箭头 ‹；否则显示右箭头 › -->
          <span>{{ isSidebarOpen ? '‹' : '›' }}</span>
    </button>
      </aside>

      <!-- 原 main-content（包含历史侧栏 / 聊天 / 展示区） -->
    <div class="main-content">
        <!-- 历史对话侧边栏 -->
        <aside
          class="history-sidebar"
          :style="{ display: isSidebarOpen ? 'block' : 'none' }"
        >
        <div class="sidebar-header">
          <h3>历史对话</h3>
            
        </div>
          <button class="new-chat-sidebar-btn" @click="startNewChat">
            ＋ 新对话
          </button>

        <ul>
            <li
              v-for="session in historySessions"
              :key="session.id"
              @click="loadSession(session.id)"
              :class="{ active: currentSessionId === session.id }"
            >
            <div class="session-info">
              {{ session.title }}
              <span class="date">{{ formatDate(session.created_at) }}</span>
            </div>
              <button
                @click.stop="deleteSession(session.id)"
                class="delete-btn"
              >
                删除
              </button>
          </li>
        </ul>
          
      </aside>

        <!-- 主聊天区域 -->
      <div class="chat-container">
        <div class="messages" ref="messagesContainer">
          <template v-for="(msg, index) in currentSession.messages" :key="index">
            <div class="message" :class="msg.role">
              <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            
            <div class="content">
              <div v-if="msg.role === 'user' && msg.image">
                  <img :src="msg.image" alt="上传的设计稿" class="design-image" />
              </div>
                <template v-if="msg.role === 'assistant' && isHtmlMessage(msg)">
                  <iframe :srcdoc="normalizeHtml(msg.content)"
                          :key="currentVersionIndex + '-' + index"
                          sandbox="allow-scripts allow-same-origin"
                          style="width:200px;height:140px;border:none;border-radius:8px;"></iframe>
                </template>
                <template v-else>
                  <div class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
                </template>
                <button
                  v-if="shouldShowGenerateBtn(index)"
                  @click="startGenerate"
                  class="start-generate-btn"
                >
                  开始生成
                </button>

                </div>
              </div>
          </template>
        </div>

          <!-- 输入区 -->
        <div class="input-area">
          <div class="image-upload">
            <input 
              type="file" 
              accept="image/*" 
              ref="fileInput"
              @change="handleImageUpload"
              style="display: none"
              />
            <button @click="triggerFileInput" class="upload-btn">
               上传图片
            </button>
              <span v-if="uploadedImage" class="file-name">{{
                uploadedImage.name
              }}</span>
          </div>
          
          <textarea 
            v-model="userInput" 
            placeholder="输入您的设计问题或上传设计稿..."
            @keyup.enter="sendMessage"
          ></textarea>
          
            <button @click="sendMessage" class="send-btn">发送</button>
          </div>
        </div>

        <!-- 展示区 -->
        <aside class="display-panel" v-show="isShowPanel">
          <!-- 展示区顶部按钮区 -->
          <div class="display-panel-header">
            <div class="tab-group">
              <button :class="{ active: displayMode === 'render' }" @click="displayMode = 'render'">
                <i class="fa-regular fa-circle-play"></i> 预览
              </button>
              <button :class="{ active: displayMode === 'code' }" @click="displayMode = 'code'">
                <strong style="font-weight: 700;">&lt;/&gt;</strong> 代码
          </button>
        </div>

            <div class="action-group">
              <button @click="copyCode">
                <i class="fa-regular fa-paste"></i> 复制
              </button>
              <button @click="downloadHtml">
                <i class="fa-solid fa-floppy-disk"></i> 下载
              </button>
            </div>
          </div>
          <!-- 展示区内容区 -->
          <div class="display-panel-content">
            <div v-if="copyTip" class="copy-toast-center">已复制到剪贴板</div>
            <div v-if="displayMode === 'render'" class="render-box">
              <iframe
                :srcdoc="normalizeHtml(htmlContent)"
                :key="currentVersionIndex"
                sandbox="allow-scripts allow-same-origin"
                style="width:100%;height:630px;border:none;border-radius:8px;overflow:auto;background:#fafbfc;"
              ></iframe>
            </div>
            <div v-else class="code-box">
              <pre><code ref="codeBoxRef" class="html">{{ normalizeHtml(htmlContent) }}</code></pre>
            </div>
          </div>
          <!-- 展示区底部版本管理区 -->
          <div class="display-panel-version">
            <div class="version-list">
              <button
                v-for="(ver, idx) in versionHtmlList"
                :key="idx"
                :class="{ active: idx === currentVersionIndex }"
                @click="selectVersion(idx)"
              >{{ 'v' + (idx + 1) }}</button>
            </div>
          </div>
          <button class="toggle-panel-btn-inside" @click="togglePanel">×</button>
        </aside>

        <!-- 展示区收起后的小按钮 -->
        <div class="display-panel-placeholder" v-show="!isShowPanel">
          <button class="toggle-panel-btn-inside" @click="togglePanel">‹</button>
        </div>
      </div>
    </div>

    <!-- 登录模态框 -->
    <LoginModal v-if="showLoginModal" @login="handleLogin" />
  </div>
  <div style="position:fixed;left:-9999px;top:-9999px;z-index:-1;width:400px;pointer-events:none;" ref="hiddenRenderRef">
    <div v-html="htmlContent"></div>
  </div>
</template>


<style scoped>
/* ======= 布局整体 ======= */
.design-review-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

/* ===== 顶部导航 ===== */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 10px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.back-btn,
.login-btn {
  background: #1f2023;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 1px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info button {
  background: #1f2023;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 1px;
}

.user-info span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #1976d2;
  color: #fff;
  border-radius: 50%;
  font-weight: bold;
  font-size: 1.1em;
  margin-right: 8px;
}

/* ===== 主体：左侧按钮列 + main-content ===== */
.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧细长列 */
.toggle-column {
  width: 30px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
}

/* 左侧列按钮 */
.toggle-sidebar-btn {
  background: transparent;
  border: none;
  color: #000;
  cursor: pointer;
  font-size: 2rem;
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 原 main-content ===== */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 历史对话侧边栏 */
.history-sidebar {
  width: 200px;
  background: white;
  border-right: 1px solid #eaeaea;
  padding: 7px;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

/* 对话列表项 */
.history-sidebar ul {
  list-style: none;
  padding: 0;
}

.history-sidebar li,
.new-chat-sidebar-btn {
  width: 100%;
  padding: 10px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border: none;
  font: inherit;
  text-align: left;
}

.history-sidebar li:hover,
.new-chat-sidebar-btn:hover {
  background: #f0f4ff;
}

.history-sidebar li.active {
  background: #e0e8ff;
  font-weight: 500;
}

.new-chat-sidebar-btn {
  border: 1px dashed #bbb;
  color: #1f2023;
  gap: 6px;
  justify-content: center;
}

/* 日期 */
.date {
  display: block;
  font-size: 0.8em;
  color: #888;
}

/* 聊天主区域 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 90%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e8ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message.user .avatar {
  background: #d1e7ff;
}

.content {
  background: #fff;
  padding: 15px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  max-width: 80%;
}

.message.user .content {
  background: #e0e8ff;
}

.design-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 10px;
  margin: 10px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 输入区 */
.input-area {
  padding: 15px;
  background: #fff;
  border-top: 1px solid #eaeaea;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.image-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-btn {
  background: #0f0404;
  border: none;
  border-radius: 18px;
  padding: 8px 15px;
  cursor: pointer;
  color: #fff;
  white-space: nowrap;
}

.file-name {
  font-size: 0.8em;
  color: #666;
  margin-top: 5px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

textarea {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 18px;
  padding: 12px 15px;
  resize: none;
  height: 50px;
  font-family: inherit;
}

.send-btn {
  background: #1f2023;
  color: #fff;
  border: none;
  border-radius: 18px;
  padding: 0 20px;
  cursor: pointer;
  font-weight: 500;
  align-self: flex-end;
}

.delete-btn {
  background: none;
  border: none;
  color: #0f0404;
  cursor: pointer;
  font-size: 0.9em;
}

/* 展示区 */
.display-panel {
  position: relative;
  width: 700px;
  background: #fff;
  border-left: 1px solid #eaeaea;
  padding: 20px;
  box-sizing: border-box;
  transition: width 0.2s;
  overflow-y: auto;
}

.display-panel[style*='display: none'] {
  width: 0 !important;
  padding: 0 !important;
  border: none !important;
}

.toggle-panel-btn-inside {
  position: absolute;
  top: 10px;
  right: 10px;
  background: transparent;
  border: none;
  width: 36px;
  height: 36px;
  font-size: 2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.display-panel-placeholder {
  position: relative;
  width: 0;
  background: transparent;
  border-left: 1px solid transparent;
}

.display-panel-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.tab-group, .action-group {
  display: flex;
  align-items: center;
}
.tab-group button, .action-group button {
  margin-right: 8px;
  padding: 6px 16px;
  border: none;
  background: #eee;
  border-radius: 6px 6px 0 0;
  font-weight: 500;
  font-size: 1em;
  display: flex;
  align-items: center;
}
.tab-group button.active {
  background: #1f2023;
  color: #fff;
}
.action-group {
  margin-left: 0;
}
.display-panel-content {
  width: 100%;
  min-height: 630px;
  background: #fafbfc;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 12px;
  overflow: auto;
  position: relative; /* Added for positioning toast */
}

.render-box {
  min-height: 180px;
}
.code-box pre {
  background:transparent;
  border-radius: 8px;
  font-family: Consolas, 'Fira Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.8em;
  overflow-x: auto;
}
.display-panel-version {
  margin-top: 10px;
  overflow-x: auto;
}
.version-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}
.version-list button {
  padding: 4px 16px;
  border: none;
  background: #eee;
  border-radius: 16px;
  cursor: pointer;
  white-space: nowrap;
}
.version-list button.active {
  background: #1f2023;
  color: #fff;
}

/* 遮罩 */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
}

.copy-tip {
  color: #d3e8fe;
  margin-left: 8px;
  font-size: 0.95em;
}

.copy-toast-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  z-index: 100;
  background: #c0dbf6;
  color: #ffffff;
  padding: 14px 32px;
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(25, 118, 210, 0.15);
  font-size: 1.08em;
  opacity: 0.95;
  animation: fadeInOut 1.5s;
  pointer-events: none;
}
@keyframes fadeInOut {
  0% { opacity: 0; transform: translate(-50%, -60%);}
  10% { opacity: 0.95; transform: translate(-50%, -50%);}
  90% { opacity: 0.95; transform: translate(-50%, -50%);}
  100% { opacity: 0; transform: translate(-50%, -60%);}
}
.markdown-body {
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  line-height: 1.7;
  color: #222;
  background: none;
  padding: 0;
}
.markdown-body h1, .markdown-body h2 { border-bottom: 1px solid #eee; }
.markdown-body code { background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }
</style>


<script setup lang="ts">
  // 原有的script部分代码保持不变
  import { ref, computed, onMounted, nextTick, watch } from 'vue'
  import LoginModal from '@/components/LoginModal.vue'
  import { useRouter } from 'vue-router' // 引入路由实例
  import { useUserStore } from '@/stores/user'
  // @ts-ignore
  import hljs from 'highlight.js'
  import 'highlight.js/styles/atom-one-light.css' // 更花哨的高亮主题
  // @ts-ignore
  import { toPng } from 'html-to-image'
  // 顶部引入 marked
  import { marked } from 'marked'

  const GREETING = '您好！请问您有什么设计需求?'
  const router = useRouter() // 获取路由实例
  const userStore = useUserStore()

  // 类型定义
  interface Message {
    id: number  // 支持字符串（前端临时）和数字（数据库ID）
    session_id: number
    content: string
    image: string
    role: string
    timestamp: Date
  }

  interface Session {
    id:number
    user_id:number
    title:string
    created_at:Date
    messages:Message[]
    hasStartedGenerate?: boolean
  }

  // 响应式数据
  const userInput = ref('')
  const uploadedImage = ref<File | null>(null)
  const messagesContainer = ref<HTMLElement | null>(null)
  const fileInput = ref<HTMLInputElement | null>(null)
  const showLoginModal = ref(false)
  const isLoggedIn = ref(false)
  const phoneNumber = ref('')
  const isDownloading = ref(false)   // 防止并发点击


  // 聊天会话数据
  const historySessions = ref<Session[]>([])
  const currentSessionId = ref<number>(0)
  const currentSession = ref<Session>({
    id: 0,
    user_id: 0,
    title: '新对话',
    created_at: new Date(),
    messages: [],
    hasStartedGenerate: false
  })

  // 新增：侧边栏显示状态
  const isSidebarOpen = ref(true)
  const isShowPanel = ref(false) // 控制展示区显示/隐藏
  const togglePanel = () => {
    isShowPanel.value = !isShowPanel.value
  }

  const userAbbr = computed(() => {
    if (!userStore.username) return ''
    const name = userStore.username as string
    if (/^[\u4e00-\u9fa5]+$/.test(name)) {
      return name.slice(0, 2).toUpperCase()
    } else {
      return name.split(/\s+/).map(s => s[0]).join('').toUpperCase()
    }
  })

  const fileToDataURL = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // 这里就是形如 "data:image/png;base64,AAAA..." 的完整 Data-URI
      resolve(reader.result as string);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};



  // 初始化
  onMounted(async () => {
    // 清空本地历史会话缓存和账号信息，保证每次都需重新登录
    localStorage.removeItem('designReviewSessions')
    localStorage.removeItem('designReviewLogin')
    
    // 检查登录状态
    const savedLogin = localStorage.getItem('designReviewLogin')
    if (savedLogin) {
      const { phone, loggedIn } = JSON.parse(savedLogin)
      isLoggedIn.value = loggedIn
      phoneNumber.value = phone
    }
    
    // 如果已登录，从数据库加载历史对话
    if (userStore.isLoggedIn && userStore.username) {
      await loadHistoryFromDatabase()
      await nextTick()  
      if (historySessions.value.length) {
        currentSession.value   = historySessions.value[0]   // 最新一条
        currentSessionId.value = historySessions.value[0].id
      }
    }

    if (!userStore.isLoggedIn) {
      showLoginModal.value = true
    }
  })

  // 1. 修正 loadHistoryFromDatabase
  const loadHistoryFromDatabase = async () => {
  try {
    const res  = await fetch(`/db/history?username=${userStore.username}`)
    const data = await res.json()
    if (data.success && data.sessions) {
      historySessions.value = data.sessions
        .map((session: any): Session => ({
          id: session.id,
          user_id: session.user_id,
          title: session.title,
          created_at: new Date(session.created_at),
          hasStartedGenerate: !!session.is_started, // 同步 is_started
          messages: session.messages.map((msg: any) => ({
            id: msg.id,
            session_id: msg.session_id,
            content: msg.content,
            image: msg.image,
            role: msg.role,
            timestamp: new Date(msg.timestamp)
          }))
        }))
        // 🔽 参数加上类型
        .sort(
          (a: Session, b: Session) =>
            b.created_at.getTime() - a.created_at.getTime()
        )
    }
  } catch (err) {
    console.error('加载历史对话失败:', err)
  }
}

  
  const addMessage = (message: Message) => {
    currentSession.value.messages.push(message)
    saveSessions()
    
    // 滚动到底部
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  }


  const startNewChat = async () => {
    // 保存当前会话
    if (currentSession.value.messages.length) {
      historySessions.value = [
        // 深拷贝，避免后续修改影响历史记录
        { ...currentSession.value, messages: [...currentSession.value.messages] },
        // 过滤掉相同 id，防止重复
          ...historySessions.value.filter(s => s.id !== currentSession.value.id)
      ]
    }
    
    // 创建新对话
    const newSession = await createSession("新对话");
    if (newSession) {
      historySessions.value.unshift(newSession) // 放在列表顶部
      currentSessionId.value = newSession.id
      currentSession.value   = newSession
    }else {
      console.error('创建新会话失败')
    }
    
    uploadedImage.value = null
    saveSessions()

    // 添加默认开头消息
    addMessage({
      id: 0,
      session_id: currentSessionId.value,
      content: '您好！请问您有什么设计需求?',
      role: 'assistant',
      image: '',
      timestamp: new Date()
    })

    try {
      const response = await fetch('/db/create_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId.value,
          content: '您好！请问您有什么设计需求?',
          role: 'assistant',
          image: ''
        })
      })
      const data = await response.json()
      if (!data.success) {
        console.error('写入数据库失败:', data.message)
      }
    } catch (error) {
      console.error('写入数据库请求失败:', error)
    }
    updateDisplayPanelVersions(currentSessionId.value)
  }


  // 2. 修正 createSession，确保 hasStartedGenerate 从后端 is_started 字段同步
  const createSession = async (title: string): Promise<Session | null> => {
    if (!userStore.isLoggedIn || !userStore.userId) {
      return null
    }
    
    try {
      const response = await fetch('/db/create_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.userId,
          title: title
        })
      })
      const data = await response.json()
      if (data.success) {
        const session: Session = {
          id: data.session_id,
          user_id: data.user_id,
          title: data.title,
          created_at: new Date(data.created_at), // 👈 注意要转成 Date 对象
          messages: data.messages, // 如果 messages 是 JSON 数组，也要确保结构正确
          hasStartedGenerate: !!data.is_started // 同步 is_started
        }
        return session
      }
    } catch (error) {
      console.error('创建会话失败:', error)
    }
    return null
  }

  const saveSessions = () => {
    // 保存到本地存储
    localStorage.setItem(
      'designReviewSessions',
      JSON.stringify(historySessions.value)
    )
}


 const deleteSession = async (sessionId: number) => {
   if (!confirm('你确定要删除这个对话吗？')) return

   const isCurrent = currentSessionId.value === sessionId
   try {
     const res = await fetch('/db/delete_session', {
       method: 'DELETE',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ session_id: sessionId })
     })
    const data = await res.json()
     if (!data.success) throw new Error(data.message)

    // 删除后再更新历史列表
     historySessions.value = historySessions.value.filter(s => s.id !== sessionId)

    if (isCurrent) {
      uploadedImage.value = null
      currentSessionId.value = 0
      currentSession.value = {
        id: 0,
        user_id: userStore.userId ?? 0,
        title: '新对话',
        created_at: new Date(),
        messages: [],
        hasStartedGenerate: false
      }
      await nextTick()
      await startNewChat()
    }

    saveSessions()
   } catch (err) {
     console.error('删除会话失败:', err)
   }
 }


  // 新增：切换侧边栏显示状态的方法
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  // 计算属性
  const hasMessages = computed(() => currentSession.value.messages.length > 0)

  // 方法
  const triggerFileInput = () => {
    if (fileInput.value) {
      fileInput.value.click()
    }
  }

  const handleImageUpload = (event: Event) => {
    const input = event.target as HTMLInputElement
    if (input.files && input.files[0]) {
      uploadedImage.value = input.files[0]
      // 只保存图片，不自动发送消息和分析
      // 可选：可在页面上显示图片预览
      const reader = new FileReader()
      reader.onload = (e) => {
        // 可将图片预览地址保存到一个变量用于展示
        // imagePreviewUrl.value = e.target?.result as string
      }
      reader.readAsDataURL(uploadedImage.value)
    }
  }



  const sendMessage = async () => {
  if (!userInput.value.trim() && !uploadedImage.value) return

  // 1. 生成图片 base64
  let imageUrl = null
  if (uploadedImage.value) {
    imageUrl = await fileToDataURL(uploadedImage.value)
  }

  const max_id = await fetch('/db/get_max_message_id')
  const data = await max_id.json()
  const max_id_value = data.max_id
  //1.5 生成标题
  if(currentSession.value.title === '新对话'){
    const title = await fetch('/api/title', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: userInput.value })
    })
    const titleData = await title.json()
    currentSession.value.title = titleData.title
    // 同步到历史会话
    const idx = historySessions.value.findIndex(s => s.id === currentSession.value.id)
    if (idx !== -1) {
      historySessions.value[idx].title = titleData.title
    }
    await fetch('/db/update_session_title', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: currentSession.value.id, title: titleData.title })
    })
    saveSessions()
    await nextTick()
  }
  // 2. 本地插入用户消息
  const userMsg = {
    id: max_id_value + 1,
    session_id: currentSession.value.id,
    content: userInput.value,
    role: 'user',
    image: imageUrl || '',
    timestamp: new Date()
  }
  addMessage(userMsg)

  // 3. 清空输入
  const inputText = userInput.value
  userInput.value = ''
  uploadedImage.value = null

  // 4. 获取AI回复
  const flag = currentSession.value.hasStartedGenerate ? 1 : 0
  const aiContent = await getAIResponse(inputText, flag, imageUrl)
  const aiMsg: Message = {
    id: max_id_value + 2,
    session_id: currentSession.value.id,
    content: aiContent,
    role: 'assistant',
    image: '', // 如有AI图片可补充
    timestamp: new Date()
  }
  addMessage(aiMsg)
  let writeSuccess = false
  if (userStore.isLoggedIn && typeof currentSession.value.id === 'number') {
    try {
      const response = await fetch('/db/create_message_pair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id1: currentSession.value.id,
          content1: userMsg.content,
          role1: userMsg.role,
          image1: userMsg.image,
          session_id2: currentSession.value.id,
          content2: aiMsg.content,
          role2: aiMsg.role,
          image2: aiMsg.image
        })
      })
      const data = await response.json()
        writeSuccess = !!data.success
      if (!data.success) {
        console.error('写入数据库失败:', data.message)
      }
       
    } catch (error) {
      console.error('写入数据库请求失败:', error)
    }
  }
  // 只有数据库写入成功后再拉取版本
  if (writeSuccess) {
    await updateDisplayPanelVersions(currentSession.value.id)
  }
}

  // 新增：获取AI回复的函数
  const getAIResponse = async (userMessage: string, flag: number, img_url: string|null) => {
    let aiText = ''
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSession.value.id,
          flag,
          user_message: userMessage,
          img_url: img_url || ''
        })
      })
      const data = await response.json()
      aiText = data.message || ''
    } catch (e) {
      aiText = '请求失败，请稍后重试'
    }
    return aiText
  }


  // 3. 修正 loadSession，切换会话时同步 hasStartedGenerate 字段
  const loadSession = (sessionId: number) => {
    const session = historySessions.value.find(s => s.id === sessionId)
    if (!session) {
      console.error('加载会话失败:', sessionId)
      return
    }
    currentSessionId.value = sessionId
    // 保证 hasStartedGenerate 字段同步
    currentSession.value = { ...session, hasStartedGenerate: session.hasStartedGenerate }
    updateDisplayPanelVersions(sessionId)

    nextTick(() => {
      highlightCode()
    })
  }



  function handleLogin(username: string, userId: number) {
    userStore.login(username, userId)
    showLoginModal.value = false
    loadHistoryAfterLogin()
  }
  const loadHistoryAfterLogin = async () => {
    await loadHistoryFromDatabase()
    await nextTick()
    if (historySessions.value.length) {
      currentSession.value   = historySessions.value[0]
      currentSessionId.value = historySessions.value[0].id
    }
  }

  
  function logout() {
    userStore.logout()
    showLoginModal.value = true
    // 注销时清空本地历史会话缓存和账号信息
    localStorage.removeItem('designReviewSessions')
    localStorage.removeItem('designReviewLogin')
  }



  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 添加返回方法
  const goBack = () => {
    router.push({ name: 'home' })
  }

  const displayMode = ref<'render' | 'code'>('render')
  // 1. 修改 versionHtmlList 类型为 string[]
  const versionHtmlList = ref<string[]>([])
  const currentVersionIndex = ref(0)
  

  // 2. updateDisplayPanelVersions 直接赋值字符串数组
  async function updateDisplayPanelVersions(sessionId: number) {
    const res = await fetch(`/db/get_all_versions?session_id=${sessionId}`)
    const data = await res.json()
    if (data.success && Array.isArray(data.versions)) {
      versionHtmlList.value = data.versions // 直接是字符串数组
      //....................................
      console.log('[debug] versions length →', versionHtmlList.value.length)

      currentVersionIndex.value = versionHtmlList.value.length - 1
    } else {
      versionHtmlList.value = []
      currentVersionIndex.value = -1
    }
    displayMode.value = 'render'
    await nextTick()
  }

  function selectVersion(idx: number) {
    currentVersionIndex.value = idx
  }

  // 3. 版本按钮渲染
  // <button v-for="(ver, idx) in versionHtmlList" :key="idx" ... >
  // 4. htmlContent 计算属性
  const htmlContent = computed(() => {
    return versionHtmlList.value[currentVersionIndex.value] || ''
  })

  const codeBoxRef = ref<HTMLElement | null>(null)

  function highlightCode() {
  if (displayMode.value === 'code' && codeBoxRef.value) {
        hljs.highlightElement(codeBoxRef.value)
      }
  }

  const hiddenRenderRef = ref<HTMLElement | null>(null)

  const copyTip = ref(false)
  function copyCode() {
    navigator.clipboard.writeText(htmlContent.value).then(() => {
      copyTip.value = true
      setTimeout(() => { copyTip.value = false }, 1500)
    })
  }

  async function downloadHtml() {
  if (isDownloading.value) return
  isDownloading.value = true
  try {
    const html = htmlContent.value
    // 获取 session_title
    let title = currentSession.value.title || 'session'
    // 去除非法文件名字符，空格转下划线
    title = title.replace(/[\\/:*?"<>|]/g, '').replace(/\s+/g, '_')
    // 版本号
    const version = `v${currentVersionIndex.value + 1}`
    const filename = `${title}_${version}.html`
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error(err)
    alert('生成 HTML 文件失败，请稍后重试')
  } finally {
    isDownloading.value = false
  }
}

  onMounted(() => {
    highlightCode()
  })

  watch([htmlContent, displayMode, currentSessionId, currentVersionIndex], () => {
    setTimeout(() => {
      highlightCode()
    })
  })

  function shouldShowGenerateBtn(idx: number) {
    if (currentSession.value.hasStartedGenerate) return false

    const msgs = currentSession.value.messages

    // 收集所有「非问候语」的 assistant‑text 消息下标
    const assistantTextIdxs = msgs
      .map((m, i) =>
        (m.role === 'assistant' &&
        m.content.trim() !== GREETING) ? i : -1)
      .filter(i => i !== -1)

    if (!assistantTextIdxs.length) return false       // 目前还没有可点击的回复

    // 只有最新一条符合条件的 assistant‑text 才显示按钮
    return idx === assistantTextIdxs[assistantTextIdxs.length - 1]
  }



  // 6. “开始生成”按钮逻辑（全量替换）
const startGenerate = async () => {
  /* ---------- 1. 本地与后端都标记已进入生成阶段 ---------- */
  currentSession.value.hasStartedGenerate = true
  saveSessions()                       // 写入 localStorage

  // 持久化到数据库（后台实现：UPDATE sessions SET hasStartedGenerate = 1 WHERE id = ?）
  fetch('/db/mark_started', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: currentSession.value.id })
  }).catch(err => console.error('标记生成阶段失败:', err))


  /* ---------- 3. 请求 AI 生成 HTML ---------- */
  const aiContent = await getAIResponse(
    "",
    1,                   // flag=1 → 生成阶段
    null
  )

  /* ---------- 4. 立即把 HTML 消息插入本地 ---------- */
  const aiMsg: Message = {
    id: Date.now(),       // 前端临时 ID，后端会重新分配
    session_id: currentSession.value.id,
    content: aiContent,
    image: '',
    role: 'assistant',
    timestamp: new Date()
  }
  addMessage(aiMsg)
  let writeSuccess = false
  if (userStore.isLoggedIn && typeof currentSession.value.id === 'number') {
    try {
      const res = await fetch('/db/create_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSession.value.id,
          content: aiContent,
          role: 'assistant',
          image: '',
          type: 'html'            // 建议后端也存这个字段
        })
      })
      const data = await res.json()
      writeSuccess = !!data.success
      if (!data.success) {
        console.error('写入数据库失败:', data.message)
      }
    } catch (err) {
      console.error('写入数据库请求失败:', err)
    }
  }
  // 只有数据库写入成功后再拉取版本
  if (writeSuccess) {
    await updateDisplayPanelVersions(currentSession.value.id)
  }
}

  // 1. 添加 isHtmlMessage 辅助函数
  function isHtmlMessage(msg: Message): boolean {
    return typeof msg.content === 'string' && /<html[\s\S]*<\/html>/i.test(msg.content)
  }

  // 渲染 markdown 的辅助函数
  function renderMarkdown(content: string) {
    // 只对非 HTML 消息做 markdown 渲染
    if (isHtmlMessage({ content, id: 0, session_id: 0, image: '', role: '', timestamp: new Date() })) return content
    return marked.parse(normalizeHtml(content || ''))
  }

  // 新增：HTML代码去除多余转义换行符
  function normalizeHtml(html: string) {
    return html.replace(/\\n/g, '\n');
  }


</script>