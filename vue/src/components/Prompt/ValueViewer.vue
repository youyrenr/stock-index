<template>
    <div>
        <label class="upload-btn">
            选择文件
            <input type="file" @change="handleFileUpload" accept=".md,.txt" class="hidden-input" />
        </label>
        <MdEditor v-model="markdown" @onSave="saveContent" :showToolbar="true" previewTheme="github" />
    </div>
</template>

<script>
import { ref, watch } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import api from '../../services/api'

export default {
    name: 'ValueViewer',
    components: {
        MdEditor
    },
    props: {
        value: {
            type: String,
            default: ''
        },
        currentKey: {
            type: String,
            required: true
        }
    },
    setup(props, { emit }) {
        console.log(props)
        const markdown = ref(props.value)

        // 监听 value 变化
        watch(() => props.value, (newValue) => {
            markdown.value = newValue
        })

        // 保存编辑器内容
        const saveContent = async (text) => {
            try {
                if(text == "") {
                    text = props.currentKey
                }
                await api.put('/prompts', {
                    key: props.currentKey,
                    value: text
                })
                emit('content-saved', text)
                console.log('Content saved successfully')
            } catch (error) {
                console.error('Failed to save content', error)
            }
        }

        // 处理文件上传
        const handleFileUpload = (event) => {
            const file = event.target.files[0]
            if (file && (file.type === 'text/markdown' || file.type === 'text/plain')) {
                const reader = new FileReader()
                reader.onload = (e) => {
                    markdown.value = e.target.result
                    // 清空文件选择框
                    event.target.value = null
                }
                reader.readAsText(file)
            } else {
                alert('Please upload a .md or .txt file')
            }
        }

        return {
            markdown,
            saveContent,
            handleFileUpload
        }
    }
}
</script>

<style>
.upload-btn {
    display: inline-block;
    padding: 7px 14px;
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    cursor: pointer;
    font-size: 13px;
    margin-bottom: 10px;
}

.upload-btn:hover {
    background-color: #0056b3;
}

.hidden-input {
    display: none;
}

.md-editor {
    height: 85vh;
}
</style>