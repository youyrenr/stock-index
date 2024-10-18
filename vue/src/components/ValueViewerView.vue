<template>
    <MdPreview :modelValue="value" previewTheme="github" />
</template>

<script>
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

export default {
    name: 'ValueViewerView',
    components: {
        MdPreview
    },
    props: {
        value: {
            type: String,
            default: ''
        }
    }
}
</script>

<style>
/* Webkit 浏览器 (Chrome, Safari) */
::-webkit-scrollbar {
    width: 10px;
    /* 设置滚动条的宽度 */
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, #ffffff, #ffffff);
    /* 滚动条的颜色或渐变 */
    border-radius: 5px;
    /* 滚动条的圆角 */
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, #ffffff, #ffffff);
    /* 滚动条在悬停时的颜色 */
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    /* 滚动条轨道的颜色 */
}

/* Firefox 浏览器 */
* {
    scrollbar-width: thin;
    /* 设置滚动条宽度为窄 */
    scrollbar-color: #bbbbbb #f1f1f1;
    /* 前景色和背景色 */
}
</style>