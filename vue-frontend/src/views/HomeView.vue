<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="home-container">
    <div class="hero">
      <h1 class="artistic-title">Canvas Echo <span>(画布回声)</span></h1>
      <nav class="nav-buttons">
  <RouterLink to="/about" active-class="router-link-exact-active">
    <span class="artistic-text">About</span>
  </RouterLink>
  <RouterLink to="/design-review" active-class="router-link-exact-active">
    <span class="artistic-text">Design</span>
  </RouterLink>

      </nav>
       <p class="subtitle" style="margin-top: 2.5rem;">AI智能设计助手，将您的想法转化为精美HTML页面</p>
    </div>
    
    <div class="features">
      <h2 class="section-title">🌟 核心功能</h2>
      <ul>
        <li>
          <div class="feature-title">聊天即设计</div>
          <div class="feature-desc">描述需求或上传草图，AI快速生成页面设计</div>
        </li>
        <li>
          <div class="feature-title">实时预览</div>
          <div class="feature-desc">即时查看并反馈设计效果，所见即所得</div>
        </li>
        <li>
          <div class="feature-title">多格式导出</div>
          <div class="feature-desc">支持纯HTML、响应式页面及组件代码导出</div>
        </li>
      </ul>
    </div>
    
    <div class="cta-section">
      <p>Canvas Echo，让网页设计更简单、更智能！</p>
      <RouterLink to="/design-review" class="cta-button">
        <span class="artistic-text">立即体验</span>
      </RouterLink>
    </div>
  </main>
</template>

<style scoped>


.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 4rem 2rem;
  text-align: center;
}

.hero {
  margin-bottom: 4rem;
  padding: 3rem 0;
  position: relative;
}

.hero::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 3px;
  background: linear-gradient(90deg, transparent, #1a1a1a, transparent);
}

.artistic-title {
  font-family: 'Black Ops One', 'Noto Sans SC', sans-serif;
  font-weight: 900;
  font-size: 4.5rem;
  color: #000;
  text-shadow: 
    3px 3px 0 #fff, 
    -3px -3px 0 #fff, 
    3px -3px 0 #fff, 
    -3px 3px 0 #fff,
    0 3px 0 #fff,
    3px 0 0 #fff,
    0 -3px 0 #fff,
    -3px 0 0 #fff;
  letter-spacing: 2px;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
}

.artistic-title:hover {
  transform: scale(1.02);
}

.artistic-title span {
  font-family: 'Noto Sans SC', sans-serif;
  font-weight: 900;
}

.subtitle {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 1.8rem;
  color: #444;
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.6;
}

.section-title {
  font-family: 'Black Ops One', 'Noto Sans SC', sans-serif;
  font-weight: 900;
  font-size: 2.5rem;
  color: #000;
  text-shadow: 
    2px 2px 0 #fff, 
    -2px -2px 0 #fff, 
    2px -2px 0 #fff, 
    -2px 2px 0 #fff;
  margin-bottom: 2.5rem;
  position: relative;
  display: inline-block;
  padding-bottom: 1rem;
}

.section-title::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 3px;
  background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
}

.features {
  margin: 4rem 0;
  padding: 0 1rem;
}

.features ul {
  list-style: none;
  padding: 0;
  max-width: 800px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2.5rem;
}

.features li {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.4s ease;
  border: 1px solid #eaeaea;
}

.features li:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.feature-title {
  font-family: 'Noto Sans SC', sans-serif;
  font-weight: 900;
  font-size: 1.6rem;
  color: #1a1a1a;
  margin-bottom: 1rem;
  position: relative;
  display: inline-block;
}

.feature-title::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 40px;
  height: 3px;
  background: #1a1a1a;
  transition: all 0.3s ease;
}

.features li:hover .feature-title::after {
  width: 100%;
}

.feature-desc {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 1.1rem;
  color: #555;
  line-height: 1.6;
}

.cta-section {
  margin-top: 4rem;
  padding: 3rem;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border-radius: 15px;
  border: 1px solid #eaeaea;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.cta-section p {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 2rem;
  font-weight: 700;
}

.cta-button {
  display: inline-block;
  background: #1a1a1a;
  color: white;
  border: none;
  border-radius: 30px;
  padding: 1rem 3rem;
  font-size: 1.2rem;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.cta-button:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

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
}

/* 响应式设计 */
@media (max-width: 768px) {
  .artistic-title {
    font-size: 3rem;
  }
  
  .subtitle {
    font-size: 1.4rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features ul {
    grid-template-columns: 1fr;
  }
  
  .cta-section p {
    font-size: 1.5rem;
  }
}

/* 导航按钮样式 */
.nav-buttons a {
  text-decoration: none;
  background: #1a1a1a;
  padding: 1.2rem 3rem; /* 增加按钮大小 */
  border-radius: 30px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.nav-buttons a:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

/* 调整艺术字大小 */
.nav-buttons .artistic-text {
  font-size: 1.8rem; /* 与核心功能标题大小一致 */
}



/* 修改导航按钮间距 */
.nav-buttons {
  display: flex;
  justify-content: center;
  gap: 6rem; /* 增加按钮间距 */
  margin: 3rem 0; /* 增加上下边距 */
}

/* 为每个导航链接添加额外间距 */
.nav-link {
  margin: 0 1.5rem; /* 增加左右间距 */
}

/* 调整艺术字大小 */
.nav-buttons .artistic-text {
  font-size: 1.8rem;
  padding: 0 1rem; /* 增加文字左右内边距 */
}

/* 增加副标题上边距 */
.subtitle {
  margin-top: 2.5rem !important; /* 确保覆盖内联样式 */
}

/* 响应式设计 - 移动端调整 */
@media (max-width: 768px) {
  .nav-buttons {
    gap: 3rem; /* 移动端按钮间距 */
  }
  
  .nav-link {
    margin: 0 0.5rem; /* 移动端左右间距 */
  }
  
  .nav-buttons .artistic-text {
    font-size: 1.5rem; /* 移动端字体大小 */
  }
  
  .subtitle {
    margin-top: 1.5rem !important; /* 移动端上边距 */
  }
}


</style>