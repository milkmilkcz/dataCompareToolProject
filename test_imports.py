#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入测试脚本

验证重构后的包结构和导入是否正常工作
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有重要模块的导入"""
    print("🔍 测试包结构和导入...")
    print("=" * 50)

    tests = [
        ("主包", "import data_validation_tool"),
        ("核心模块", "from data_validation_tool.core import config, database, query, validation"),
        ("CLI 模块", "from data_validation_tool.cli import main, cli, jenkins_cli"),
        ("工具模块", "from data_validation_tool.utils import advanced, jenkins_reporter"),
        ("测试模块", "from tests.test_suite import test_database_connection"),
    ]

    passed = 0
    total = len(tests)

    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}: 导入成功")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: 导入失败 - {e}")

    print("=" * 50)
    print(f"📊 导入测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有导入测试通过！包结构正确。")
        return True
    else:
        print("⚠️  部分导入失败，请检查包结构。")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🔧 测试基本功能...")
    print("=" * 50)

    try:
        from data_validation_tool.core.config import REQUIRED_STATUS
        print(f"✅ 配置加载成功: REQUIRED_STATUS = {REQUIRED_STATUS}")

        from data_validation_tool.core.database import DatabaseConnection
        print("✅ 数据库类导入成功")

        from data_validation_tool.core.query import DataLakeMessageQuery
        print("✅ 查询类导入成功")

        from data_validation_tool.core.validation import DataValidation, ValidationResult
        print("✅ 验证类导入成功")

        print("🎉 基本功能测试通过！")
        return True

    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 数据对比验证工具 - 导入和功能测试")
    print("=" * 60)

    # 测试导入
    imports_ok = test_imports()

    if imports_ok:
        # 测试基本功能
        functionality_ok = test_basic_functionality()

        if functionality_ok:
            print("\n" + "=" * 60)
            print("🎊 所有测试通过！项目重构成功！")
            print("=" * 60)
            print("\n📋 现在你可以：")
            print("  • ��行测试: python tests/test_suite.py")
            print("  • 安装包: pip install -e .")
            print("  • 运行工具: python -m data_validation_tool.cli.main")
            print("  • Jenkins 集成: python -m data_validation_tool.cli.jenkins_cli --today")
            sys.exit(0)
        else:
            print("\n❌ 功能测试失败")
            sys.exit(1)
    else:
        print("\n❌ 导入测试失败")
        sys.exit(1)
