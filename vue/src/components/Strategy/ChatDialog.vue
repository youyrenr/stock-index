<template>
    <div class="dialog-overlay" v-if="visible">
        <!--  @click.self="handleClose" -->
        <div class="dialog-content">
            <div class="dialog-header">
                <h3 class="dialog-title">调用</h3>
                <button class="close-btn" @click="handleClose">
                    <span class="close-icon">×</span>
                </button>
            </div>

            <div class="dialog-body">
                <div class="chat-container">
                    <div class="messages" ref="messagesContainer">
                        <div v-for="message in messages" :key="message.messageId" class="message-wrapper">
                            <div class="sender-tag" :class="[message.sender == 'User' ? 'user' : 'ai']">
                                {{ message.sender }}
                            </div>

                            <div :class="['message', message.sender == 'User' ? 'user' : 'ai']">
                                <!-- 编辑状态显示输入框 -->
                                <div v-if="editingMessage?.messageId === message.messageId" class="edit-mode">
                                    <textarea v-model="editingText" class="message-input"
                                        @keydown.enter.ctrl="updateMessage" rows="4"></textarea>
                                    <div class="edit-actions">
                                        <button class="action-btn save" @click="updateMessage">保存</button>
                                        <button class="action-btn cancel" @click="cancelEdit">取消</button>
                                    </div>
                                </div>
                                <!-- 正常状态显示内容 -->
                                <template v-else>
                                    <div class="message-content">
                                        <MdPreview :modelValue="message.text" previewTheme="github"
                                            class="md-preview" />
                                    </div>
                                    <div class="message-actions">
                                        <!-- v-if="message.sender === 'User'" -->
                                        <button class="action-btn edit" @click="startEdit(message)">
                                            编辑
                                        </button>
                                        <button class="action-btn delete" @click="deleteMessage(message)">
                                            删除
                                        </button>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </div>

                    <div class="input-area">
                        <textarea v-model="newMessage" class="message-input" placeholder="输入消息..."
                            @keydown.enter.ctrl="sendMessage" rows="4"></textarea>

                        <div class="controls-area">
                            <select v-model="selectedModel" class="model-select">
                                <option value="gpt-4o-mini">gpt-4o-mini</option>
                                <option value="gemini-1.5-pro-latest">gemini-1.5-pro-latest</option>
                            </select>

                            <button class="send-btn" @click="sendMessage" :disabled="!newMessage.trim() && loading">
                                添加
                            </button>
                            <button class="send-btn" @click="sendLLM" :disabled="loading">
                                调用
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, nextTick, onMounted } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import api from '../../services/api'

export default {
    components: {
        MdPreview
    },

    props: {
        visible: Boolean,
        strategy: Object
    },

    emits: ['close', 'update:strategy'],

    setup(props, { emit, expose }) {
        const messages = ref([])
        const newMessage = ref('')
        const messagesContainer = ref(null)
        const editingMessage = ref(null)
        const editingText = ref('')
        const shouldRenderContent = ref(false)
        const loading = ref(false)
        const selectedModel = ref('gpt-4o-mini')


        onMounted(async () => {
            await nextTick()
            shouldRenderContent.value = true
            await loadMessages()
        })

        const loadMessages = async () => {
            if (!props.strategy?.conversationId) {
                props.strategy.conversationId = 0
            }

            try {
                const response = await api.get(`/messages/${props.strategy.conversationId}`)
                messages.value = response.data
                scrollToBottom()
            } catch (error) {
                console.error('加载消息失败:', error)
            }
        }

        const createNewConversation = async (text) => {
            try {
                const response = await api.post('/messages', {
                    text,
                    sender: 'User',
                    isCreatedByUser: true
                })

                const updatedStrategy = {
                    ...props.strategy,
                    conversationId: response.data.conversationId
                }
                await api.put('/strategies', updatedStrategy)
                emit('update:strategy', updatedStrategy)

                return response.data
            } catch (error) {
                console.error('创建对话失败:', error)
                throw error
            }
        }

        const processTextReplacements = async (text) => {
            let processedText = text

            // 处理所有替换
            async function processAllReplacements() {
                // 处理 #{value} 替换
                processedText = processedText.replace(/#{value}/g, props.strategy.conversationId || '')

                // 处理 #{key=xxx} 替换
                const keyMatches = processedText.match(/#{key=(.*?)}/g)
                if (keyMatches) {
                    for (const match of keyMatches) {
                        const key = match.match(/#{key=(.*?)}/)[1]
                        try {
                            const response = await api.get('/key-values', { params: { key } })
                            const value = typeof response.data.value === 'string'
                                ? response.data.value
                                : JSON.stringify(response.data.value, null, 2)
                            processedText = processedText.replace(match, value)
                        } catch (error) {
                            console.error(`获取key=${key}的值失败:`, error)
                            processedText = processedText.replace(match, `[获取key=${key}失败]`)
                        }
                    }
                }

                // 处理 #{keychi=xxx} 替换
                const keychiMatches = processedText.match(/#{keychi=(.*?)}/g)
                if (keychiMatches) {
                    for (const match of keychiMatches) {
                        const key = match.match(/#{keychi=(.*?)}/)[1]
                        try {
                            const response = await api.get(`/key-values/concatenated-values`, { params: { key } })
                            const value = typeof response.data.value === 'string'
                                ? response.data.value
                                : JSON.stringify(response.data.value, null, 2)
                            processedText = processedText.replace(match, value)
                        } catch (error) {
                            console.error(`获取keychi=${key}的值失败:`, error)
                            processedText = processedText.replace(match, `[获取keychi=${key}失败]`)
                        }
                    }
                }

                // 处理 #{prompt=xxx} 替换
                const promptMatches = processedText.match(/#{prompt=(.*?)}/g)
                if (promptMatches) {
                    for (const match of promptMatches) {
                        const key = match.match(/#{prompt=(.*?)}/)[1]
                        try {
                            const response = await api.get('/prompts', { params: { key } })
                            const value = typeof response.data.value === 'string'
                                ? response.data.value
                                : JSON.stringify(response.data.value, null, 2)
                            processedText = processedText.replace(match, value)
                        } catch (error) {
                            console.error(`获取prompt=${key}的值失败:`, error)
                            processedText = processedText.replace(match, `[获取prompt=${key}失败]`)
                        }
                    }
                }

                return processedText
            }

            return await processAllReplacements()
        }

        const sendMessage = async () => {
            if (!newMessage.value.trim()) return

            try {
                // 处理所有替换
                const processedText = await processTextReplacements(newMessage.value)

                let messageData
                if (!props.strategy.conversationId) {
                    messageData = await createNewConversation(processedText)
                } else {
                    messageData = await api.post('/messages', {
                        conversationId: props.strategy.conversationId,
                        parentMessageId: messages.value[messages.value.length - 1]?.messageId,
                        text: processedText,
                        sender: 'User',
                        isCreatedByUser: true
                    })
                }

                messages.value.push(messageData.data)
                newMessage.value = ''
                scrollToBottom()
            } catch (error) {
                console.error('发送消息失败:', error)
            }
        }
        const sendLLM = async () => {
            if (loading.value) return

            try {
                loading.value = true

                if (!props.strategy.conversationId) {
                    return
                }

                const messageData = await api.post('/messages/regenerate', {
                    conversation_id: props.strategy.conversationId,
                    sender: selectedModel.value
                })

                messages.value.push(messageData.data)
                newMessage.value = ''
                scrollToBottom()
            } catch (error) {
                console.error('发送消息失败:', error)
                loadMessages()
            } finally {
                loading.value = false
            }
        }


        // 开始编辑消息
        const startEdit = (message) => {
            editingMessage.value = message
            editingText.value = message.text
        }

        // 取消编辑
        const cancelEdit = () => {
            editingMessage.value = null
            editingText.value = ''
        }

        // 更新消息
        const updateMessage = async () => {
            if (!editingMessage.value || !editingText.value.trim()) return

            try {
                const response = await api.put('/messages', {
                    messageId: editingMessage.value.messageId,
                    text: editingText.value,
                    conversationId: props.strategy.conversationId,
                })

                const index = messages.value.findIndex(m => m.messageId === editingMessage.value.messageId)
                if (index !== -1) {
                    messages.value[index] = {
                        ...messages.value[index],
                        text: editingText.value
                    }
                }

                cancelEdit()
            } catch (error) {
                console.error('更新消息失败:', error)
            }
        }

        // 删除消息
        const deleteMessage = async (message) => {
            try {
                await api.delete(`/messages/${message.messageId}`)

                const index = messages.value.findIndex(m => m.messageId === message.messageId)
                if (index !== -1) {
                    messages.value.splice(index, 1)
                }
            } catch (error) {
                console.error('删除消息失败:', error)
            }
        }

        const scrollToBottom = () => {
            setTimeout(() => {
                if (messagesContainer.value) {
                    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
                }
            }, 100)
        }

        const handleClose = () => {
            emit('close')
        }

        expose({
            loadMessages
        })

        return {
            messages,
            newMessage,
            messagesContainer,
            editingMessage,
            editingText,
            sendMessage,
            sendLLM,
            startEdit,
            cancelEdit,
            updateMessage,
            deleteMessage,
            handleClose,
            shouldRenderContent,
            loading,
            selectedModel
        }
    }
}
</script>



<style lang="scss" scoped>
@use "sass:color";

* {
    box-sizing: border-box;
}

// 变量定义
$primary-color: #2563eb;
$user-color: #f0f9ff;
$ai-color: #ffffff;
$border-color: #e2e8f0;
$text-primary: #1e293b;
$text-secondary: #64748b;
$radius-lg: 12px;
$radius-md: 8px;
$transition: all 0.3s ease;

// 混入
@mixin flex-center {
    display: flex;
    justify-content: center;
    align-items: center;
}

@mixin custom-scrollbar {
    &::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    &::-webkit-scrollbar-track {
        background: transparent;
    }

    &::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 3px;

        &:hover {
            background: rgba(0, 0, 0, 0.2);
        }
    }
}

// 对话框样式
.dialog-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.4);
    @include flex-center;
    z-index: 1000;
    backdrop-filter: blur(4px);
    animation: fadeIn 0.2s ease;
}

.dialog-content {
    background: white;
    border-radius: $radius-lg;
    width: 90%;
    height: 90%;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
        0 10px 10px -5px rgba(0, 0, 0, 0.04);
    animation: slideUp 0.3s ease;
}

.dialog-header {
    padding: 16px 24px;
    border-bottom: 1px solid $border-color;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dialog-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
}

.close-btn {
    @include flex-center;
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: $radius-md;
    cursor: pointer;
    transition: $transition;

    &:hover {
        background-color: $ai-color;

        .close-icon {
            color: $text-primary;
        }
    }
}

.close-icon {
    font-size: 1.5rem;
    color: $text-secondary;
    line-height: 1;
}

.dialog-body {
    flex: 1;
    overflow: hidden;
}

// 聊天容器样式
.chat-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 20px;
}

.messages {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    @include custom-scrollbar;
}

.message-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.sender-tag {
    font-size: 0.85rem;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
    width: fit-content;

    &.user {
        color: $primary-color;
        background: rgba($primary-color, 0.1);
    }

    &.ai {
        color: $text-secondary;
        background: rgba($text-secondary, 0.1);
    }
}

.message {
    max-width: 85%;
    animation: messageAppear 0.3s ease;

    &.user {
        .message-content {
            background-color: $user-color;
            border: 1px solid rgba($primary-color, 0.1);
        }
    }

    &.ai {
        .message-content {
            background-color: $ai-color;
            border: 1px solid rgba($primary-color, 0.1);
        }
    }
}

.message-content {
    padding: 16px;
    border-radius: $radius-md;
    font-size: 0.95rem;
    line-height: 1.5;

    :deep(.md-preview) {
        background: transparent;
        padding: 0;
        margin: 0;

        min-height: 0 !important;
        max-height: 500px !important;
        height: auto !important;

        .default-theme {
            padding: 0;
            margin: 0;
            min-height: 0 !important;
            height: auto !important;
        }

        p {
            margin: 0;
            line-height: 1.5;
            min-height: 0 !important;
        }

        .editor-container {
            min-height: 0 !important;
            height: auto !important;
        }
    }
}

.message-actions {
    display: flex;
    justify-content: flex-start;
    margin-top: 8px;
}

.edit-btn {
    padding: 4px 12px;
    font-size: 0.875rem;
    color: $text-secondary;
    background: transparent;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    cursor: pointer;
    transition: $transition;

    &:hover {
        background: $ai-color;
        color: $text-primary;
        border-color: $text-secondary;
    }
}

.input-area {
    margin-top: 24px;
    display: flex;
    gap: 12px;
}

.message-input {
    flex: 1;
    padding: 12px 16px;
    font-size: 0.95rem;
    line-height: 1.5;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    resize: none;
    transition: $transition;
    height: 160px; // 调整高度以适应右侧三个元素
    @include custom-scrollbar;

    &:focus {
        outline: none;
        border-color: $primary-color;
        box-shadow: 0 0 0 2px rgba($primary-color, 0.1);
    }

    &::placeholder {
        color: $text-secondary;
    }
}

// 右侧控制区样式
.controls-area {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 200px; // 设置固定宽度
}

.model-select {
    height: 40px;
    padding: 0 12px;
    font-size: 0.95rem;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    background-color: white;
    color: $text-primary;
    cursor: pointer;
    transition: $transition;
    width: 100%; // 占满容器宽度

    &:focus {
        outline: none;
        border-color: $primary-color;
        box-shadow: 0 0 0 2px rgba($primary-color, 0.1);
    }

    &:hover {
        border-color: $primary-color;
    }
}

.send-btn {
    height: 40px;
    padding: 0 24px;
    font-size: 0.95rem;
    font-weight: 500;
    color: white;
    background: $primary-color;
    border: none;
    border-radius: $radius-md;
    cursor: pointer;
    transition: $transition;
    width: 100%; // 占满容器宽度

    &:hover:not(:disabled) {
        background: color.scale($primary-color, $lightness: -9%);
    }

    &:disabled {
        background: rgba($primary-color, 0.5);
        cursor: not-allowed;
    }
}

// 动画
@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes messageAppear {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.edit-mode {
    width: 100%;

    .message-input {
        width: 100%;
        margin-bottom: 8px;
    }
}

.edit-actions {
    display: flex;
    gap: 8px;
}

.action-btn {
    padding: 4px 12px;
    font-size: 0.875rem;
    border-radius: $radius-md;
    cursor: pointer;
    transition: $transition;

    &.edit {
        color: $text-secondary;
        background: transparent;
        border: 1px solid $border-color;

        &:hover {
            background: $ai-color;
            color: $text-primary;
            border-color: $text-secondary;
        }
    }

    &.delete {
        color: #ef4444;
        background: transparent;
        border: 1px solid #fecaca;

        &:hover {
            background: #fef2f2;
            border-color: #ef4444;
        }
    }

    &.save {
        color: white;
        background: $primary-color;
        border: none;

        &:hover {
            background: color.scale($primary-color, $lightness: -9%);
        }
    }

    &.cancel {
        color: $text-secondary;
        background: transparent;
        border: 1px solid $border-color;

        &:hover {
            background: $ai-color;
            color: $text-primary;
        }
    }
}

.message-actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}
</style>