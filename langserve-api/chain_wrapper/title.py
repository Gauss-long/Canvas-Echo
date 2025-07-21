import dashscope
import re
import os
from dotenv import load_dotenv
def get_title(text: str) -> str:
    """
    使用阿里云 Qwen-Turbo 模型生成不超过8个字的标题
    需要设置环境变量 DASHSCOPE_API_KEY
    """
    # 设置你的阿里云API密钥（从环境变量获取）
    load_dotenv()
     # 获取 API 密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError("未检测到 DASHSCOPE_API_KEY，请检查 .env 文件")
    
    dashscope.api_key = api_key
    
    # 创建优化后的提示词
    prompt = f"""请为以下内容生成一个精炼的中文标题，严格遵守以下要求：
                1. 标题长度不超过8个汉字
                2. 包含核心信息
                3. 避免使用标点符号和特殊字符
                4. 语言简洁有力

                文本内容：
                {text}"""

    try:
        # 调用 Qwen-Turbo API
        response = dashscope.Generation.call(
            model='qwen-turbo',
            prompt=prompt,
            max_length=50,
            top_p=0.8,
            result_format='message'
        )
        
        if response.status_code == 200:
            # 提取生成的标题
            title = response.output.choices[0]['message']['content'].strip()
            
            # 清洗标题：移除引号、冒号等特殊字符
            title = re.sub(r'["\':：]', '', title)
            
            # 确保不超过8字
            chinese_chars = [c for c in title if '\u4e00' <= c <= '\u9fff']
            if len(chinese_chars) > 8:
                # 找到第8个汉字的位置
                count = 0
                index = 0
                for i, char in enumerate(title):
                    if '\u4e00' <= char <= '\u9fff':
                        count += 1
                        if count == 8:
                            index = i + 1
                            break
                return title[:index]
            return title
        else:
            raise Exception(f"API错误: {response.code} - {response.message}")
    
    except Exception as e:
        # API调用失败时的备用方案
        print(f"警告: Qwen-Turbo调用失败, 使用备用方案: {str(e)}")
        return extract_title_fallback(text)

def extract_title_fallback(text: str) -> str:
    """API调用失败时的备用方案（纯文本处理）"""
    # 移除特殊字符和标点
    cleaned = re.sub(r'[^\w\u4e00-\u9fff\s]', '', text)
    # 提取前8个中文字符
    chinese_chars = [c for c in cleaned if '\u4e00' <= c <= '\u9fff']
    return ''.join(chinese_chars[:8])
