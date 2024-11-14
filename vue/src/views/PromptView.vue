<template>
    <div class="key-value-view">
        <PromptManager />
    </div>
</template>

<script>
import PromptManager from '../components/Prompt/PromptManager.vue'

export default {
    components: {
        PromptManager
    }
}
</script>

<style scoped>
.key-value-view {
    height: 100%;
    width: 100%;
}
</style>