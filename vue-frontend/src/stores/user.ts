import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const username = ref<string | null>(localStorage.getItem('username'))
  const userId = ref<number | null>(localStorage.getItem('userId') ? parseInt(localStorage.getItem('userId')!) : null)
  const isLoggedIn = ref<boolean>(!!username.value)

  function login(name: string, id: number) {
    username.value = name
    userId.value = id
    isLoggedIn.value = true
    localStorage.setItem('username', name)
    localStorage.setItem('userId', id.toString())
  }

  function logout() {
    username.value = null
    userId.value = null
    isLoggedIn.value = false
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
  }

  return { username, userId, isLoggedIn, login, logout }
}) 