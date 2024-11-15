import axios from 'axios'
import { useAuthStore } from '../store/auth'

const api = axios.create({
    // baseURL: 'http://localhost:8000/'
    baseURL: 'http://stock.api.bookagent.com.cn/'
})

api.interceptors.request.use(
    config => {
        const authStore = useAuthStore()
        if (authStore.token) {
            config.headers['Authorization'] = `Bearer ${authStore.token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            const authStore = useAuthStore()
            authStore.logout()
        }
        return Promise.reject(error)
    }
)

export default api