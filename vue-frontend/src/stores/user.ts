import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const username = ref<string | null>(localStorage.getItem('username'))
  const isLoggedIn = ref<boolean>(!!username.value)

  function login(name: string) {
    username.value = name
    isLoggedIn.value = true
    localStorage.setItem('username', name)
  }

  function logout() {
    username.value = null
    isLoggedIn.value = false
    localStorage.removeItem('username')
  }

  return { username, isLoggedIn, login, logout }
}) 