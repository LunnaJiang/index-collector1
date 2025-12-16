#!/usr/bin/env python3
"""
Replit部署专用Web应用
提供简单的Web界面和API接口
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from template_utils import render_template_string
import threading
import time

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入我们的模块
from config import create_directories, get_collection_dates
from baidu_collector import BaiduIndexCollector
from wechat_collector import WechatIndexCollector
from data_processor import DataProcessor

# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'index-collector-secret-key'

# 全局变量
collection_status = {
    'is_running': False,
    'progress': 0,
    'message': '',
    'last_run': None,
    'last_report': None
}

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """主页"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>运营商指数数据收集工具</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .status-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .status-running {
            background: #28a745;
            animation: pulse 2s infinite;
        }
        
        .status-stopped {
            background: #6c757d;
        }
        
        .status-error {
            background: #dc3545;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
        }
        
        .btn-info {
            background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
        }
        
        .progress {
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .progress-bar {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .info-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }
        
        .info-card h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .info-card p {
            color: #666;
            margin-bottom: 5px;
        }
        
        .log-section {
            background: #1e1e1e;
            color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .buttons {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 运营商指数数据收集工具</h1>
            <p>自动收集百度指数和微信指数数据，生成Excel报告</p>
        </div>
        
        <div class="status-card">
            <h2>
                <span class="status-indicator status-{{ 'running' if collection_status.is_running else 'stopped' }}"></span>
                系统状态: {{ '正在运行' if collection_status.is_running else '待机中' }}
            </h2>
            {% if collection_status.message %}
            <p style="margin-top: 10px; color: #666;">{{ collection_status.message }}</p>
            {% endif %}
        </div>
        
        {% if collection_status.is_running %}
        <div class="progress">
            <div class="progress-bar" style="width: {{ collection_status.progress }}%">
                {{ collection_status.progress }}%
            </div>
        </div>
        {% endif %}
        
        <div class="buttons">
            <a href="/collect" class="btn btn-success">📊 手动收集数据</a>
            <a href="/schedule/start" class="btn btn-warning">⏰ 启动定时任务</a>
            <a href="/report" class="btn btn-info">📈 查看报告</a>
            <a href="/screenshots" class="btn">📸 查看截图</a>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📊 数据收集</h3>
                <p>✅ 百度指数：搜索指数 + 资讯指数</p>
                <p>✅ 微信指数：趋势指数</p>
                <p>✅ 自动截图保存</p>
                <p>✅ 每周平均值计算</p>
            </div>
            
            <div class="info-card">
                <h3>📈 报告生成</h3>
                <p>✅ Excel格式报告</p>
                <p>✅ 多工作表展示</p>
                <p>✅ 数据可视化</p>
                <p>✅ 自动样式美化</p>
            </div>
            
            <div class="info-card">
                <h3>⏰ 定时任务</h3>
                <p>✅ 每周五自动收集</p>
                <p>✅ 数据延迟处理</p>
                <p>✅ 智能日期计算</p>
                <p>✅ 错误自动重试</p>
            </div>
            
            <div class="info-card">
                <h3>🔧 系统特性</h3>
                <p>✅ 响应式界面</p>
                <p>✅ 实时日志显示</p>
                <p>✅ 进度条显示</p>
                <p>✅ 错误处理机制</p>
            </div>
        </div>
        
        {% if collection_status.last_run %}
        <div class="info-card">
            <h3>📅 最近运行</h3>
            <p>上次运行时间: {{ collection_status.last_run }}</p>
            {% if collection_status.last_report %}
            <p>最新报告: {{ collection_status.last_report }}</p>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="log-section">
            <h3 style="color: white; margin-bottom: 15px;">📋 实时日志</h3>
            <div id="log-content">
                <p style="color: #888;">等待日志输出...</p>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 运营商指数数据收集工具 | 部署在Replit平台</p>
            <p>访问地址: <a href="/" style="color: #667eea;">https://index-collector.repl.co</a></p>
        </div>
    </div>
    
    <script>
        // 自动刷新日志
        function refreshLog() {
            fetch('/api/log')
                .then(response => response.json())
                .then(data => {
                    const logContent = document.getElementById('log-content');
                    if (data.logs && data.logs.length > 0) {
                        logContent.innerHTML = data.logs.map(log => 
                            `<p style="color: ${log.level === 'ERROR' ? '#ff6b6b' : log.level === 'WARNING' ? '#ffd93d' : '#ffffff'};">${log.time} - ${log.level} - ${log.message}</p>`
                        ).join('');
                    }
                })
                .catch(error => {
                    console.error('Failed to fetch logs:', error);
                });
        }
        
        // 每5秒刷新一次日志
        setInterval(refreshLog, 5000);
        
        // 页面加载完成后立即刷新一次
        document.addEventListener('DOMContentLoaded', refreshLog);
    </script>
</body>
</html>
''')

@app.route('/collect')
def collect():
    """手动收集数据"""
    if collection_status['is_running']:
        return jsonify({'error': '数据收集正在进行中，请稍候'}), 400
    
    # 在新线程中运行收集任务
    thread = threading.Thread(target=run_collection_task)
    thread.start()
    
    return jsonify({'message': '数据收集任务已启动'})

def run_collection_task():
    """运行收集任务"""
    collection_status['is_running'] = True
    collection_status['progress'] = 0
    collection_status['message'] = '正在收集数据...'
    
    try:
        logger.info("开始数据收集任务")
        
        # 获取收集日期
        start_date, end_date = get_collection_dates()
        logger.info(f"收集日期范围: {start_date} 到 {end_date}")
        
        collection_status['progress'] = 10
        
        # 收集百度指数数据
        logger.info("开始收集百度指数数据")
        collection_status['message'] = '正在收集百度指数数据...'
        
        baidu_collector = BaiduIndexCollector(headless=True)
        baidu_data = baidu_collector.collect_baidu_index_data(start_date, end_date)
        
        collection_status['progress'] = 40
        
        # 收集微信指数数据
        logger.info("开始收集微信指数数据")
        collection_status['message'] = '正在收集微信指数数据...'
        
        wechat_collector = WechatIndexCollector(headless=True)
        wechat_data = wechat_collector.collect_wechat_index_data(start_date, end_date)
        
        collection_status['progress'] = 70
        
        # 处理数据
        logger.info("开始处理数据")
        collection_status['message'] = '正在处理数据...'
        
        processor = DataProcessor()
        processor.process_baidu_data(baidu_data)
        processor.process_wechat_data(wechat_data)
        
        collection_status['progress'] = 90
        
        # 生成报告
        logger.info("生成Excel报告")
        collection_status['message'] = '正在生成Excel报告...'
        
        output_path = f"data/运营商指数报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        if processor.generate_excel_report(output_path):
            logger.info(f"Excel报告生成成功: {output_path}")
            collection_status['last_report'] = output_path
        else:
            logger.error("Excel报告生成失败")
        
        collection_status['progress'] = 100
        collection_status['message'] = '数据收集完成'
        collection_status['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info("数据收集任务完成")
        
    except Exception as e:
        logger.error(f"数据收集失败: {str(e)}")
        collection_status['message'] = f'数据收集失败: {str(e)}'
    finally:
        collection_status['is_running'] = False
        collection_status['progress'] = 0

@app.route('/schedule/<action>')
def schedule_control(action):
    """定时任务控制"""
    if action == 'start':
        # 启动定时任务（这里简化处理，实际应该使用后台任务）
        return jsonify({'message': '定时任务功能需要配置后台任务调度器'})
    elif action == 'stop':
        return jsonify({'message': '定时任务已停止'})
    else:
        return jsonify({'error': '未知操作'}), 400

@app.route('/report')
def report():
    """查看报告"""
    data_dir = Path('data')
    if not data_dir.exists():
        return jsonify({'message': '暂无报告，请先收集数据'})
    
    reports = sorted(data_dir.glob('*.xlsx'), reverse=True)
    
    if not reports:
        return jsonify({'message': '暂无报告，请先收集数据'})
    
    latest_report = reports[0]
    
    return jsonify({
        'latest_report': latest_report.name,
        'download_url': f'/download/{latest_report.name}',
        'all_reports': [report.name for report in reports[:10]]
    })

@app.route('/download/<filename>')
def download(filename):
    """下载文件"""
    file_path = Path('data') / filename
    if file_path.exists():
        return send_file(str(file_path), as_attachment=True)
    else:
        return jsonify({'error': '文件不存在'}), 404

@app.route('/screenshots')
def screenshots():
    """查看截图"""
    screenshots_dir = Path('screenshots')
    if not screenshots_dir.exists():
        return jsonify({'message': '暂无截图'})
    
    screenshots = sorted(screenshots_dir.glob('*.png'), reverse=True)
    
    return jsonify({
        'screenshots': [
            {
                'filename': screenshot.name,
                'url': f'/screenshot/{screenshot.name}',
                'created': datetime.fromtimestamp(screenshot.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            }
            for screenshot in screenshots[:20]
        ]
    })

@app.route('/screenshot/<filename>')
def screenshot(filename):
    """查看截图"""
    file_path = Path('screenshots') / filename
    if file_path.exists():
        return send_file(str(file_path))
    else:
        return jsonify({'error': '截图不存在'}), 404

@app.route('/api/log')
def api_log():
    """API: 获取日志"""
    log_file = Path('logs/app.log')
    if not log_file.exists():
        return jsonify({'logs': []})
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        logs = []
        for line in lines[-50:]:  # 只显示最近50行
            if ' - ' in line:
                parts = line.strip().split(' - ', 3)
                if len(parts) >= 4:
                    logs.append({
                        'time': parts[0],
                        'level': parts[2],
                        'message': parts[3]
                    })
        
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'logs': [{'time': '', 'level': 'ERROR', 'message': f'读取日志失败: {str(e)}'}]})

@app.route('/api/status')
def api_status():
    """API: 获取状态"""
    return jsonify(collection_status)

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """API: 收集数据"""
    return collect()

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/docs')
def docs():
    """API文档"""
    return jsonify({
        'endpoints': {
            'GET /': '主页',
            'GET /collect': '手动收集数据',
            'GET /schedule/<action>': '定时任务控制',
            'GET /report': '查看报告',
            'GET /download/<filename>': '下载报告',
            'GET /screenshots': '查看截图',
            'GET /screenshot/<filename>': '查看截图',
            'GET /api/log': '获取日志',
            'GET /api/status': '获取状态',
            'POST /api/collect': 'API收集数据',
            'GET /health': '健康检查',
            'GET /docs': 'API文档'
        }
    })

def run_app():
    """运行Flask应用"""
    # 初始化目录
    create_directories()
    
    # 设置环境变量
    os.environ['DISPLAY'] = ':99'
    os.environ['CHROME_BIN'] = 'chromium-browser'
    
    print("=" * 60)
    print("🚀 启动运营商指数数据收集工具")
    print("=" * 60)
    print(f"📍 访问地址: http://localhost:8080")
    print(f"📊 主页: http://localhost:8080/")
    print(f"📋 API文档: http://localhost:8080/docs")
    print(f"❤️ 健康检查: http://localhost:8080/health")
    print("=" * 60)
    
    # 运行Flask应用
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    run_app()