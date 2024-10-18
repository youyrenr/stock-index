<template>
    <div class="login-container">
        <div class="login-card">
            <h2>欢迎光临</h2>
            <form @submit.prevent="login">
                <div class="input-group">
                    <input class="input" v-model="username" type="text" placeholder="用户名" required>
                </div>
                <div class="input-group">
                    <input class="input" v-model="password" type="password" placeholder="密码" required>
                </div>
                <button type="submit" :disabled="isLoading">
                    <span v-if="!isLoading">登录</span>
                    <span v-else class="loading-spinner"></span>
                </button>
            </form>
            <p v-if="error" class="error">{{ error }}</p>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'

export default {
    setup() {
        const authStore = useAuthStore()
        const username = ref('')
        const password = ref('')
        const error = ref('')
        const isLoading = ref(false)

        const login = async () => {
            error.value = ''
            isLoading.value = true
            try {
                await authStore.login(username.value, password.value)
            } catch (err) {
                error.value = 'Login failed. Please check your credentials.'
            } finally {
                isLoading.value = false
            }
        }

        return { username, password, login, error, isLoading }
    }
}
</script>
<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f0f4f8;
    font-family: 'Roboto', sans-serif;
}

.login-card {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

h2 {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 1.5rem;
}

.input-group {
    margin-bottom: 1rem;
    position: relative;
}

input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
}

input:focus {
    outline: none;
    border-color: #3498db;
}

button {
    width: 100%;
    padding: 0.75rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
    box-sizing: border-box;
}

button:hover:not(:disabled) {
    background-color: #2980b9;
}

button:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
}

.error {
    color: #e74c3c;
    text-align: center;
    margin-top: 1rem;
}

.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 480px) {
    .login-card {
        padding: 1.5rem;
    }
}
</style>