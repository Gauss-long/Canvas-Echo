<template>
  <div class="about">
    <!-- 悬浮返回按钮 -->
    <button class="back-to-home" :class="{ 'show': showBackButton }" @click="goHome">
      <i class="fa fa-arrow-left"></i>
      <span>返回首页</span>
    </button>

    <div class="team-container">
      <!-- 团队头部 -->
      <div class="team-header">
        <h1 class="artistic-title">TEAM</h1>
        <div class="subtitle">创新 · 协作 · 卓越</div>
      </div>

      <!-- 团队成员 -->
      <div class="team-grid">
        <div class="leader-card">
          <div class="leader-info">
            <h2 class="leader-name">郭鑫隆</h2>
            <div class="leader-role">组长 / 项目负责人</div>
            <div class="leader-desc">战略规划 · 团队领导 · 决策制定</div>
          </div>
          <div class="leader-quote">
            "优秀的团队由共同的目标、信任和协作构建"
          </div>
        </div>

        <div class="members-section">
          <div class="section-title">团队成员</div>
          <div class="members-grid">
            <div class="member-card">
              <div class="member-info">
                <h3 class="member-name">谢小珂</h3>
                <div class="member-role">开发工程师</div>
              </div>
              <div class="member-desc">积微成著·借势而为·化凡为奇</div>
            </div>

            <div class="member-card">
              <div class="member-info">
                <h3 class="member-name">王采奕</h3>
                <div class="member-role">开发工程师</div>
              </div>
              <div class="member-desc">聚沙成塔·持之以恒·终成大势</div>
            </div>

            <div class="member-card">
              <div class="member-info">
                <h3 class="member-name">吴行健</h3>
                <div class="member-role">开发工程师</div>
              </div>
              <div class="member-desc">另辟蹊径·洞察先机·焕发新生</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 应用场景 -->
      <div class="application-scenarios">
        <div class="section-title">应用场景</div>
        <ul class="scenario-list">
          <li class="scenario-item">快速原型制作与迭代</li>
          <li class="scenario-item">企业官网、电商落地页设计</li>
          <li class="scenario-item">广告创意和营销活动页面</li>
        </ul>
      </div>

      <!-- 联系我们 -->
      <div class="contact-us">
        <div class="section-title">联系我们</div>
        <div class="contact-info email">2338485672@qq.com</div>
        <div class="contact-info phone"> +86 166 2905 8429</div>
      </div>

      <!-- 页脚 -->
      <div class="team-footer">
        <div class="copyright">© 2025 创新团队 | 简约成就卓越</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 引入更大气的字体 */
@import url('https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Black+Ops+One&family=Noto+Sans+SC:wght@400;700;900&display=swap');

/* 基础样式与平滑滚动 */
html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  padding: 0;
}

.about {
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
  background: #f8f9fa;
  padding: 4rem 2rem;
  font-family: 'Noto Sans SC', sans-serif;
  color: #333;
  overflow-x: hidden;
  text-align: center;
}

.team-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* 悬浮返回按钮 */
.back-to-home {
  position: fixed;
  bottom: 40px;
  left: 40px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 25px;
  font-size: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  opacity: 0;
  visibility: hidden;
  transform: translateX(-20px);
}

.back-to-home.show {
  opacity: 1;
  visibility: visible;
  transform: translateX(0);
}

.back-to-home:hover {
  background-color: #1a1a1a;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.back-to-home:active {
  transform: translateY(1px);
}

/* 团队头部样式 */
.team-header {
  margin-bottom: 4rem;
  padding: 3rem 0;
  position: relative;
}

.team-header::after {
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

.subtitle {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 1.8rem;
  color: #444;
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.6;
}

/* 团队成员样式 */
.team-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 4rem;
  margin-bottom: 6rem;
}

.leader-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  transition: all 0.4s ease;
  border: 1px solid #eaeaea;
}

.leader-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.leader-name {
  font-family: 'Black Ops One', 'Noto Sans SC', sans-serif;
  font-weight: 900;
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: #000;
  text-shadow: 
    2px 2px 0 #fff, 
    -2px -2px 0 #fff, 
    2px -2px 0 #fff, 
    -2px 2px 0 #fff;
  letter-spacing: 2px;
  transition: all 0.3s ease;
}

.leader-name:hover {
  transform: scale(1.02);
}

.leader-role {
  color: #555;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 2rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  position: relative;
  padding-left: 10px;
}

.leader-role::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 80%;
  background: #555;
}

.leader-desc {
  color: #555;
  font-size: 1.2rem;
  line-height: 1.8;
  max-width: 600px;
  margin-top: 1rem;
  padding-left: 10px;
  border-left: 1px solid #eaeaea;
  margin: 0 auto;
}

.leader-quote {
  font-style: italic;
  color: #888;
  font-size: 1.3rem;
  padding: 2rem;
  border-top: 1px solid #eaeaea;
  margin-top: 2rem;
  text-align: right;
  letter-spacing: 1px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 0 0 5px 5px;
}

.members-section {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  transition: all 0.4s ease;
  border: 1px solid #eaeaea;
}

.members-section:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
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

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2.5rem;
}

.member-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  transition: all 0.4s ease;
  border: 1px solid #eaeaea;
}

.member-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.member-name {
  font-family: 'Black Ops One', 'Noto Sans SC', sans-serif;
  font-weight: 900;
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #000;
  text-shadow: 
    2px 2px 0 #fff, 
    -2px -2px 0 #fff, 
    2px -2px 0 #fff, 
    -2px 2px 0 #fff;
  letter-spacing: 2px;
  transition: all 0.3s ease;
}

.member-name:hover {
  transform: scale(1.02);
}

.member-role {
  color: #555;
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  padding-bottom: 5px;
}

.member-role::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 30px;
  height: 2px;
  background: #555;
  transition: all 0.3s ease;
}

.member-card:hover .member-role::after {
  width: 100%;
}

.member-desc {
  color: #555;
  font-size: 1.1rem;
  line-height: 1.6;
  padding-top: 1rem;
  border-top: 1px solid #eaeaea;
}

/* 应用场景样式 */
.application-scenarios {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  transition: all 0.4s ease;
  border: 1px solid #eaeaea;
  margin-bottom: 6rem;
}

.application-scenarios:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.scenario-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-width: 800px;
  margin: 0 auto;
}

.scenario-item {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 1.5rem;
  line-height: 2;
  margin-bottom: 2rem;
  padding-left: 2rem;
  position: relative;
  color: #555;
  transition: all 0.3s ease;
}

.scenario-item::before {
  content: "•";
  position: absolute;
  left: 0;
  top: 0;
  color: #aaa;
  font-size: 2rem;
  transition: all 0.3s ease;
}

.scenario-item:hover {
  transform: translateX(10px);
  color: #1a1a1a;
}

.scenario-item:hover::before {
  color: #1a1a1a;
}

/* 联系我们样式 */
.contact-us {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  transition: all 0.4s ease;
  border: 1px solid #eaeaea;
  margin-bottom: 6rem;
}

.contact-us:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.contact-info {
  font-family: 'Noto Sans SC', sans-serif;
  color: #555;
  font-size: 1.5rem;
  letter-spacing: 2px;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
  position: relative;
  display: block;
}

.contact-info::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #1a1a1a;
  transition: all 0.3s ease;
}

.contact-info:hover {
  color: #1a1a1a;
  transform: translateY(-3px);
}

.contact-info:hover::after {
  width: 100%;
}

/* 页脚样式 */
.team-footer {
  margin-top: 8rem;
  text-align: center;
  padding: 3rem 0;
  border-top: 2px solid #eaeaea;
}

.copyright {
  color: #777;
  font-size: 1rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  position: relative;
}

.copyright::before {
  content: "";
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 1px;
  background: #eaeaea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .artistic-title {
    font-size: 3rem;
  }
  
  .subtitle {
    font-size: 1.4rem;
  }
  
  .leader-name,
  .section-title {
    font-size: 2rem;
  }
  
  .member-name {
    font-size: 1.8rem;
  }
  
  .scenario-item,
  .contact-info {
    font-size: 1.3rem;
  }
  
  .members-grid {
    grid-template-columns: 1fr;
  }
  
  .back-to-home {
    bottom: 20px;
    left: 20px;
    padding: 10px 15px;
    font-size: 14px;
  }
}
</style>

<script>
export default {
  name: 'AboutView',
  data() {
    return {
      showBackButton: false
    }
  },
  mounted() {
    // 监听滚动事件
    window.addEventListener('scroll', this.handleScroll);
    // 初始检查一次
    this.handleScroll();
  },
  beforeDestroy() {
    // 移除滚动事件监听
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    handleScroll() {
      // 当页面滚动超过300px时显示返回按钮
      this.showBackButton = window.scrollY > 300;
    },
    goHome() {
      // 返回主界面的逻辑
      this.$router.push('/');
    }
  }
}
</script>