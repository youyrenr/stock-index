<template>
    <div class="main-layout">
        <Sidebar />
        <div class="content">
            <router-view></router-view>
        </div>
    </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
    components: {
        Sidebar
    }
}
</script>

<style lang="scss" scoped>
$background-color: #f0f4f8;

.main-layout {
    display: flex;
    height: 100vh;
}

.content {
    flex: 1;
    background-color: $background-color;
    overflow: auto;
}
</style>