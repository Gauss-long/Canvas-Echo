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
            v-for="(session, index) in historySessions" 
            :key="index"
            @click="loadSession(session.id)"
            :class="{ active: currentSessionId === session.id }"
          >
            <div class="session-info">
              {{ session.title || `对话 ${index + 1}` }}
              <span class="date">{{ formatDate(session.date) }}</span>
            </div>
            <!-- 修改删除按钮文字 -->
            <button @click.stop="deleteSession(index)" class="delete-btn">删除</button> 
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
    role: 'user' | 'assistant'
    content: string
    image?: string
    rating?: number
  }

  interface ChatSession {
    id: string
    title: string
    date: Date
    messages: Message[]
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
  const historySessions = ref<ChatSession[]>([])
  const currentSessionId = ref('')
  const currentSession = ref<ChatSession>({
    id: 'session-' + Date.now(),
    title: '新对话',
    date: new Date(),
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

  // 初始化
  onMounted(() => {
    // 从本地存储加载历史对话
    const savedSessions = localStorage.getItem('designReviewSessions')
    if (savedSessions) {
      historySessions.value = JSON.parse(savedSessions)
      // 对历史对话按日期降序排序（最近的在前面）
      historySessions.value.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    }
    
    // 检查登录状态
    const savedLogin = localStorage.getItem('designReviewLogin')
    if (savedLogin) {
      const { phone, loggedIn } = JSON.parse(savedLogin)
      isLoggedIn.value = loggedIn
      phoneNumber.value = phone
    }
    
    // 创建新会话
    startNewChat()

    if (!userStore.isLoggedIn) {
      showLoginModal.value = true
    }
  })

  // 删除对话方法
  const deleteSession = (index: number) => {
    // 使用 confirm 方法弹出确认对话框
    const isConfirmed = confirm('你确定要删除这个对话吗？');
    if (isConfirmed) {
      historySessions.value.splice(index, 1);
      saveSessions();
      
      // 如果删除的是当前会话，开始新对话
      if (currentSessionId.value === historySessions.value[index]?.id) {
        startNewChat();
      }
    }
  };

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

  const sendMessage = async () => {
    if (!userInput.value.trim() && !uploadedImage.value) return
    let imageUrl = null
    if (uploadedImage.value) {
      // 生成图片的base64用于发送
      const reader = new FileReader()
      imageUrl = await new Promise<string>((resolve) => {
        reader.onload = (e) => {
          resolve(e.target?.result as string)
        }
        reader.readAsDataURL(uploadedImage.value as File)
      })
    }
    // 添加用户消息，包含文字和图片
    addMessage({
      role: 'user',
      content: userInput.value,
      ...(imageUrl ? { image: imageUrl } : {})
    })
    // 如果是新对话的第一条消息，设置对话标题
    if (currentSession.value.messages.length === 1) {
      const keywords = userInput.value.trim().split(' ')[0].slice(0, 20);
      currentSession.value.title = keywords;
      saveSessions();
    }
    // 清空输入和图片
    const inputText = userInput.value
    userInput.value = ''
    uploadedImage.value = null
    // 模拟AI响应
    simulateAIResponse(inputText)
    // 如果有图片，也可以在这里调用 analyzeDesign(imageUrl)
    // if (imageUrl) {
    //   analyzeDesign(imageUrl)
    // }
  }

  const simulateAIResponse = async (userMessage: string) => {
    addMessage({
      role: 'assistant',
      content: '<div class="loading">分析中...</div>'
    })

    try {
      const response = await fetch('http://localhost:3000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: userMessage })
      })
      // 处理流式响应
      const reader = response.body?.getReader()
      let aiText = ''
      if (reader) {
        let decoder = new TextDecoder('utf-8')
        let done = false
        while (!done) {
          const { value, done: doneReading } = await reader.read()
          done = doneReading
          if (value) {
            aiText += decoder.decode(value, { stream: true })
            // 实时更新内容
            currentSession.value.messages[currentSession.value.messages.length - 1].content = aiText
          }
        }
      } else {
        aiText = await response.text()
        currentSession.value.messages[currentSession.value.messages.length - 1].content = aiText
      }
    } catch (e) {
      currentSession.value.messages.pop()
      addMessage({
        role: 'assistant',
        content: '请求失败，请稍后重试'
      })
    }
  }

  const generateDesignFeedback = (userMessage: string) => {
    // 这里生成设计评审反馈 - 实际应用中应调用API
    return `
      <div class="design-feedback">
        <h3>设计评审反馈</h3>
        <p>基于您上传的设计稿和描述"${userMessage}"，以下是我的专业分析：</p>
        
        <div class="feedback-section">
          <h4>布局分析：</h4>
          <p>整体布局合理，视觉层次清晰。建议在顶部导航区域增加10px的内边距以提升可读性。</p>
        </div>
        
        <div class="feedback-section">
          <h4>色彩搭配：</h4>
          <p>主色调协调，但对比度可进一步提升。建议将按钮颜色从 #4CAF50 调整为 #388E3C 以增强可访问性。</p>
        </div>
        
        <div class="feedback-section">
          <h4>可用性建议：</h4>
          <p>表单字段标签应更明显，考虑增加字体重量或使用更深的灰色（#555）。</p>
        </div>
        
        <div class="feedback-section">
          <h4>一致性检查：</h4>
          <p>图标风格统一，但按钮圆角半径存在不一致（4px vs 6px）。</p>
        </div>
      </div>
    `
  }

  // analyzeDesign 也改为请求后端（如需图片分析可自定义接口）
  const analyzeDesign = async (imageUrl: string) => {
    addMessage({
      role: 'assistant',
      content: '<div class="loading">正在分析设计稿...</div>'
    })
    try {
      const response = await fetch('http://localhost:3000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: '图片分析:' + imageUrl })
      })
      const reader = response.body?.getReader()
      let aiText = ''
      if (reader) {
        let decoder = new TextDecoder('utf-8')
        let done = false
        while (!done) {
          const { value, done: doneReading } = await reader.read()
          done = doneReading
          if (value) {
            aiText += decoder.decode(value, { stream: true })
            currentSession.value.messages[currentSession.value.messages.length - 1].content = aiText
          }
        }
      } else {
        aiText = await response.text()
        currentSession.value.messages[currentSession.value.messages.length - 1].content = aiText
      }
    } catch (e) {
      currentSession.value.messages.pop()
      addMessage({
        role: 'assistant',
        content: '图片分析请求失败，请稍后重试'
      })
    }
  }

  const startNewChat = () => {
    // 保存当前会话
    if (currentSession.value.messages.length > 0) {
      historySessions.value.push({...currentSession.value})
      // 对历史对话按日期降序排序（最近的在前面）
      historySessions.value.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    }
    
    // 创建新会话
    currentSessionId.value = 'session-' + Date.now()
    currentSession.value = {
      id: currentSessionId.value,
      title: '新对话',
      date: new Date(),
      messages: []
    }
    
    uploadedImage.value = null
    saveSessions()

    // 添加默认开头消息
    addMessage({
      role: 'assistant',
      content: '您好！请问您有什么设计需求?'
    })
  }

  const loadSession = (sessionId: string) => {
    const session = historySessions.value.find(s => s.id === sessionId)
    if (session) {
      currentSessionId.value = sessionId
      currentSession.value = {...session}
    }
  }

  const regenerateResponse = (index: number) => {
    // 移除原回复
    currentSession.value.messages.splice(index, 1)
    
    // 获取前一条用户消息
    const userMessage = currentSession.value.messages[index - 1].content
    
    // 重新生成
    simulateAIResponse(userMessage)
  }

  const rateResponse = (index: number, stars: number) => {
    currentSession.value.messages[index].rating = stars
    saveSessions()
  }

  function handleLogin(username: string) {
    userStore.login(username)
    showLoginModal.value = false
  }

  function logout() {
    userStore.logout()
    showLoginModal.value = true
  }

  const saveSessions = () => {
    // 保存到本地存储
    localStorage.setItem('designReviewSessions', JSON.stringify([
      ...historySessions.value,
      {...currentSession.value}
    ]))
    
    // 如果已登录，同步到云端
    if (userStore.isLoggedIn) {
      syncToCloud()
    }
  }

  const syncToCloud = () => {
    // 实际应用中应调用API同步数据
    console.log('同步数据到云端...')
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