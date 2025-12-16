#!/usr/bin/env python3
"""
安装脚本 - 自动检查和安装依赖
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("✅ 需要 Python 3.8 或更高版本")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_chrome():
    """检查Chrome浏览器"""
    chrome_paths = {
        'Windows': [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe')
        ],
        'Darwin': [  # macOS
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/usr/bin/google-chrome',
            '/usr/bin/chromium'
        ],
        'Linux': [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/snap/bin/chromium'
        ]
    }
    
    system = platform.system()
    paths = chrome_paths.get(system, [])
    
    for path in paths:
        if os.path.exists(path):
            print(f"✅ 找到Chrome浏览器: {path}")
            return True
    
    print(f"⚠️ 未找到Chrome浏览器")
    print(f"📥 请下载安装: https://www.google.com/chrome/")
    return False

def check_pip():
    """检查pip是否可用"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
        print("✅ pip可用")
        return True
    except:
        print("❌ pip不可用")
        print("📥 请安装pip: https://pip.pypa.io/en/installation/")
        return False

def install_dependencies():
    """安装依赖包"""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ 未找到requirements.txt文件")
        return False
    
    print("📦 正在安装依赖包...")
    
    try:
        # 升级pip
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print("✅ pip已更新")
        
        # 安装依赖
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖包安装成功")
            return True
        else:
            print("❌ 依赖包安装失败")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 安装过程中出错: {str(e)}")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ['screenshots', 'data', 'logs']
    base_dir = Path(__file__).parent
    
    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ 创建目录: {directory}/")
            except Exception as e:
                print(f"❌ 创建目录失败 {directory}/: {str(e)}")
                return False
        else:
            print(f"✅ 目录已存在: {directory}/")
    
    return True

def check_webdriver():
    """检查WebDriver"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # 尝试自动下载WebDriver
        print("📦 正在检查ChromeDriver...")
        
        # 使用webdriver-manager自动管理
        ChromeDriverManager().install()
        print("✅ ChromeDriver已安装/更新")
        return True
        
    except Exception as e:
        print(f"⚠️ ChromeDriver检查失败: {str(e)}")
        print("ℹ️ 程序将尝试在运行时自动下载")
        return True

def test_imports():
    """测试导入模块"""
    modules = [
        'selenium',
        'pandas',
        'openpyxl',
        'schedule',
        'requests',
        'PIL'
    ]
    
    print("🧪 测试模块导入...")
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - 未安装")
            return False
    
    return True

def check_system():
    """检查系统环境"""
    print("=" * 60)
    print("🔍 系统环境检查")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 检查pip
    if not check_pip():
        return False
    
    # 检查Chrome
    chrome_ok = check_chrome()
    
    # 创建目录
    if not create_directories():
        return False
    
    print("=" * 60)
    return True

def install_all():
    """完整安装流程"""
    print("=" * 60)
    print("📦 开始安装运营商指数数据自动收集工具")
    print("=" * 60)
    
    # 检查系统
    if not check_system():
        print("❌ 系统检查失败，请修复后重新运行")
        return False
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        return False
    
    # 检查WebDriver
    if not check_webdriver():
        print("❌ WebDriver检查失败")
        return False
    
    # 测试导入
    if not test_imports():
        print("❌ 模块导入测试失败")
        return False
    
    print("=" * 60)
    print("✅ 安装完成！")
    print("=" * 60)
    print("\n🚀 快速开始：")
    print("1. 运行图形界面: python main.py")
    print("2. 或运行命令行: python scheduler.py --mode manual")
    print("3. 查看说明文档: 打开 README.md")
    print("\n📖 详细说明：")
    print("- 快速开始指南: 快速开始指南.md")
    print("- 完整文档: README.md")
    print("- 配置文件: config.py")
    print("\n⚙️ 配置建议：")
    print("- 修改关键词: 编辑 config.py 中的 KEYWORDS")
    print("- 修改时间: 编辑 config.py 中的 COLLECTION_HOUR")
    print("- 无浏览器模式: 设置 headless = True")
    print("=" * 60)
    
    return True

def main():
    """主函数"""
    try:
        if install_all():
            print("\n🎉 安装成功！现在可以开始使用工具了。")
        else:
            print("\n💥 安装失败，请根据提示修复问题后重新运行。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 安装过程出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()