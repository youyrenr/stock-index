<template>
    <div class="key-value-manager">
        <div class="key-list" :class="{ 'collapsed': isCollapsed }">
            <button @click="toggleCollapse" class="collapse-btn">
                {{ isCollapsed ? '❯' : '❮' }}
            </button>
            <KeyList @select-key="selectKey" @key-added="handleKeyAdded" @key-deleted="handleKeyDeleted"
                v-show="!isCollapsed" />
        </div>
        <div class="value-viewer" v-if="selectedValue">
            <ValueViewer v-if="userType == 1" :value="selectedValue" :currentKey="selectedKey"
                @content-saved="handleContentSaved" />
            <ValueViewerView v-else :value="selectedValue" />
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import KeyList from './KeyList.vue'
import ValueViewerView from './ValueViewerView.vue'
import ValueViewer from './ValueViewer.vue'
import api from '../services/api'

export default {
    components: { KeyList, ValueViewerView, ValueViewer },
    setup() {
        const selectedValue = ref('')
        const selectedKey = ref('')
        const isCollapsed = ref(false)

        const selectKey = async (key) => {
            selectedKey.value = key
            try {
                const response = await api.get('/key-values', { params: { key } })
                selectedValue.value = typeof response.data.value === 'string'
                    ? response.data.value
                    : JSON.stringify(response.data.value, null, 2)
            } catch (error) {
                console.error('Failed to fetch value', error)
                selectedValue.value = 'Error loading value'
            }
        }

        const toggleCollapse = () => {
            isCollapsed.value = !isCollapsed.value
        }

        const handleContentSaved = (newContent) => {
            selectedValue.value = newContent
            // 可以在这里添加一些用户反馈，比如显示一个"保存成功"的提示
        }

        const handleKeyAdded = (newKey) => {
            selectKey(newKey)
        }

        const handleKeyDeleted = (deletedKey) => {
            if (selectedKey.value === deletedKey) {
                selectedKey.value = ''
                selectedValue.value = ''
            }
        }

        return {
            selectedValue,
            selectedKey,
            selectKey,
            isCollapsed,
            toggleCollapse,
            handleContentSaved,
            handleKeyAdded,
            handleKeyDeleted
        }
    },
    data() {
        return {
            userType: localStorage.user_type
        }
    }
}
</script>

<style scoped>
.key-value-manager {
    display: flex;
    height: 100vh;
    background-color: #f0f4f8;
    color: #2c3e50;
    font-family: 'Roboto', sans-serif;
}

.key-list {
    flex: 0 0 30%;
    max-width: 300px;
    transition: all 0.3s ease;
    background-color: #ffffff;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    position: relative;
    border-radius: 0 10px 10px 0;
}

.key-list.collapsed {
    flex: 0 0 60px;
}

.collapse-btn {
    position: absolute;
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 18px;
    cursor: pointer;
    z-index: 10;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.collapse-btn:hover {
    background-color: #2980b9;
}

.value-viewer {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    background-color: #ffffff;
    border-radius: 10px;
    margin: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
    .key-value-manager {
        flex-direction: column;
    }

    .key-list {
        flex: none;
        max-width: 100%;
        height: auto;
        border-radius: 0 0 10px 10px;
    }

    .key-list.collapsed {
        height: 60px;
    }

    .value-viewer {
        flex: 1;
        margin: 10px;
    }

    .collapse-btn {
        top: 100%;
        right: 50%;
        transform: translate(50%, -50%) rotate(90deg);
    }
}

.value-viewer {
    overflow: hidden;
}
</style>