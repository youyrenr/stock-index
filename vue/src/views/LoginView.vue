<template>
    <div class="login-view">
        <Login class="login"/>
    </div>
</template>

<script>
import Login from '../components/Login.vue'

export default {
    components: {
        Login
    }
}
</script>

<style scoped>
.login-view {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100%;
}

.login {
    width: 100%;
}
</style>