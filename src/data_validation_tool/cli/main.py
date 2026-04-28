import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径，以便导入正常工作
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 使用绝对导入
from data_validation_tool.core.database import get_db_connection
from data_validation_tool.core.validation import DataValidation
from data_validation_tool.utils.local_reporter import create_local_report

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DataComparisonTool:
    """数据对比工具主类"""

    def __init__(self):
        self.validator = DataValidation()
        self.db_conn = get_db_connection()

    def validate_by_time_range(self, start_time, end_time):
        """
        按时间范围进行数据验证

        Args:
            start_time: 开始时间 (格式: YYYY-MM-DD HH:MM:SS)
            end_time: 结束时间 (格式: YYYY-MM-DD HH:MM:SS)

        Returns:
            验证结果
        """
        logger.info(f"开始按时间范围验证数据: {start_time} ~ {end_time}")
        result = self.validator.validate_by_biztime_range(start_time, end_time)
        return result

    def print_error_details(self, result):
        """打印错误详情"""
        if result.error_records:
            print("\n" + "="*50)
            print("错误记录详情")
            print("="*50)
            for i, error_item in enumerate(result.error_records, 1):
                print(f"\n错误 #{i}:")
                print(f"  错误原因: {error_item['error_reason']}")
                record = error_item['record']
                print(f"  保单号: {record.get('policyNum')}")
                print(f"  业务表: {record.get('msgHead')}")
                print(f"  业务时间: {record.get('bizTime')}")


def main():
    """主函数"""

    # 环境选择
    print("\n" + "="*50)
    print("数据对比工具 - 环境选择")
    print("="*50)
    print("请选择要连接的数据库环境:")
    print("  sit - SIT测试环境")
    print("  qa  - QA测试环境")
    print()

    while True:
        env_input = input("请选择环境 (sit/qa): ").strip().lower()
        if env_input in ['sit', 'qa']:
            break
        print("无效输入，请输入 'sit' 或 'qa'")

    # 设置环境变量
    os.environ['ENVIRONMENT'] = env_input

    # 重新导入配置以使用新环境
    import importlib
    import data_validation_tool.core.config as config_module
    importlib.reload(config_module)

    # 强制重新创建数据库连接实例
    import data_validation_tool.core.database as db_module
    importlib.reload(db_module)

    print(f"\n已选择环境: {env_input.upper()}")
    print(f"数据库: {config_module.DATABASE_NAME}")
    print(f"连接串: {config_module.MONGODB_URI[:50]}...")
    print()

    tool = DataComparisonTool()

    # 连接数据库
    if not tool.db_conn.connect():
        logger.error("无法连接到数据库，程序退出")
        sys.exit(1)

    try:
        # 交互式输入
        print("\n" + "="*50)
        print("数据对比工具")
        print("="*50)
        print("请输入查询时间范围 (格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 或 ISO格式)\n")

        # 输入开始时间
        start_input = input("开始时间 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 或 ISO格式): ").strip()

        # 输入结束时间
        end_input = input("结束时间 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 或 ISO格式): ").strip()

        # 验证时间格式并转换为标准格式
        try:
            # 定义多种时间格式
            time_formats = [
                '%Y-%m-%d',                          # 2026-04-24
                '%Y-%m-%d %H:%M:%S',                 # 2026-04-24 13:28:11
                '%Y-%m-%dT%H:%M:%S.%f%z',           # 2026-04-24T13:28:11.946+00:00
                '%Y-%m-%dT%H:%M:%S.%fZ',            # 2026-04-24T13:28:31.491Z
                '%Y-%m-%dT%H:%M:%SZ',                # 2026-04-24T13:28:31Z
                '%Y-%m-%dT%H:%M:%S.%f',             # 2026-04-24T13:28:31.491
                '%Y-%m-%dT%H:%M:%S',                 # 2026-04-24T13:28:31
            ]

            def parse_input_time(time_str):
                """解析用户输入的时间字符串"""
                for fmt in time_formats:
                    try:
                        parsed_dt = datetime.strptime(time_str, fmt)
                        return parsed_dt, fmt
                    except ValueError:
                        continue
                raise ValueError(f"无法解析时间格式: {time_str}")

            # 解析开始时间
            start_dt, start_fmt = parse_input_time(start_input)

            # 解析结束时间
            end_dt, end_fmt = parse_input_time(end_input)

            # 验证时间逻辑
            if start_dt > end_dt:
                logger.error("开始时间不能晚于结束时间")
                sys.exit(1)

            # 转换为ISO 8601格式（与数据库一致，保留毫秒和T分隔符）
            # 若用户只输入日期，则补全为当天起止时间
            if start_fmt == '%Y-%m-%d':
                start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            if end_fmt == '%Y-%m-%d':
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999000)

            # 生成ISO格式字符串，带毫秒和Z（假���数据库为UTC）
            def to_iso(dt):
                # 若无tzinfo，假定为本地时间，转为UTC（如有需要可根据实际情况调整）
                if dt.tzinfo is None:
                    return dt.isoformat(timespec='milliseconds') + 'Z'
                return dt.isoformat(timespec='milliseconds')

            start_time = to_iso(start_dt)
            end_time = to_iso(end_dt)

            print(f"查询时间范围: {start_time} ~ {end_time}")

        except ValueError as e:
            logger.error(f"时间格式错误: {e}")
            logger.error("支持的格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 或 ISO格式")
            sys.exit(1)

        # 执行验证
        result = tool.validate_by_time_range(start_time, end_time)

        # 打印错误详情
        if result.error_records:
            tool.print_error_details(result)

        print("\n验证完成！")

        # 生成本地报告
        reports_dir = os.path.join(project_root, 'reports')
        if create_local_report(result, env_input, start_time, end_time, reports_dir):
            print(f"多种格式的报告已生成并保存到: {reports_dir}")
        else:
            print("报���生成失败，请检查日志")

    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.exception(f"程序异常: {e}")
    finally:
        tool.db_conn.close()


if __name__ == '__main__':
    main()
