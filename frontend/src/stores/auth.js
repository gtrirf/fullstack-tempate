import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'
import { usersApi } from '@/api/users'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    registerEmail: null,
  }),

  getters: {
    isAuthenticated: (s) => !!s.access,
    isAdmin: (s) => ['admin', 'superadmin'].includes(s.user?.role),
    isGuest: (s) => s.user?.role === 'guest',
    isUser: (s) => s.user?.role === 'user',
  },

  actions: {
    _persist(data) {
      this.access = data.access
      this.refresh = data.refresh
      this.user = data.user
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
    },

    async login(email, password) {
      const { data } = await authApi.login(email, password)
      this._persist(data)
    },

    async logout() {
      try {
        if (this.refresh) await authApi.logout(this.refresh)
      } catch {}
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.clear()
    },

    async fetchMe() {
      const { data } = await usersApi.getMe()
      this.user = data
      localStorage.setItem('user', JSON.stringify(data))
    },

    setTokensFromRegister(data) {
      this._persist(data)
    },
  },
})
