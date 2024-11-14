<template>
    <div class="dialog-overlay" v-if="visible" @click.self="handleClose">
        <div class="dialog-content">
            <div class="dialog-header">
                <h3>{{ editData ? '编辑策略' : '添加策略' }}</h3>
                <span class="close-btn" @click="handleClose">×</span>
            </div>

            <div class="dialog-body">
                <form @submit.prevent="handleSubmit">
                    <div class="form-item">
                        <label>策略Key:</label>
                        <input v-model="form.key" :readonly="!!editData" placeholder="请输入策略Key" required />
                    </div>

                    <div class="form-item">
                        <label>策略内容:</label>
                        <textarea v-model="form.value" placeholder="请输入策略内容" required></textarea>
                    </div>

                    <div class="dialog-footer">
                        <button type="button" class="btn-cancel" @click="handleClose">取消</button>
                        <button type="submit" class="btn-submit">确定</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
    props: {
        visible: {
            type: Boolean,
            required: true
        },
        editData: {
            type: Object,
            default: null
        }
    },

    emits: ['close', 'submit'],

    setup(props, { emit }) {
        const form = ref({
            key: '',
            value: '',
            status: '0'
        })

        watch(() => props.editData, (newVal) => {
            if (newVal) {
                form.value = { ...newVal }
            } else {
                form.value = { key: '', value: '', status: '0' }
            }
        }, { immediate: true })

        const handleClose = () => {
            emit('close')
        }

        const handleSubmit = () => {
            emit('submit', { ...form.value })
        }

        return {
            form,
            handleClose,
            handleSubmit
        }
    }
}
</script>

<style lang="scss" scoped>
.dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.dialog-content {
    background: white;
    border-radius: 8px;
    width: 500px;
    max-width: 90%;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.dialog-header {
    padding: 20px;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
        margin: 0;
        font-size: 18px;
        color: #303133;
    }

    .close-btn {
        border: none;
        background: none;
        font-size: 20px;
        cursor: pointer;
        color: #909399;

        &:hover {
            color: #606266;
        }
    }
}

.dialog-body {
    padding: 20px;

    .form-item {
        margin-bottom: 20px;

        label {
            display: block;
            margin-bottom: 8px;
            color: #606266;
        }

        input,
        textarea,
        select {
            width: 100%;
            padding: 8px;
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            font-size: 14px;

            &:focus {
                outline: none;
                border-color: #3498db;
            }
        }

        textarea {
            height: 100px;
            resize: vertical;
        }
    }
}

.dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;

    button {
        padding: 8px 20px;
        border-radius: 4px;
        cursor: pointer;
        border: none;
    }

    .btn-cancel {
        background-color: #ffffff;
        border: 1px solid #dcdfe6;
        color: #606266;

        &:hover {
            color: #3498db;
            border-color: #3498db;
        }
    }

    .btn-submit {
        background-color: #3498db;
        color: white;

        &:hover {
            background-color: #2980b9;
        }
    }
}
</style>