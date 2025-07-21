<template>
  <!-- 原模板代码保持不变 -->
  <div class="design-review-container">
    <!-- 遮罩层，未登录时显示，禁止主界面交互 -->
    <div v-if="showLoginModal" class="modal-mask"></div>
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <!-- 新增一个容器来包裹开启新对话和返回按钮 -->
      <div class="button-group">
        <button class="new-chat-btn" @click="startNewChat">
          <span>开启新对话</span>
        </button>
        <!-- 添加返回按钮 -->
        <button class="back-btn" @click="goBack">返回</button>
      </div>
      <div class="auth-section">
        <button v-if="!userStore.isLoggedIn" class="login-btn" @click="showLoginModal = true">
          <span> 登录</span>
        </button>
        <div v-else class="user-info">
          <span>{{ userAbbr }}</span>
          <button @click="logout">注销</button>
        </div>
      </div>
    </header>

    <!-- 侧边栏显示切换按钮 -->
    <button class="toggle-sidebar-btn" @click="toggleSidebar">
      <span>{{ isSidebarOpen ? '<' : '>' }}</span>
    </button>

    <div class="main-content">
      <!-- 侧边栏 - 历史对话 -->
      <aside class="history-sidebar" :style="{ display: isSidebarOpen ? 'block' : 'none' }">
        <div class="sidebar-header">
          <h3>历史对话</h3>
        </div>
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
            <!-- 修改删除按钮文字 -->
            <button @click.stop="deleteSession(session.id)" class="delete-btn">删除</button> 
          </li>
        </ul>
      </aside>

      <!-- 主对话区域 -->
      <div class="chat-container">
        <div class="messages" ref="messagesContainer">
          <div 
            v-for="(msg, index) in currentSession.messages" 
            :key="index" 
            class="message"
            :class="msg.role"
          >
            <div class="avatar">
              {{ msg.role === 'user' ? '👤' : '🤖' }}
            </div>
            
            <div class="content">
              <div v-if="msg.role === 'user' && msg.image">
                <img :src="msg.image" alt="上传的设计稿" class="design-image">
              </div>
              <div v-html="msg.content"></div>
              
              <!-- 模型回复操作区 -->
              <!-- 删除 assistant 消息下的重新生成按钮 -->
              <!--
              <div v-if="msg.role === 'assistant'" class="message-actions">
                <button @click="regenerateResponse(index)" class="action-btn">
                  🔄 重新生成
                </button>
                <div class="rating">
                  <span 
                    v-for="star in 5" 
                    :key="star" 
                    @click="rateResponse(index, star)"
                    :class="{ active: (msg.rating||0 )>= star }"
                  >
                    ⭐
                  </span>
                </div>
              </div>
              -->
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="image-upload">
            <input 
              type="file" 
              accept="image/*" 
              ref="fileInput"
              @change="handleImageUpload"
              style="display: none"
            >
            <button @click="triggerFileInput" class="upload-btn">
               上传图片
            </button>
            <span v-if="uploadedImage" class="file-name">
              {{ uploadedImage.name }}
            </span>
          </div>
          
          <textarea 
            v-model="userInput" 
            placeholder="输入您的设计问题或上传设计稿..."
            @keyup.enter="sendMessage"
          ></textarea>
          
          <button @click="sendMessage" class="send-btn">
            发送
          </button>
        </div>
      </div>
    </div>

    <!-- 登录模态框 -->
    <LoginModal 
      v-if="showLoginModal" 
      @login="handleLogin"
    />
  </div>
</template>

<script setup lang="ts">
  // 原有的script部分代码保持不变
  import { ref, computed, onMounted, nextTick } from 'vue'
  import LoginModal from '@/components/LoginModal.vue'
  import { useRouter } from 'vue-router' // 引入路由实例
  import { useUserStore } from '@/stores/user'

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
  }

  // 响应式数据
  const userInput = ref('')
  const uploadedImage = ref<File | null>(null)
  const messagesContainer = ref<HTMLElement | null>(null)
  const fileInput = ref<HTMLInputElement | null>(null)
  const showLoginModal = ref(false)
  const isLoggedIn = ref(false)
  const phoneNumber = ref('')

  // 聊天会话数据
  const historySessions = ref<Session[]>([])
  const currentSessionId = ref<number>(0)
  const currentSession = ref<Session>({
    id: 0,
    user_id: 0,
    title: '新对话',
    created_at: new Date(),
    messages: []
  })

  // 新增：侧边栏显示状态
  const isSidebarOpen = ref(true)

  const userAbbr = computed(() => {
    if (!userStore.username) return ''
    const name = userStore.username as string
    if (/^[\u4e00-\u9fa5]+$/.test(name)) {
      return name.slice(0, 2).toUpperCase()
    } else {
      return name.split(/\s+/).map(s => s[0]).join('').toUpperCase()
    }
  })

  const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = (error) => reject(error)
    reader.readAsDataURL(file)
  })
}


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

  // 新增：从数据库加载历史对话
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
    
    // 创建新会话
    const newSession = await createSession("新会话");
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
  }


  // 新增：创建数据库会话
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
          messages: data.messages // 如果 messages 是 JSON 数组，也要确保结构正确
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
        messages: []
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
    imageUrl = await fileToBase64(uploadedImage.value)
  }

  const max_id = await fetch('/db/get_max_message_id')
  const data = await max_id.json()
  const max_id_value = data.max_id

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
  const aiContent = await getAIResponse(inputText)
  const aiMsg = {
    id: max_id_value + 2,
    session_id: currentSession.value.id,
    content: aiContent,
    role: 'assistant',
    image: '', // 如有AI图片可补充
    timestamp: new Date()
  }
  addMessage(aiMsg)

  // 5. 写入数据库
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
      if (!data.success) {
        console.error('写入数据库失败:', data.message)
      }
    } catch (error) {
      console.error('写入数据库请求失败:', error)
    }
  }
}

  // 新增：获取AI回复的函数
  const getAIResponse = async (userMessage: string) => {
    let aiText = ''
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userMessage, session_id: currentSession.value.id }) // 修复：加上 session_id
      })
      const reader = response.body?.getReader()
      if (reader) {
        let decoder = new TextDecoder('utf-8')
        let done = false
        while (!done) {
          const { value, done: doneReading } = await reader.read()
          done = doneReading
          if (value) {
            aiText += decoder.decode(value, { stream: true })
          }
        }
      } else {
        aiText = await response.text()
      }
    } catch (e) {
      aiText = '请求失败，请稍后重试'
    }
    return aiText
  }


  const loadSession = (sessionId: number) => {
    const session = historySessions.value.find(s => s.id === sessionId)
    if (!session) {
      console.error('加载会话失败:', sessionId)
      return
    }
    currentSessionId.value = sessionId
    currentSession.value   = { ...session }
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
</script>

<style scoped>
  /* 原有的样式部分代码保持不变 */
  .design-review-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #f5f7fa;
  }

  .app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
  }

  .button-group {
    display: flex;
    align-items: center;
    gap: 15px; /* 设置按钮之间的间隔 */
  }

  .new-chat-btn, .login-btn ,.back-btn{
    background: #1f2023;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 10px 16px;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 15px;
  }

  .main-content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .history-sidebar {
    width: 250px;
    background-color: white;
    border-right: 1px solid #eaeaea;
    padding: 20px;
    overflow-y: auto;
  }

  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  .sidebar-header h3 {
    margin: 0;
    color: #333;
    font-size: 18px; 
    letter-spacing: 1px; 
    padding-left: 40px; 
    font-weight: 700; 

  }

  .toggle-sidebar-btn {
    background: #1f2023;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 8px 16px;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    position: absolute;
    left: 10px;
    top: 80px;
    z-index: 11;
  }

  .history-sidebar ul {
    list-style: none;
    padding: 0;
  }


  .history-sidebar li {
    padding: 10px 15px; 
    margin-bottom: 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex; /* 使用弹性布局 */
    justify-content: space-between; /* 将子元素分散对齐 */
    align-items: center; /* 垂直居中对齐 */
  }

  .history-sidebar li:hover {
    background-color: #f0f4ff;
  }

  .history-sidebar li.active {
    background-color: #e0e8ff;
    font-weight: 500;
  }

  .date {
    display: block;
    font-size: 0.8em;
    color: #888;
    margin-top: 4px;
  }

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
    background-color: #e0e8ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }

  .message.user .avatar {
    background-color: #d1e7ff;
  }

  .content {
    background: white;
    padding: 15px;
    border-radius: 18px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    max-width: 80%;
  }

  .message.user .content {
    background: #e0e8ff;
    border-bottom-right-radius: 5px;
  }

  .message.assistant .content {
    border-bottom-left-radius: 5px;
  }

  .design-image {
    max-width: 100%;
    max-height: 300px;
    border-radius: 10px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .message-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #eee;
  }

  .action-btn {
    background: none;
    border: none;
    color: #1f2023;
    cursor: pointer;
    font-size: 0.9em;
    padding: 5px;
  }

  .rating {
    display: flex;
    gap: 3px;
  }

  .rating span {
    cursor: pointer;
    color: #ddd;
    font-size: 1.1em;
  }

  .rating span.active {
    color: #ffc107;
  }

  .input-area {
    padding: 15px;
    background: white;
    border-top: 1px solid #eaeaea;
    display: flex;
    gap: 10px;
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
    color: white; 
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
    color: white;
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
    padding: 5px;
    margin-left: 10px;
  }

  .design-feedback, .design-analysis {
    line-height: 1.6;
  }

  .feedback-section, .analysis-section {
    margin: 15px 0;
    padding-bottom: 15px;
    border-bottom: 1px solid #f0f0f0;
  }

  .feedback-section:last-child, .analysis-section:last-child {
    border-bottom: none;
  }

  .modal-mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.4);
    z-index: 999;
  }
</style>