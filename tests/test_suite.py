"""
测试和演示模块

这个文件主要用于：
1. 演示各个模块的使用方法
2. 进行单元测试
3. 快速调试
"""

import logging
import sys
import os
from datetime import datetime, timedelta

# 添加 src 目录到 Python 路径，以便导入包
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_database_connection():
    """测试数据库连接"""
    print("\n" + "="*50)
    print("测试 1: 数据库连接")
    print("="*50)

    from data_validation_tool.core.database import get_db_connection

    try:
        conn = get_db_connection()
        if conn.connect():
            print("✓ 数据库连接成功")
            conn.close()
            return True
        else:
            print("✗ 数据库连接失败")
            return False
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False


def test_query_by_biztime():
    """测试按 bizTime 查询"""
    print("\n" + "="*50)
    print("测试 2: 按 bizTime 查询")
    print("="*50)

    from data_validation_tool.core.database import get_db_connection
    from data_validation_tool.core.query import DataLakeMessageQuery

    try:
        conn = get_db_connection()
        conn.connect()

        query = DataLakeMessageQuery()

        # 查询最近 7 天的数据，确保能找到数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)

        print(f"查询范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        records = query.query_by_biztime_range(start_time, end_time)

        if records:
            print(f"✓ 查询到 {len(records)} 条数据")
            # 显示第一条数据的摘要
            first_record = records[0]
            print(f"\n第一条数据摘要:")
            print(f"  - msgHead: {first_record.get('msgHead')}")
            print(f"  - policyNum: {first_record.get('policyNum')}")
            print(f"  - status: {first_record.get('status')}")
            print(f"  - bizTime: {first_record.get('bizTime')}")
            return True
        else:
            print("✗ 未查询到数据")
            return False

    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


def test_validation():
    """测试验证功能"""
    print("\n" + "="*50)
    print("测试 3: 数据验证")
    print("="*50)

    from data_validation_tool.core.database import get_db_connection
    from data_validation_tool.core.query import DataLakeMessageQuery
    from data_validation_tool.core.validation import DataValidation

    try:
        conn = get_db_connection()
        conn.connect()

        query = DataLakeMessageQuery()
        validator = DataValidation()

        # 查询最近 7 天的数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)

        records = query.query_by_biztime_range(start_time, end_time)

        if not records:
            print("✗ 未查询到数据，无法进行验证")
            return False

        # 验证前 5 条记录（或全部，如果少于 5 条）
        test_records = records[:min(5, len(records))]
        print(f"测试验证前 {len(test_records)} 条记录...")

        valid_count = 0
        error_count = 0

        for i, record in enumerate(test_records, 1):
            result = validator.validate_record(record)
            if result.valid_records:
                valid_count += 1
                print(f"  ✓ 记录 #{i} 验证通过")
            else:
                error_count += 1
                error_info = result.error_records[0]
                print(f"  ✗ 记录 #{i} 验证失败: {error_info['error_reason']}")

        print(f"\n验证结果摘要:")
        print(f"  有效: {valid_count}")
        print(f"  错误: {error_count}")

        return error_count == 0

    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("开始运行测试套件")
    print("="*70)

    tests = [
        ("数据库连接", test_database_connection),
        ("按 bizTime 查询", test_query_by_biztime),
        ("数据验证", test_validation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 '{test_name}' 发生异常: {e}")
            results.append((test_name, False))

    # 打印总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n总体: {passed}/{total} 测试通过")
    print("="*70 + "\n")


if __name__ == '__main__':
    # 运行所有测试
    run_all_tests()

    # 或者运行单个测试，取消注释对应行：
    # test_database_connection()
    # test_query_by_biztime()
    # test_validation()
