import { defineStore } from 'pinia'
import api from '../services/api'
import router from '../router'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        user: null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
    },
    actions: {
        async login(username, password) {
            try {
                const response = await api.post('/auth/token', { username, password })
                this.token = response.data.access_token
                localStorage.setItem('token', this.token)
                localStorage.setItem('user_type', response.data.user_type)
                await this.fetchUser()
                router.push('/key-value')
            } catch (error) {
                console.error('Login failed', error)
                throw error
            }
        },
        async fetchUser() {
            try {
                const response = await api.get('/users/me')
                this.user = response.data
            } catch (error) {
                console.error('Failed to fetch user', error)
                throw error
            }
        },
        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            router.push('/login')
        },
    },
})