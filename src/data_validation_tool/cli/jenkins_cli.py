#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据对比工具 - Jenkins 专用版本

支持 Jenkins Pipeline 的运行方式，包括：
- 正确的 exit codes
- JUnit XML 输出
- JSON 报告生成
- 构建日志兼容
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
from data_validation_tool.utils.jenkins_reporter import JenkinsReporter

# 配置日志（Jenkins 兼容格式）
log_format = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format
)

logger = logging.getLogger(__name__)


class JenkinsDataComparisonTool:
    """Jenkins 数据对比工具"""

    def __init__(self, output_dir: str = None):
        self.db_conn = get_db_connection()
        self.data_query = DataLakeMessageQuery()
        self.validator = DataValidation()
        self.advanced = AdvancedFeatures()
        self.reporter = JenkinsReporter()
        self.output_dir = output_dir or '.'

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

    def validate_and_report(self, start_date: str, end_date: str,
                           export_json: bool = False,
                           export_csv: bool = False,
                           export_junit: bool = False) -> int:
        """
        执行验证并生成报告

        Args:
            start_date: 开始日期
            end_date: 结束日期
            export_json: 导出 JSON
            export_csv: 导出 CSV
            export_junit: 导出 JUnit XML

        Returns:
            exit code (0=success, 1=failure, 2=error)
        """
        try:
            # 解析时间
            try:
                if len(start_date) == 10:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                else:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

                if len(end_date) == 10:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                else:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                logger.error(f"时间格式错误: {e}")
                return 2

            logger.info(f"验证范围: {start_dt} ~ {end_dt}")

            # 查询数据
            records = self.data_query.query_by_biztime_range(start_dt, end_dt)
            if not records:
                logger.warning("未查询到数据")
                self.reporter.results['status'] = 'NO_DATA'
                return 0

            # 验证数据
            logger.info(f"开始验证 {len(records)} 条记录...")
            result = self.validator.validate_records(records)

            # 添加验证结果到报告
            self.reporter.add_validation_result(result)

            # 打印摘要
            result.print_summary()
            self.advanced.print_error_analysis(result)
            self.reporter.print_jenkins_summary()

            # 生成报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if export_junit:
                junit_file = os.path.join(self.output_dir, f'test-results-{timestamp}.xml')
                self.reporter.export_junit_xml(junit_file)

            if export_json:
                json_file = os.path.join(self.output_dir, f'validation-report-{timestamp}.json')
                self.reporter.export_json(json_file)

                errors_file = os.path.join(self.output_dir, f'validation-errors-{timestamp}.json')
                self.advanced.export_errors_to_json(result, errors_file)

            if export_csv:
                csv_file = os.path.join(self.output_dir, f'validation-errors-{timestamp}.csv')
                self.advanced.export_errors_to_csv(result, csv_file)

            # 返回退出码
            return self.reporter.get_exit_code()

        except Exception as e:
            logger.exception(f"执行异常: {e}")
            return 2

    def validate_last_n_days(self, days: int,
                            export_json: bool = False,
                            export_csv: bool = False,
                            export_junit: bool = False) -> int:
        """验证最近 N 天的数据"""
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=days)
        logger.info(f"验证最近 {days} 天的数据...")
        return self.validate_and_report(
            start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            export_json, export_csv, export_junit
        )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Jenkins 数据对比验证工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Jenkins Pipeline 示例用法:

  # 验证今天的数据，并导出 JUnit XML
  python jenkins_cli.py --today --export-junit --export-json

  # 验证最近 7 天的数据
  python jenkins_cli.py --last-days 7 --export-junit --export-csv

  # 按日期范围验证并生成所有报告
  python jenkins_cli.py --start 2024-01-01 --end 2024-01-31 \\
      --export-junit --export-json --export-csv --output build/reports

自动退出码:
  0 - 成功，数据验证通过
  1 - 验证失败，有错误数据
  2 - 执行错误或异常发生
        '''
    )

    # 时间范围参数
    time_group = parser.add_argument_group('时间范围（选择其一）')
    time_group.add_argument('--start', help='开始日期 (YYYY-MM-DD 或 HH:MM:SS)')
    time_group.add_argument('--end', help='结束日期')
    time_group.add_argument('--last-days', type=int, help='最近 N 天')
    time_group.add_argument('--today', action='store_true', help='今天的数据')
    time_group.add_argument('--this-week', action='store_true', help='本周的数据')
    time_group.add_argument('--this-month', action='store_true', help='本月的数据')

    # 输出参数
    output_group = parser.add_argument_group('输出选项')
    output_group.add_argument('--export-json', action='store_true', help='导出 JSON 报告')
    output_group.add_argument('--export-csv', action='store_true', help='导出 CSV 报告')
    output_group.add_argument('--export-junit', action='store_true', help='导出 JUnit XML（Jenkins 原生支持）')
    output_group.add_argument('--export-all', action='store_true', help='导出所有格式')
    output_group.add_argument('--output', default='.', help='输出目录（默认：当前目录）')

    # 日志参数
    parser.add_argument('-v', '--verbose', action='store_true', help='详细日志')
    parser.add_argument('--log-file', help='日志文件路径')

    args = parser.parse_args()

    # 设置日志
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

    # 创建工具
    tool = JenkinsDataComparisonTool(output_dir=args.output)

    # 连接数据库
    logger.info("正在连接数据库...")
    if not tool.db_conn.connect():
        logger.error("数据库连接失败")
        sys.exit(2)

    # 处理导出选项
    export_json = args.export_json or args.export_all
    export_csv = args.export_csv or args.export_all
    export_junit = args.export_junit or args.export_all

    try:
        exit_code = 2  # 默认错误

        # 根据参数执行
        if args.start and args.end:
            exit_code = tool.validate_and_report(
                args.start, args.end,
                export_json, export_csv, export_junit
            )
        elif args.last_days:
            exit_code = tool.validate_last_n_days(
                args.last_days,
                export_json, export_csv, export_junit
            )
        elif args.today:
            exit_code = tool.validate_last_n_days(
                1, export_json, export_csv, export_junit
            )
        elif args.this_week:
            exit_code = tool.validate_last_n_days(
                7, export_json, export_csv, export_junit
            )
        elif args.this_month:
            exit_code = tool.validate_last_n_days(
                30, export_json, export_csv, export_junit
            )
        else:
            parser.print_help()
            exit_code = 2

        logger.info(f"执行完成，退出码: {exit_code}")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("用户中断")
        sys.exit(2)
    except Exception as e:
        logger.exception(f"未预期的错误: {e}")
        sys.exit(2)
    finally:
        tool.db_conn.close()


if __name__ == '__main__':
    main()

