import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import LoginView from '../views/LoginView.vue'
import KeyValueView from '../views/KeyValueView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: LoginView
        },
        {
            path: '/key-value',
            name: 'keyValue',
            component: KeyValueView,
            meta: { requiresAuth: true }
        },
        {
            path: '/',
            redirect: '/key-value'
        }
    ]
})

router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!authStore.isAuthenticated) {
            next({ name: 'login' })
        } else {
            if (!authStore.user) {
                try {
                    await authStore.fetchUser()
                } catch (error) {
                    authStore.logout()
                    next({ name: 'login' })
                    return
                }
            }
            next()
        }
    } else {
        if (authStore.isAuthenticated && to.name === 'login') {
            next({ name: 'keyValue' })
        } else {
            next()
        }
    }
})

export default router