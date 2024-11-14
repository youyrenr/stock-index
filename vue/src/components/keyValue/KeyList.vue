<template>
  <div class="key-list">
    <div class="search-container">
      <input v-model="search" placeholder="搜索" class="search-input">
      <span class="search-icon">🔍</span>
    </div>
    <ul class="key-items">
      <li v-for="item in filteredItems" :key="item.key" class="key-item">
        <div class="key-item-header" :class="{ 'selected': selectedKey === item.key }">
          <span class="arrow" @click.stop="toggleExpand(item)">
            <i :class="['fas', item.expanded ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
          </span>
          <span class="key-text" @click="selectKey(item.key)">{{ item.key }}</span>
          <div class="key-actions">
            <button v-if="userType == 1" class="action-btn add-btn" @click="showAddDialog(item.key)">
              <i class="fas fa-plus"></i>
            </button>
            <button v-if="userType == 1" class="action-btn delete-btn" @click="confirmDelete(item.key)">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        </div>
        <transition name="expand">
          <ul v-if="item.expanded" class="sub-items">
            <li v-for="subItem in item.children" :key="subItem.key" class="sub-item"
              :class="{ 'selected': selectedKey === subItem.key }">
              <span class="key-text" @click="selectKey(subItem.key)">{{ subItem.key }}</span>
              <div class="key-actions">
                <button v-if="userType == 1" class="action-btn delete-btn" @click="confirmDelete(subItem.key)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </li>
          </ul>
        </transition>
      </li>
    </ul>
    <div class="add-key-container" v-if="userType == 1">
      <input v-model="newKey" placeholder="输入键名" class="add-input">
      <button @click="addNewKey" :disabled="!newKey.trim()" class="add-button">新增</button>
    </div>

    <!-- 确认删除对话框 -->
    <transition name="fade">
      <div v-if="showConfirmDialog" class="modal-overlay">
        <div class="modal-content confirm-dialog">
          <p>确定要删除 "{{ keyToDelete }}" 吗？</p>
          <div class="modal-actions">
            <button @click="deleteKey" class="confirm-btn">确定</button>
            <button @click="cancelDelete" class="cancel-btn">取消</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 添加子键对话框 -->
    <transition name="fade">
      <div v-if="isAddDialogVisible" class="modal-overlay">
        <div class="modal-content add-dialog">
          <h3>添加子键</h3>
          <input v-model="newSubKey" placeholder="输入子键名" class="add-input">
          <input v-model="newSubValue" placeholder="输入子键值" class="add-input">
          <div class="modal-actions">
            <button @click="addSubKey" :disabled="!newSubKey.trim() || !newSubValue.trim()"
              class="confirm-btn">添加</button>
            <button @click="cancelAddSubKey" class="cancel-btn">取消</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

export default {
  emits: ['select-key', 'key-added', 'key-deleted'],
  setup(props, { emit }) {
    const items = ref([])
    const search = ref('')
    const newKey = ref('')
    const showConfirmDialog = ref(false)
    const keyToDelete = ref('')
    const isAddDialogVisible = ref(false)
    const parentKeyForAdd = ref('')
    const newSubKey = ref('')
    const newSubValue = ref('')
    const selectedKey = ref('')

    const fetchKeys = async () => {
      try {
        const response = await api.post('/key-values/keys', { skip: 0, limit: 1000, parentKey: "" })
        console.log("返回", response)
        items.value = response.data.map(item => ({
          ...item,
          expanded: false,
          children: []
        }))
      } catch (error) {
        console.error('Failed to fetch keys', error)
      }
    }

    onMounted(fetchKeys)

    const filteredItems = computed(() => {
      return items.value.filter(item => item.key.toLowerCase().includes(search.value.toLowerCase()))
    })

    const addNewKey = async () => {
      if (newKey.value.trim()) {
        try {
          await api.post('/key-values', { key: newKey.value, value: newKey.value })
          items.value.push({ key: newKey.value, expanded: false, children: [] })
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
        items.value = items.value.filter(item => item.key !== keyToDelete.value)
        emit('key-deleted', keyToDelete.value)

        await fetchKeys()

        if (selectedKey.value === keyToDelete.value) {
          selectedKey.value = ''
          emit('select-key', '')
        }
        showConfirmDialog.value = false
      } catch (error) {
        console.error('Failed to delete key', error)
      }
    }

    const cancelDelete = () => {
      showConfirmDialog.value = false
      keyToDelete.value = ''
    }

    const toggleExpand = async (item) => {
      item.expanded = !item.expanded
      if (item.expanded && item.children.length === 0) {
        try {
          const response = await api.post('/key-values/keys', { skip: 0, limit: 1000, parentKey: item.key })
          console.log("返回", response)
          item.children = response.data
        } catch (error) {
          console.error('Failed to fetch sub-keys', error)
        }
      }
    }

    const showAddDialog = (parentKey) => {
      parentKeyForAdd.value = parentKey
      isAddDialogVisible.value = true
    }

    const addSubKey = async () => {
      if (newSubKey.value.trim() && newSubValue.value.trim()) {
        try {
          await api.post('/key-values', {
            key: newSubKey.value,
            value: newSubValue.value,
            parentKey: parentKeyForAdd.value
          })
          const parentItem = items.value.find(item => item.key === parentKeyForAdd.value)
          if (parentItem) {
            parentItem.children.push({ key: newSubKey.value })
          }
          emit('key-added', newSubKey.value)
          newSubKey.value = ''
          newSubValue.value = ''
          isAddDialogVisible.value = false
        } catch (error) {
          console.error('Failed to add new sub-key', error)
        }
      }
    }

    const cancelAddSubKey = () => {
      isAddDialogVisible.value = false
      newSubKey.value = ''
      newSubValue.value = ''
    }

    const selectKey = (key) => {
      selectedKey.value = key
      emit('select-key', key)
    }

    return {
      items,
      search,
      filteredItems,
      newKey,
      addNewKey,
      showConfirmDialog,
      keyToDelete,
      confirmDelete,
      deleteKey,
      cancelDelete,
      toggleExpand,
      showAddDialog,
      isAddDialogVisible,
      parentKeyForAdd,
      newSubKey,
      newSubValue,
      addSubKey,
      cancelAddSubKey,
      selectedKey,
      selectKey
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
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

.key-list {
  box-sizing: border-box;
  position: relative;
  padding: 20px;
  background-color: #f8f9fa;
  height: 100vh;
  display: flex;
  flex-direction: column;
  max-width: 600px;
  margin: 0 auto;
  font-family: 'Arial', sans-serif;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      color: #2c3e50;
      font-size: 24px;
    }
  }

  .search-container {
    position: relative;
    margin-bottom: 20px;

    .search-input {
      box-sizing: border-box;
      width: 100%;
      padding: 12px 15px 12px 40px;
      border: 1px solid #e0e6ed;
      border-radius: 8px;
      font-size: 14px;
      transition: all 0.3s ease;
      background-color: #ffffff;

      &:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
      }
    }

    .search-icon {
      position: absolute;
      left: 15px;
      top: 50%;
      transform: translateY(-50%);
      color: #7f8c8d;
    }
  }

  button {
    padding: 10px 15px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.1s ease;
    font-size: 14px;
    font-weight: bold;

    &:hover {
      background-color: #2980b9;
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(1px);
    }

    &:disabled {
      background-color: #bdc3c7;
      cursor: not-allowed;
    }

    &.logout-btn {
      background-color: #e74c3c;

      &:hover {
        background-color: #c0392b;
      }
    }
  }

  .key-items {
    list-style-type: none;
    padding: 2px;
    flex-grow: 1;
    overflow-y: auto;
    margin: 0;

    .key-item {
      margin-bottom: 8px;

      .key-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 15px;
        border-radius: 8px;
        transition: all 0.2s ease;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

        &:hover {
          background-color: #f0f4f8;
        }

        &.selected {
          background-color: #e0e6ed;
          box-shadow: 0 0 0 2px #3498db;
        }

        .arrow {
          cursor: pointer;
          margin-right: 10px;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;

          i {
            color: #3498db;
            transition: transform 0.2s ease;
          }
        }

        .key-text {
          cursor: pointer;
          flex-grow: 1;
          font-size: 16px;
          color: #2c3e50;

          &:hover {
            color: #3498db;
          }
        }

        .key-actions {
          display: flex;

          .action-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 5px;
            color: #2ecc71;
            transition: color 0.2s ease, transform 0.1s ease;

            &:hover {
              transform: scale(1.1);
            }

            &:active {
              transform: scale(0.95);
            }

            &.delete-btn {
              color: #e74c3c;

              &:hover {
                color: #c0392b;
              }
            }
          }
        }
      }

      .sub-items {
        list-style-type: none;
        padding-left: 30px;
        margin-top: 8px;

        .sub-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          margin-top: 5px;
          background-color: #f8f9fa;
          border-radius: 6px;
          transition: background-color 0.2s ease;

          &:hover {
            background-color: #e0e6ed;
          }

          &.selected {
            background-color: #d4e6f1;
            box-shadow: 0 0 0 2px #3498db;
          }
        }
      }
    }
  }

  .add-key-container {
    display: flex;
    margin-top: 20px;

    .add-button {
      padding: 10px 20px;
    }
  }
}

.add-input {
  flex-grow: 1;
  margin-right: 10px;
  padding: 10px 15px;
  border: 1px solid #e0e6ed;
  border-radius: 8px;
  font-size: 14px;
}

.modal-overlay {
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

  .modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 400px;
    width: 100%;

    h3 {
      margin-top: 0;
      color: #2c3e50;
    }

    p {
      margin-bottom: 20px;
      color: #34495e;
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;

      .confirm-btn,
      .cancel-btn {
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        transition: all 0.3s ease;
      }

      .confirm-btn {
        background-color: #2ecc71;

        &:hover {
          background-color: #27ae60;
        }
      }

      .cancel-btn {
        background-color: #e74c3c;

        &:hover {
          background-color: #c0392b;
        }
      }
    }
  }
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease-in-out;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  height: 0;
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>