"""
运营商指数数据自动收集工具配置文件
"""

import os
from datetime import datetime, timedelta

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'screenshots')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# 关键词配置
KEYWORDS = {
    'baidu': ['上海电信', '上海移动', '上海联通'],
    'wechat': ['上海电信', '上海移动', '上海联通']
}

# URL配置
BAIDU_INDEX_URL = 'https://index.baidu.com/v2/index.html#/'
WECHAT_MINIPROGRAM_PATH = '小程序://微信指数/RTGJwjluzNnWpqq'

# 时间配置
COLLECTION_DAYS = 7  # 收集7天数据
COLLECTION_HOUR = 9  # 每天9点开始收集（周五或周一）

# Excel模板配置
EXCEL_TEMPLATE = {
    '微信指数趋势': {
        'columns': ['日期', '星期', '上海电信每日指数', '每周指数平均值', 
                   '上海移动每日指数', '每周指数平均值', 
                   '上海联通每日指数', '每周指数平均值', '三家指数趋势对比'],
        'keywords': ['上海电信', '上海移动', '上海联通']
    },
    '百度指数搜索': {
        'columns': ['日期', '星期', '上海电信每日搜索指数', '每周指数平均值',
                   '上海移动每日搜索指数', '每周指数平均值',
                   '上海联通每日搜索指数', '每周指数平均值', '三家每日搜索指数趋势对比'],
        'keywords': ['上海电信', '上海移动', '上海联通']
    },
    '百度指数资讯': {
        'columns': ['日期', '星期', '上海电信每日资讯指数', '每周指数平均值',
                   '上海移动每日资讯指数', '每周指数平均值',
                   '上海联通每日资讯指数', '每周指数平均值', '三家每日资讯指数趋势对比'],
        'keywords': ['上海电信', '上海移动', '上海联通']
    }
}

# 浏览器配置
BROWSER_CONFIG = {
    'headless': True,   # Replit环境必须设为True
    'window_size': '1920,1080',
    'timeout': 30,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(LOGS_DIR, f'index_collector_{datetime.now().strftime("%Y%m%d")}.log')
}

# 截图配置
SCREENSHOT_CONFIG = {
    'baidu': {
        'full_page': True,
        'wait_time': 5,
        'file_prefix': 'baidu_index'
    },
    'wechat': {
        'full_page': True,
        'wait_time': 3,
        'file_prefix': 'wechat_index'
    }
}

def get_collection_dates():
    """获取需要收集数据的日期范围"""
    today = datetime.now()
    weekday = today.weekday()  # 0=周一, 6=周日
    
    # 如果是周五，收集上周四到本周四的数据
    if weekday == 4:  # 周五
        end_date = today - timedelta(days=1)  # 本周四
        start_date = end_date - timedelta(days=6)  # 上周四
    # 如果是周一，收集上周四到本周四的数据（数据可能有延迟）
    elif weekday == 0:  # 周一
        end_date = today - timedelta(days=4)  # 上周四
        start_date = end_date - timedelta(days=6)  # 上上周四
    else:
        # 其他时间，收集最近7天
        end_date = today - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
    
    return start_date, end_date

def create_directories():
    """创建必要的目录"""
    for dir_path in [DATA_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

# 初始化目录
create_directories()