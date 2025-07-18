import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import init_db

if __name__ == "__main__":
    # 获取项目根目录下的app.db路径
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, 'app.db')
    # 删除旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已删除旧数据库: {db_path}")
    else:
        print(f"未检测到旧数据库: {db_path}")
    # 初始化新数据库
    init_db()
    print("数据库已初始化并同步最新结构！") 