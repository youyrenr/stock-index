<template>
    <div class="key-value-view">
        <KeyValueManager />
    </div>
</template>

<script>
import KeyValueManager from '../components/keyValue/KeyValueManager.vue'

export default {
    components: {
        KeyValueManager
    }
}
</script>

<style scoped>
.key-value-view {
    height: 100%;
    width: 100%;
}
</style>