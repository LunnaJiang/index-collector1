#!/usr/bin/env python3
"""
环境测试脚本 - 检查是否可以正常运行
"""

import sys
import os
from pathlib import Path

def test_basic_imports():
    """测试基础模块导入"""
    print("🔍 测试基础模块导入...")
    
    required_modules = [
        'sys', 'os', 'datetime', 'logging', 'pathlib'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - 导入失败")
            return False
    
    return True

def test_project_structure():
    """测试项目结构"""
    print("\n🔍 检查项目结构...")
    
    base_dir = Path(__file__).parent
    
    # 检查必需的文件
    required_files = [
        'config.py',
        'baidu_collector.py',
        'wechat_collector.py',
        'data_processor.py',
        'scheduler.py',
        'main.py',
        'requirements.txt',
        'README.md',
        '快速开始指南.md'
    ]
    
    for file in required_files:
        file_path = base_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            return False
    
    # 检查目录
    required_dirs = ['screenshots', 'data', 'logs']
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"⚠️ {dir_name}/ 目录不存在（将自动创建）")
    
    return True

def test_config_import():
    """测试配置文件导入"""
    print("\n🔍 测试配置文件...")
    
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, str(Path(__file__).parent))
        
        import config
        
        # 检查基本配置
        if hasattr(config, 'KEYWORDS'):
            print(f"✅ KEYWORDS配置: {len(config.KEYWORDS)} 个平台")
        else:
            print("❌ KEYWORDS配置缺失")
            return False
        
        if hasattr(config, 'COLLECTION_HOUR'):
            print(f"✅ COLLECTION_HOUR: {config.COLLECTION_HOUR}")
        else:
            print("❌ COLLECTION_HOUR配置缺失")
            return False
        
        # 测试函数
        if hasattr(config, 'get_collection_dates'):
            start_date, end_date = config.get_collection_dates()
            print(f"✅ 日期计算功能正常: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
        else:
            print("❌ 日期计算功能缺失")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件测试失败: {str(e)}")
        return False

def test_optional_dependencies():
    """测试可选依赖"""
    print("\n🔍 测试可选依赖...")
    
    optional_modules = [
        ('selenium', 'Web自动化'),
        ('pandas', '数据处理'),
        ('openpyxl', 'Excel操作'),
        ('schedule', '定时任务'),
        ('requests', '网络请求'),
        ('PIL', '图像处理')
    ]
    
    all_good = True
    
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"⚠️ {module} - {description} - 未安装")
            all_good = False
    
    if not all_good:
        print("\n💡 提示：运行 install.py 自动安装依赖")
    
    return True

def test_directory_creation():
    """测试目录创建"""
    print("\n🔍 测试目录创建...")
    
    base_dir = Path(__file__).parent
    test_dirs = ['screenshots', 'data', 'logs']
    
    for dir_name in test_dirs:
        dir_path = base_dir / dir_name
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {dir_name}/ 目录可写")
        except Exception as e:
            print(f"❌ {dir_name}/ 目录创建失败: {str(e)}")
            return False
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 运营商指数数据自动收集工具 - 环境测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("基础模块导入", test_basic_imports),
        ("项目结构检查", test_project_structure),
        ("配置文件测试", test_config_import),
        ("可选依赖测试", test_optional_dependencies),
        ("目录创建测试", test_directory_creation)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 环境测试通过！可以开始使用工具了。")
        print("\n🚀 快速开始：")
        print("1. 图形界面: python main.py")
        print("2. 命令行: python scheduler.py --mode manual")
        print("3. 安装依赖: python install.py")
        print("4. 查看文档: README.md")
    else:
        print("⚠️ 环境测试未完全通过，但基础功能可用。")
        print("\n🔧 建议：")
        print("1. 运行 python install.py 安装依赖")
        print("2. 查看快速开始指南.md")
        print("3. 检查错误信息并修复")
    
    print("=" * 60)

if __name__ == '__main__':
    main()