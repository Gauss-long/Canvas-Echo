<template>
  <div class="modal-backdrop">
    <div class="modal">
      <div class="modal-header">
        <h3>登录账号</h3>
        <!-- 移除关闭按钮 -->
      </div>
      
      <div class="modal-body">
        <p>请输入用户名和密码登录，体验设计评审服务</p>
        
        <div class="form-group">
          <label>用户名</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="请输入用户名"
          >
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input 
            type="password" 
            v-model="password" 
            placeholder="请输入密码"
          >
        </div>
        
        <button class="login-btn" @click="handleLogin">
          登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['close', 'login'])

const username = ref('')
const password = ref('')

const handleLogin = async () => {
  if (!username.value.trim() || !password.value) {
    alert('请输入用户名和密码')
    return
  }
  try {
    const res = await fetch('/db/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    const data = await res.json()
    if (data.success) {
      emit('login', username.value, data.user_id)
      emit('close')
    } else {
      alert(data.message || '用户名或密码错误')
    }
  } catch (e) {
    console.error(e)
    alert('登录请求失败，请稍后重试')
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.modal-header button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.code-input {
  display: flex;
  gap: 10px;
}

.code-input input {
  flex: 1;
}

.code-input button {
  background: #f0f4ff;
  border: none;
  border-radius: 8px;
  padding: 0 15px;
  color: #4a6cf7;
  cursor: pointer;
  white-space: nowrap;
}

.code-input button:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.login-btn {
  width: 100%;
  background: #4a6cf7;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 10px;
}
</style>