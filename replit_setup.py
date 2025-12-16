#!/usr/bin/env python3
"""
Replit部署专用设置脚本
"""

import os
import subprocess
import sys
from pathlib import Path

def setup_replit_environment():
    """设置Replit环境"""
    print("🚀 正在设置Replit环境...")
    
    # 1. 安装Chrome
    print("📦 安装Chrome浏览器...")
    try:
        subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
        subprocess.run(['apt', 'install', '-y', 'chromium-browser'], check=True, capture_output=True)
        print("✅ Chrome安装成功")
    except Exception as e:
        print(f"⚠️ Chrome安装失败: {str(e)}")
        print("ℹ️ 将使用无浏览器模式")
    
    # 2. 安装Python依赖
    print("📦 安装Python依赖...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        
        requirements_file = Path(__file__).parent / 'requirements.txt'
        if requirements_file.exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                          check=True, capture_output=True)
            print("✅ Python依赖安装成功")
        else:
            print("❌ 未找到requirements.txt")
            return False
    except Exception as e:
        print(f"❌ 依赖安装失败: {str(e)}")
        return False
    
    # 3. 创建必要的目录
    print("📁 创建目录...")
    directories = ['screenshots', 'data', 'logs']
    base_dir = Path(__file__).parent
    
    for directory in directories:
        dir_path = base_dir / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {directory}/")
        except Exception as e:
            print(f"❌ 创建目录失败 {directory}/: {str(e)}")
            return False
    
    # 4. 修改配置文件以适应Replit环境
    print("⚙️ 配置环境...")
    config_file = base_dir / 'config.py'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保headless为True
        if "'headless': False" in content:
            content = content.replace("'headless': False", "'headless': True")
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ 配置文件已更新为无浏览器模式")
        else:
            print("✅ 配置文件已正确设置")
    except Exception as e:
        print(f"⚠️ 配置文件更新失败: {str(e)}")
    
    # 5. 创建启动脚本
    print("📝 创建启动脚本...")
    
    # 创建Web启动脚本
    web_script = '''#!/usr/bin/env python3
"""
Replit Web启动脚本
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置环境变量
os.environ['DISPLAY'] = ':99'
os.environ['CHROME_BIN'] = 'chromium-browser'

print("🚀 启动运营商指数数据收集工具...")
print("=" * 60)
print("📋 可用命令:")
print("1. 运行图形界面: python main.py")
print("2. 运行定时任务: python scheduler.py --mode schedule --headless")
print("3. 手动收集数据: python scheduler.py --mode manual --headless")
print("4. 测试环境: python test_environment.py")
print("=" * 60)

# 如果提供了参数，执行相应命令
if len(sys.argv) > 1:
    if sys.argv[1] == 'main':
        os.system('python main.py')
    elif sys.argv[1] == 'schedule':
        os.system('python scheduler.py --mode schedule --headless')
    elif sys.argv[1] == 'manual':
        os.system('python scheduler.py --mode manual --headless')
    elif sys.argv[1] == 'test':
        os.system('python test_environment.py')
    else:
        print(f"未知命令: {sys.argv[1]}")
        print("可用命令: main, schedule, manual, test")
else:
    print("请使用上面的命令来运行工具")
'''
    
    try:
        with open(base_dir / 'start.py', 'w', encoding='utf-8') as f:
            f.write(web_script)
        os.chmod(base_dir / 'start.py', 0o755)
        print("✅ 启动脚本已创建")
    except Exception as e:
        print(f"❌ 启动脚本创建失败: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Replit环境设置完成！")
    print("=" * 60)
    print("\n📋 使用说明：")
    print("1. 在Replit的Shell中运行: python start.py manual")
    print("2. 或运行图形界面: python main.py")
    print("3. 或启动定时任务: python scheduler.py --mode schedule --headless")
    print("\n📁 输出文件位置：")
    print("- Excel报告: data/目录")
    print("- 截图: screenshots/目录")
    print("- 日志: logs/目录")
    print("\n⚙️ 配置修改：")
    print("- 编辑 config.py 文件修改关键词、时间等设置")
    print("=" * 60)
    
    return True

def create_replit_config():
    """创建.replit配置文件"""
    print("📝 创建Replit配置文件...")
    
    replit_config = '''run = "python start.py"
language = "python3"

[env]
PYTHON_VERSION = "3.8"

[packager]
language = "python3"

[packager.features]
packageSearch = true
guessImports = true

[[ports]]
localPort = 8080
externalPort = 80
'''
    
    try:
        with open('.replit', 'w', encoding='utf-8') as f:
            f.write(replit_config)
        print("✅ .replit配置文件已创建")
    except Exception as e:
        print(f"❌ .replit配置文件创建失败: {str(e)}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Replit部署设置工具")
    print("=" * 60)
    
    try:
        if setup_replit_environment():
            create_replit_config()
            print("\n🎉 所有设置完成！")
            print("\n📌 下一步：")
            print("1. 在Replit中点击'Run'按钮")
            print("2. 或在Shell中运行: python start.py")
            print("3. 查看输出文件在 data/ 目录")
        else:
            print("\n❌ 设置失败，请检查错误信息")
    except Exception as e:
        print(f"\n💥 设置过程出错: {str(e)}")

if __name__ == '__main__':
    main()