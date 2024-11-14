<template>
    <div class="strategy-view">
        <div class="page-header">
            <h2>策略管理</h2>
            <button class="btn-primary" @click="showAddDialog">添加策略</button>
        </div>

        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>策略Key</th>
                        <th>策略内容</th>
                        <!-- <th>状态</th> -->
                        <th>创建时间</th>
                        <th>更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in strategies" :key="item.key">
                        <td>{{ item.key }}</td>
                        <td>{{ item.value }}</td>
                        <!-- <td>{{ item.status == '0' ? '未开始' : item.status == '1' ? '进行中' : item.status == '2' ? '已完成' :
                '错误' }}</td> -->
                        <td>{{ formatDate(item.created_at) }}</td>
                        <td>{{ formatDate(item.updated_at) }}</td>
                        <td class="operation-column">
                            <button class="btn-call" @click="showChatDialog(item)">调用</button>
                            <button class="btn-edit" @click="showEditDialog(item)">编辑</button>
                            <el-popconfirm title="确认删除该策略吗？" confirm-button-text="确定" cancel-button-text="取消"
                                @confirm="handleDelete(item)">
                                <template #reference>
                                    <button class="btn-delete">删除</button>
                                </template>
                            </el-popconfirm>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- 添加/编辑弹窗 -->
        <StrategyDialog v-if="showDialog" :visible="showDialog" :editData="currentStrategy" @close="closeDialog"
            @submit="handleSubmit" />

        <ChatDialog v-if="showChatDialogVisible" :visible="showChatDialogVisible" :strategy="currentStrategy"
            @close="closeChatDialog" @update:strategy="handleStrategyUpdate" />
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import StrategyDialog from '../components/Strategy/StrategyDialog.vue'
import ChatDialog from '../components/Strategy/ChatDialog.vue'
import { ElMessage, ElPopconfirm } from 'element-plus'
import api from '../services/api'

export default {
    name: 'StrategyView',
    components: {
        StrategyDialog,
        ChatDialog,
        ElPopconfirm
    },
    setup() {
        const strategies = ref([])
        const showDialog = ref(false)
        const currentStrategy = ref(null)
        const showChatDialogVisible = ref(false)
        const showChatDialog = (strategy) => {
            currentStrategy.value = { ...strategy }
            showChatDialogVisible.value = true
        }

        const closeChatDialog = () => {
            showChatDialogVisible.value = false
            currentStrategy.value = null
        }

        const handleStrategyUpdate = async (updatedStrategy) => {
            try {
                await loadStrategies()
            } catch (error) {
                console.error('更新策略失败:', error)
            }
        }

        const loadStrategies = async () => {
            try {
                const response = await api.post('/strategies/list', {
                    skip: 0,
                    limit: 100
                })
                strategies.value = response.data
            } catch (error) {
                ElMessage.error('加载策略列表失败')
            }
        }

        const showAddDialog = () => {
            currentStrategy.value = null
            showDialog.value = true
        }

        const showEditDialog = (strategy) => {
            currentStrategy.value = { ...strategy }
            showDialog.value = true
        }

        const closeDialog = () => {
            showDialog.value = false
            currentStrategy.value = null
        }

        const handleSubmit = async (formData) => {
            try {
                if (currentStrategy.value) {
                    await api.put('/strategies', formData)
                    ElMessage.success('更新成功')
                } else {
                    await api.post('/strategies', formData)
                    ElMessage.success('添加成功')
                }
                closeDialog()
                loadStrategies()
            } catch (error) {
                ElMessage.error(currentStrategy.value ? '更新失败' : '添加失败')
            }
        }

        const handleDelete = async (strategy) => {
            try {
                await api.delete('/strategies', {
                    data: { key: strategy.key }
                })
                ElMessage.success('删除成功')
                loadStrategies()
            } catch (error) {
                ElMessage.error('删除失败')
            }
        }

        const formatDate = (dateStr) => {
            return new Date(dateStr).toLocaleString()
        }

        onMounted(() => {
            loadStrategies()
        })

        return {
            strategies,
            showDialog,
            currentStrategy,
            showAddDialog,
            showEditDialog,
            closeDialog,
            handleSubmit,
            handleDelete,
            formatDate,
            showChatDialogVisible,
            showChatDialog,
            closeChatDialog,
            handleStrategyUpdate
        }
    }
}
</script>

<style lang="scss">
.strategy-view {
    padding: 20px;
    height: 100%;
    background-color: #f0f4f8;

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;

        h2 {
            margin: 0;
            color: #2c3e50;
        }
    }

    .table-container {
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
        padding: 20px;
        overflow-x: auto;
    }

    .data-table {
        width: 100%;
        border-collapse: collapse;

        th,
        td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ebeef5;
        }

        th {
            background-color: #f5f7fa;
            color: #606266;
            font-weight: 500;
        }

        .operation-column {
            white-space: nowrap;
        }
    }

    .btn-primary {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;

        &:hover {
            background-color: #2980b9;
        }
    }

    .btn-edit,
    .btn-delete {
        padding: 4px 8px;
        border: none;
        border-radius: 4px;
        margin-right: 8px;
        cursor: pointer;
        font-size: 14px;
    }

    .btn-edit {
        background-color: #67c23a;
        color: white;

        &:hover {
            background-color: #529b2e;
        }
    }

    .btn-delete {
        background-color: #f56c6c;
        color: white;

        &:hover {
            background-color: #e64242;
        }
    }

    .btn-call {
        padding: 4px 8px;
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 4px;
        margin-right: 8px;
        cursor: pointer;
        font-size: 14px;

        &:hover {
            background-color: #2980b9;
        }
    }
}
</style>