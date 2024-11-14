import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import LoginView from '../LoginView.vue'
import KeyValueView from '../views/KeyValueView.vue'
import PromptView from '../views/PromptView.vue'
import StrategyView from '../views/StrategyView.vue'
import HomeView from '../views/HomeView.vue'
import OtherView from '../views/OtherView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: LoginView
        },
        {
            path: '/',
            component: () => import('../MainLayout.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    name: 'home',
                    component: HomeView
                },
                {
                    path: 'key-value',
                    name: 'keyValue',
                    component: KeyValueView
                },
                {
                    path: 'prompt',
                    name: 'Prompt',
                    component: PromptView
                },
                {
                    path: 'strategy',
                    name: 'Strategy',
                    component: StrategyView
                },
                {
                    path: 'other',
                    name: 'other',
                    component: OtherView
                }
            ]
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