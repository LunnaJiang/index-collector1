# 运营商指数数据自动收集工具

## 📋 项目简介

这是一个自动化收集运营商指数数据的工具，能够定期收集百度指数和微信指数中关于"上海电信"、"上海移动"、"上海联通"的关键词数据，并自动生成包含平均值计算的Excel报告。

## ✨ 主要功能

- **百度指数收集**：自动收集搜索指数和资讯指数数据
- **微信指数收集**：支持网页版和手动辅助收集模式
- **自动截图**：收集数据时自动保存页面截图
- **Excel报告**：自动生成包含平均值计算的Excel报告
- **定时任务**：支持定时自动收集（每周五或周一）
- **图形界面**：提供友好的图形用户界面

## 🛠️ 技术架构

### 核心组件

1. **baidu_collector.py** - 百度指数数据收集器
2. **wechat_collector.py** - 微信指数数据收集器
3. **data_processor.py** - 数据处理和Excel报告生成
4. **scheduler.py** - 定时任务调度系统
5. **main.py** - 图形用户界面主程序
6. **config.py** - 配置文件

### 技术栈

- **Python 3.8+** - 主要编程语言
- **Selenium** - Web自动化测试工具
- **Pandas** - 数据处理和分析
- **OpenPyXL** - Excel文件操作
- **Schedule** - 定时任务调度
- **Tkinter** - 图形用户界面

## 📦 安装说明

### 1. 环境要求

- Python 3.8 或更高版本
- Chrome浏览器（推荐最新版本）
- 操作系统：Windows / macOS / Linux

### 2. 安装依赖

```bash
# 克隆或下载项目文件
cd /mnt/okcomputer/output/index_collector

# 安装Python依赖
pip install -r requirements.txt

# 安装Chrome WebDriver（或使用webdriver-manager自动管理）
# Windows: 下载chromedriver.exe并添加到PATH
# macOS/Linux: brew install chromedriver
```

### 3. 目录结构

```
index_collector/
├── main.py                 # 主程序入口（GUI）
├── scheduler.py            # 定时任务调度
├── baidu_collector.py      # 百度指数收集器
├── wechat_collector.py     # 微信指数收集器
├── data_processor.py       # 数据处理工具
├── config.py               # 配置文件
├── requirements.txt        # 依赖包列表
├── README.md               # 使用说明
├── screenshots/            # 截图保存目录
├── data/                   # Excel报告保存目录
└── logs/                   # 日志文件目录
```

## 🚀 使用说明

### 方式一：图形界面（推荐）

```bash
# 运行主程序
python main.py
```

界面功能：
- **手动收集数据**：立即执行一次数据收集
- **启动定时任务**：开启自动定时收集（每周五或周一）
- **生成Excel报告**：生成包含平均值计算的报告
- **查看截图**：打开截图保存目录

### 方式二：命令行模式

```bash
# 手动运行一次数据收集
python scheduler.py --mode manual

# 启动定时调度器（后台运行）
python scheduler.py --mode schedule

# 使用无浏览器模式（服务器环境）
python scheduler.py --mode manual --headless
```

### 方式三：Python脚本调用

```python
from baidu_collector import BaiduIndexCollector
from wechat_collector import WechatIndexCollector
from data_processor import DataProcessor
from config import get_collection_dates

# 获取收集日期
start_date, end_date = get_collection_dates()

# 收集百度指数
baidu_collector = BaiduIndexCollector(headless=True)
baidu_data = baidu_collector.collect_baidu_index_data(start_date, end_date)

# 收集微信指数
wechat_collector = WechatIndexCollector(headless=True)
wechat_data = wechat_collector.collect_wechat_index_data(start_date, end_date)

# 处理数据
processor = DataProcessor()
processor.process_baidu_data(baidu_data)
processor.process_wechat_data(wechat_data)

# 生成报告
output_path = f"运营商指数报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
processor.generate_excel_report(output_path)
```

## ⚙️ 配置说明

### 配置文件（config.py）

#### 关键词配置
```python
KEYWORDS = {
    'baidu': ['上海电信', '上海移动', '上海联通'],
    'wechat': ['上海电信', '上海移动', '上海联通']
}
```

#### 时间配置
```python
COLLECTION_DAYS = 7  # 收集7天数据
COLLECTION_HOUR = 9  # 每天9点开始收集
```

#### 浏览器配置
```python
BROWSER_CONFIG = {
    'headless': False,  # 是否无浏览器模式
    'window_size': '1920,1080',
    'timeout': 30,
    'user_agent': '...'
}
```

#### Excel模板配置
```python
EXCEL_TEMPLATE = {
    '微信指数趋势': {
        'columns': ['日期', '星期', '上海电信每日指数', '每周指数平均值', ...],
        'keywords': ['上海电信', '上海移动', '上海联通']
    }
    # ...
}
```

## 📊 数据收集规则

### 收集周期

- **正常情况**：每周五统计"上周四-本周四"数据
- **数据延迟**：如果周五数据未更新，则周一统计
- **自动判断**：根据当前日期自动计算需要收集的日期范围

### 数据内容

1. **微信指数**
   - 每日指数数据
   - 每周平均值
   - 趋势对比

2. **百度指数**
   - 搜索指数（每日 + 每周平均）
   - 资讯指数（每日 + 每周平均）
   - 趋势对比

3. **截图记录**
   - 百度指数页面截图
   - 微信指数页面截图
   - 带时间戳的文件名

## 🔧 常见问题

### 1. Chrome WebDriver问题

**问题**：`selenium.common.exceptions.SessionNotCreatedException`

**解决**：
- 确保Chrome浏览器已安装
- 下载与Chrome版本匹配的WebDriver
- 或使用webdriver-manager自动管理

```bash
# 安装webdriver-manager
pip install webdriver-manager

# 修改代码（已集成在代码中）
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
```

### 2. 微信指数无法自动获取

**原因**：微信指数主要通过小程序提供，自动化难度较大

**解决方案**：
- 工具提供手动辅助收集模式
- 自动打开提示界面，引导用户手动收集
- 提供截图记录功能

### 3. 百度指数登录问题

**问题**：百度指数需要登录才能查看详细数据

**解决**：
- 首次运行时手动登录
- 保存Cookie供后续使用
- 或使用百度账号自动登录（需要配置）

### 4. 定时任务不执行

**检查项**：
- 系统时间是否正确
- Python进程是否有权限
- 日志文件查看具体错误

## 📈 Excel报告格式

### 工作表结构

1. **微信指数趋势**
   - 日期、星期
   - 各运营商每日指数
   - 每周平均值
   - 趋势对比图

2. **百度指数搜索**
   - 日期、星期
   - 各运营商每日搜索指数
   - 每周平均值
   - 趋势对比图

3. **百度指数资讯**
   - 日期、星期
   - 各运营商每日资讯指数
   - 每周平均值
   - 趋势对比图

4. **数据汇总**
   - 各运营商平均值汇总
   - 平台间对比

### 样式特点

- 标题行蓝色背景，白色字体
- 峰值数据红色标记
- 自动边框和对齐
- 数据可视化图表

## 📝 使用建议

### 首次使用

1. 运行程序前确保Chrome浏览器已安装
2. 首次运行时建议关闭headless模式，观察运行过程
3. 根据提示登录百度指数（如需要）
4. 检查生成的Excel报告格式是否符合要求

### 日常使用

1. **定时模式**：部署在服务器上，设置定时任务自动运行
2. **手动模式**：每周手动运行一次，检查数据准确性
3. **数据备份**：定期备份data目录下的Excel文件

### 扩展建议

- 可以添加邮件通知功能
- 可以集成数据库保存历史数据
- 可以增加数据可视化看板
- 可以扩展其他指数平台

## 🚨 注意事项

1. **遵守规则**：请遵守百度指数和微信指数的使用条款
2. **频率控制**：不要过于频繁地访问，避免被封IP
3. **数据准确性**：定期人工校验数据准确性
4. **隐私保护**：注意保护账号密码等敏感信息

## 📞 技术支持

如有问题，可以：
1. 查看logs目录下的日志文件
2. 检查config.py配置文件
3. 参考README.md中的常见问题

## 📄 更新日志

### v1.0.0 (2025-11-01)
- 初始版本发布
- 支持百度指数自动收集
- 支持微信指数手动辅助收集
- 支持Excel报告生成
- 支持定时任务调度
- 提供图形用户界面

---

**开发者**：AI Assistant  
**版本**：1.0.0  
**更新日期**：2025-11-01  
**许可证**：MIT License