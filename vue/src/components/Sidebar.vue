<template>
    <nav class="sidebar">
        <ul class="menu">
            <!-- <li><router-link to="/" class="menu-item">首页</router-link></li> -->
            <li><router-link to="/key-value" class="menu-item">知识库</router-link></li>
            <li><router-link to="/prompt" class="menu-item">提示词</router-link></li>
            <li><router-link to="/strategy" class="menu-item">策略</router-link></li>
            <!-- <li><router-link to="/other" class="menu-item">其他</router-link></li> -->
        </ul>
        <button @click="logout" class="logout-btn">退出</button>
    </nav>
</template>

<script>
export default {
    methods: {
        logout() {
            localStorage.clear();
            window.location.reload();
        }
    }
}
</script>

<style lang="scss" scoped>
.sidebar {
    width: 160px;
    height: 100vh;
    background-color: #f5f5f5;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 20px 0;
    box-shadow: 1px 0 3px rgba(0, 0, 0, 0.1);
    box-sizing: border-box;

    .menu {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
            margin-bottom: 10px;
        }

        .menu-item {
            display: block;
            padding: 10px 15px;
            color: #333;
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;

            &:hover,
            &.router-link-exact-active {
                background-color: #e0e0e0;
                border-left-color: #3498db;
            }
        }
    }

    .logout-btn {
        margin: 0 15px;
        padding: 10px;
        background-color: #e74c3c;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;

        &:hover {
            background-color: #c0392b;
        }
    }
}
</style>