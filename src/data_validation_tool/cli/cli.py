#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据对比工具 - 命令行版本（高级）

支持更多的命令行参数和操作选项
"""

import argparse
import logging
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径，以便导入正常工作
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 使用绝对导入
from data_validation_tool.core.database import get_db_connection
from data_validation_tool.core.query import DataLakeMessageQuery
from data_validation_tool.core.validation import DataValidation
from data_validation_tool.utils.advanced import AdvancedFeatures

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CommandLineTool:
    """命令行工具"""

    def __init__(self):
        self.db_conn = get_db_connection()
        self.data_query = DataLakeMessageQuery()
        self.validator = DataValidation()
        self.advanced = AdvancedFeatures()

    def validate_by_date_range(self, start_date: str, end_date: str, export_format: str = None):
        """
        按日期范围验证

        Args:
            start_date: 开始日期 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)
            end_date: 结束日期
            export_format: 导出格式 ('json' 或 'csv' 或 None)
        """
        try:
            # 解析时间
            if len(start_date) == 10:  # YYYY-MM-DD
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            else:  # YYYY-MM-DD HH:MM:SS
                start_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

            if len(end_date) == 10:  # YYYY-MM-DD
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:  # YYYY-MM-DD HH:MM:SS
                end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

            logger.info(f"已连接数据库，开始查询和验证...")
            logger.info(f"时间范围: {start_dt} ~ {end_dt}")

            # 查询
            records = self.data_query.query_by_biztime_range(start_dt, end_dt)
            if not records:
                logger.warning("未查询到数据")
                return

            # 验证
            logger.info(f"开始验证 {len(records)} 条记录...")
            result = self.validator.validate_records(records)

            # 打印结果
            result.print_summary()
            self.advanced.print_error_analysis(result)

            # 导出
            if export_format:
                self.advanced.export_errors_to_json(result, f'validation_errors.{export_format}')
                self.advanced.export_errors_to_csv(result, f'validation_errors.csv')

        except ValueError as e:
            logger.error(f"日期格式错误: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"验证失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def validate_last_n_days(self, days: int, export_format: str = None):
        """
        验证最近 N 天的数据

        Args:
            days: 天数
            export_format: 导出格式
        """
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)

        logger.info(f"验证最近 {days} 天的数据...")
        self.validate_by_date_range(
            start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            export_format
        )

    def validate_today(self, export_format: str = None):
        """
        验证今天的数据

        Args:
            export_format: 导出格式
        """
        self.validate_last_n_days(1, export_format)

    def validate_this_week(self, export_format: str = None):
        """
        验证本周的数据

        Args:
            export_format: 导出格式
        """
        self.validate_last_n_days(7, export_format)

    def validate_this_month(self, export_format: str = None):
        """
        验证本月的数据

        Args:
            export_format: 导出格式
        """
        self.validate_last_n_days(30, export_format)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MongoDB 数据对比验证工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 按日期范围验证
  python cli.py --start 2024-01-01 --end 2024-01-31
  
  # 按日期时间范围验证并导出为 JSON
  python cli.py --start "2024-01-01 00:00:00" --end "2024-01-31 23:59:59" --export json
  
  # 验证最近 7 天的数据
  python cli.py --last-days 7
  
  # 验证今天的数据并导出
  python cli.py --today --export json
  
  # 验证本周的数据并导出为 CSV
  python cli.py --this-week --export csv
  
  # 验证本月的数据
  python cli.py --this-month
  
  # 增加日志的详细程度
  python cli.py --today -v
        '''
    )

    # 时间范围参数
    time_group = parser.add_argument_group('时间范围选项（选择其一）')
    time_group.add_argument('--start', help='开始日期 (YYYY-MM-DD) 或 日期时间 (YYYY-MM-DD HH:MM:SS)')
    time_group.add_argument('--end', help='结束日期 (YYYY-MM-DD) 或 日期时间 (YYYY-MM-DD HH:MM:SS)')
    time_group.add_argument('--last-days', type=int, help='验证最近 N 天的数据')
    time_group.add_argument('--today', action='store_true', help='验证今天的数据')
    time_group.add_argument('--this-week', action='store_true', help='验证本周的数据')
    time_group.add_argument('--this-month', action='store_true', help='验证本月的数据')

    # 导出参数
    parser.add_argument(
        '--export',
        choices=['json', 'csv'],
        help='导出格式 (json 或 csv)'
    )

    # 日志参数
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='��加日志详细程度'
    )

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 创建工具实例
    tool = CommandLineTool()

    # 连接数据库
    logger.info("正在连接数据库...")
    if not tool.db_conn.connect():
        logger.error("无法连接到数据库")
        sys.exit(1)

    try:
        # 根据参数执行相应操作
        if args.start and args.end:
            tool.validate_by_date_range(args.start, args.end, args.export)
        elif args.last_days:
            tool.validate_last_n_days(args.last_days, args.export)
        elif args.today:
            tool.validate_today(args.export)
        elif args.this_week:
            tool.validate_this_week(args.export)
        elif args.this_month:
            tool.validate_this_month(args.export)
        else:
            parser.print_help()
            sys.exit(1)

    finally:
        tool.db_conn.close()
        logger.info("数据库连接已关闭")


if __name__ == '__main__':
    main()

