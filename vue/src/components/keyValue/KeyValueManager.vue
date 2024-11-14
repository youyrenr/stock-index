<template>
    <div class="key-value-manager">
        <div class="key-list" :class="{ 'is-collapsed': isCollapsed }">
            <button @click="toggleCollapse" class="collapse-btn">
                {{ isCollapsed ? '❯' : '❮' }}
            </button>
            <KeyList @select-key="selectKey" @key-added="handleKeyAdded" @key-deleted="handleKeyDeleted"
                v-show="!isCollapsed" />
        </div>
        <div class="value-viewer" v-if="selectedValue">
            <component :is="userType == 1 ? 'ValueViewer' : 'ValueViewerView'" :value="selectedValue"
                :currentKey="selectedKey" @content-saved="handleContentSaved" />
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import KeyList from './KeyList.vue'
import ValueViewerView from './ValueViewerView.vue'
import ValueViewer from './ValueViewer.vue'
import api from '../../services/api'

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

        const logout = () => {
            localStorage.clear()
            window.location.reload()
        }

        return {
            selectedValue,
            selectedKey,
            selectKey,
            isCollapsed,
            toggleCollapse,
            handleContentSaved,
            handleKeyAdded,
            handleKeyDeleted,
            logout
        }
    },
    data() {
        return {
            userType: localStorage.user_type
        }
    }
}
</script>

<style lang="scss" scoped>
$primary-color: #3498db;
$secondary-color: #2980b9;
$danger-color: #e74c3c;
$danger-hover-color: #c0392b;
$background-color: #f0f4f8;
$text-color: #2c3e50;
$border-color: rgba(0, 0, 0, 0.05);
$box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);

.key-value-manager {
    display: flex;
    height: 100vh;
    background-color: $background-color;
    color: $text-color;
    font-family: 'Roboto', sans-serif;
}

.key-list {
    flex: 0 0 30%;
    max-width: 300px;
    transition: all 0.3s ease;
    background-color: #fff;
    box-shadow: 10px 0 20px rgba(0, 0, 0, 0.05);
    position: relative;
    border-radius: 0 10px 10px 0;

    &.is-collapsed {
        flex: 0 0 0;
    }
}

.collapse-btn {
    position: absolute;
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
    background-color: $primary-color;
    color: #fff;
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

    &:hover {
        background-color: $secondary-color;
    }
}

.value-viewer {
    flex: 1;
    padding: 30px;
    overflow: hidden;
    background-color: #fff;
    border-radius: 10px;
    margin: 20px;
    box-shadow: $box-shadow;
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

        &.is-collapsed {
            height: 60px;
        }
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
</style>