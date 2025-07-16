<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const isFullScreen = computed(() => route.meta.fullScreen)
</script>

<template>
  <header v-if="!isFullScreen">
    <div class="wrapper">
      <nav>
      </nav>
    </div>
  </header>
  <RouterView :class="{ 'full-screen': isFullScreen }" />
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Noto+Sans+SC:wght@900&display=swap');

/* 全屏样式 */
.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
}

header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: none; /* 隐藏 logo */
}

.wrapper {
  display: flex;
  place-items: flex-start;
  flex-wrap: wrap;
}

/* 艺术字样式 */
.artistic-text {
  font-family: 'Black Ops One', 'Noto Sans SC', sans-serif;
  font-weight: 900;
  color: #fff;
  text-shadow: 
    2px 2px 0 #000, 
    -2px -2px 0 #000, 
    2px -2px 0 #000, 
    -2px 2px 0 #000;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: all 0.3s ease; /* 添加平滑过渡效果 */
  margin: 0 1rem; /* 添加按钮间距 */
}

/* 中文特殊样式 */
.artistic-text:lang(zh) {
  font-family: 'Noto Sans SC', sans-serif;
  font-weight: 900;
  letter-spacing: 2px;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
  
  /* 大屏幕下调整艺术字大小 */
  .artistic-text {
    font-size:28px;
  }
}
</style>
