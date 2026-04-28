"""
高级功能模块

提供高级功能，如：
- 批量验证和导出
- 统计分析
- 数据修复建议
"""

import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any
from ..core.validation import DataValidation, ValidationResult

logger = logging.getLogger(__name__)


class AdvancedFeatures:
    """高级功能类"""

    def __init__(self):
        self.validator = DataValidation()

    def export_errors_to_json(self, result: ValidationResult, filename: str):
        """
        导出错误记录到 JSON 文件

        Args:
            result: ValidationResult 对象
            filename: 输出文件名
        """
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'summary': result.get_summary(),
                'errors': []
            }

            # 序列化错误记录
            for error_item in result.error_records:
                record = error_item['record']
                export_data['errors'].append({
                    'policyNum': record.get('policyNum'),
                    'msgHead': record.get('msgHead'),
                    'bizTime': str(record.get('bizTime')),
                    'status': record.get('status'),
                    'error_reason': error_item['error_reason']
                })

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"错误记录已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"导出 JSON 失败: {e}")
            return False

    def export_errors_to_csv(self, result: ValidationResult, filename: str):
        """
        导出错误记录到 CSV 文件

        Args:
            result: ValidationResult 对象
            filename: 输出文件名
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['policyNum', 'msgHead', 'bizTime', 'status', 'error_reason']
                )
                writer.writeheader()

                for error_item in result.error_records:
                    record = error_item['record']
                    writer.writerow({
                        'policyNum': record.get('policyNum'),
                        'msgHead': record.get('msgHead'),
                        'bizTime': str(record.get('bizTime')),
                        'status': record.get('status'),
                        'error_reason': error_item['error_reason']
                    })

            logger.info(f"错误记录已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"导出 CSV 失败: {e}")
            return False

    def export_summary_to_json(self, result: ValidationResult, filename: str):
        """
        导出验证摘要到 JSON 文件

        Args:
            result: ValidationResult 对象
            filename: 输出文件名
        """
        try:
            summary = result.get_summary()
            summary['export_time'] = datetime.now().isoformat()

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            logger.info(f"验证摘要已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"导出摘要失败: {e}")
            return False

    def analyze_error_types(self, result: ValidationResult) -> Dict[str, int]:
        """
        分析错误类型分布

        Args:
            result: ValidationResult 对象

        Returns:
            错误类型统计字典
        """
        error_types = {}

        for error_item in result.error_records:
            error_reason = error_item['error_reason']

            # 基于错误信息分类
            if 'msgHead' in error_reason and '为空' in error_reason:
                error_type = 'msgHead_empty'
            elif 'status' in error_reason:
                error_type = 'status_invalid'
            elif '未查询到' in error_reason:
                error_type = 'business_data_not_found'
            elif '数据对比失败' in error_reason:
                error_type = 'data_mismatch'
            elif 'body' in error_reason:
                error_type = 'body_format_error'
            elif 'policyNum' in error_reason:
                error_type = 'policy_num_error'
            else:
                error_type = 'other'

            error_types[error_type] = error_types.get(error_type, 0) + 1

        return error_types

    def print_error_analysis(self, result: ValidationResult):
        """
        打印错误分析报告

        Args:
            result: ValidationResult 对象
        """
        error_types = self.analyze_error_types(result)

        print("\n" + "="*50)
        print("错误类型分析")
        print("="*50)

        if not error_types:
            print("✓ 未发现错误")
            return

        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(result.error_records)) * 100
            print(f"{error_type}: {count} ({percentage:.1f}%)")

        print("="*50)

    def get_error_statistics(self, result: ValidationResult) -> Dict[str, Any]:
        """
        获取详细的错误统计

        Args:
            result: ValidationResult 对象

        Returns:
            统计字典
        """
        error_types = self.analyze_error_types(result)

        return {
            'total_records': len(result.valid_records) + len(result.error_records),
            'valid_records': len(result.valid_records),
            'error_records': len(result.error_records),
            'error_rate': (len(result.error_records) / (len(result.valid_records) + len(result.error_records))) * 100 if (len(result.valid_records) + len(result.error_records)) > 0 else 0,
            'error_types': error_types
        }

    def batch_validate_and_export(self, records: List[Dict], output_prefix: str = 'validation_result'):
        """
        批量验证并导出结果

        Args:
            records: 记录列表
            output_prefix: 输出文件前缀

        Returns:
            ValidationResult 对象
        """
        logger.info(f"开始批量验证 {len(records)} 条记录...")

        # 验证
        result = self.validator.validate_records(records)

        # 导出
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = f"{output_prefix}_{timestamp}.json"
        csv_file = f"{output_prefix}_{timestamp}.csv"
        summary_file = f"{output_prefix}_summary_{timestamp}.json"

        self.export_errors_to_json(result, json_file)
        self.export_errors_to_csv(result, csv_file)
        self.export_summary_to_json(result, summary_file)

        logger.info(f"批量验证完成，已生成 3 个结果文件")

        return result


# 便捷函数
def export_validation_result(result: ValidationResult, format: str = 'json', filename: str = None):
    """
    导出验证结果

    Args:
        result: ValidationResult 对象
        format: 格式 'json' 或 'csv'
        filename: 文件名，如为 None 则自动生成

    Returns:
        是否成功
    """
    advanced = AdvancedFeatures()

    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'validation_errors_{timestamp}.{format}'

    if format == 'json':
        return advanced.export_errors_to_json(result, filename)
    elif format == 'csv':
        return advanced.export_errors_to_csv(result, filename)
    else:
        logger.error(f"不支持的格式: {format}")
        return False

