<template>
    <div class="key-list">
        <div class="header">
            <h2>列表</h2>
            <button @click="logout" class="logout-btn">退出</button>
        </div>
        <div class="search-container">
            <input v-model="search" placeholder="搜索">
            <span class="search-icon">🔍</span>
        </div>
        <ul class="key-items">
            <li v-for="key in filteredKeys" :key="key">
                <span @click="$emit('select-key', key)">{{ key }}</span>
                <button class="delete-btn" @click="confirmDelete(key)">🗑️</button>
            </li>
        </ul>
        <div class="add-key-container">
            <input v-model="newKey" placeholder="输入键名" class="add-input">
            <button @click="addNewKey" :disabled="!newKey.trim()" class="add-button">新增</button>
        </div>

        <!-- 确认删除对话框 -->
        <div v-if="showConfirmDialog" class="confirm-dialog">
            <p>确定要删除 "{{ keyToDelete }}" 吗？</p>
            <button @click="deleteKey">确定</button>
            <button @click="cancelDelete">取消</button>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

export default {
    emits: ['select-key', 'key-added', 'key-deleted'],
    setup(props, { emit }) {
        const keys = ref([])
        const search = ref('')
        const newKey = ref('')
        const showConfirmDialog = ref(false)
        const keyToDelete = ref('')

        const fetchKeys = async () => {
            try {
                const response = await api.post('/key-values/keys', { skip: 0, limit: 100 })
                keys.value = response.data.map(item => item.key)
            } catch (error) {
                console.error('Failed to fetch keys', error)
            }
        }

        onMounted(fetchKeys)

        const filteredKeys = computed(() => {
            return keys.value.filter(key => key.toLowerCase().includes(search.value.toLowerCase()))
        })

        const addNewKey = async () => {
            if (newKey.value.trim()) {
                try {
                    await api.post('/key-values', { key: newKey.value, value: '' })
                    keys.value.push(newKey.value)
                    emit('key-added', newKey.value)
                    newKey.value = ''
                } catch (error) {
                    console.error('Failed to add new key', error)
                }
            }
        }

        const confirmDelete = (key) => {
            keyToDelete.value = key
            showConfirmDialog.value = true
        }

        const deleteKey = async () => {
            try {
                await api.delete('/key-values', { data: { key: keyToDelete.value } })
                keys.value = keys.value.filter(k => k !== keyToDelete.value)
                emit('key-deleted', keyToDelete.value)
                showConfirmDialog.value = false
            } catch (error) {
                console.error('Failed to delete key', error)
            }
        }

        const cancelDelete = () => {
            showConfirmDialog.value = false
            keyToDelete.value = ''
        }

        const logout = () => {
            localStorage.clear()
            window.location.reload()
        }

        return {
            keys,
            search,
            filteredKeys,
            newKey,
            addNewKey,
            showConfirmDialog,
            keyToDelete,
            confirmDelete,
            deleteKey,
            cancelDelete,
            logout
        }
    }
}
</script>

<style scoped>
.key-list {
    box-sizing: border-box;
    position: relative;
    padding: 20px;
    background-color: #ffffff;
    height: 100vh;
    display: flex;
    flex-direction: column;
    max-width: 600px;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.header h2 {
    margin: 0;
    color: #2c3e50;
}

.search-container {
    position: relative;
    margin-bottom: 20px;
}

input {
    box-sizing: border-box;
    width: 100%;
    padding: 10px 15px;
    padding-right: 40px;
    border: 1px solid #e0e6ed;
    border-radius: 5px;
    font-size: 14px;
    transition: all 0.3s ease;
}

input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.search-icon {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: #7f8c8d;
}

button {
    padding: 10px 15px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

button:hover {
    background-color: #2980b9;
}

button:disabled {
    background-color: #bdc3c7;
    cursor: not-allowed;
}

.logout-btn {
    background-color: #e74c3c;
}

.logout-btn:hover {
    background-color: #c0392b;
}

.key-items {
    list-style-type: none;
    padding: 0;
    flex-grow: 1;
    overflow-y: auto;
    margin: 0;
}

.key-items li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    border-radius: 5px;
    transition: all 0.2s ease;
    margin-bottom: 5px;
}

.key-items li:hover {
    background-color: #f0f4f8;
}

.key-items li span {
    cursor: pointer;
    flex-grow: 1;
}

.key-items li span:hover {
    color: #3498db;
}

.delete-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.2em;
    padding: 0 5px;
    color: #e74c3c;
}

.delete-btn:hover {
    color: #c0392b;
}

.add-key-container {
    display: flex;
    margin-top: 20px;
}

.add-input {
    flex-grow: 1;
    margin-right: 10px;
}

.confirm-dialog {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: white;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.confirm-dialog button {
    margin-right: 10px;
}
</style>