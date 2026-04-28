"""
Jenkins 集成模块

提供 Jenkins 友好的运行方式：
- 正确的 exit codes
- 结构化的输出
- JUnit XML 格式���告
- 构建结果汇总
"""

import json
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
from typing import Dict, Any, List
from ..core.validation import ValidationResult

logger = logging.getLogger(__name__)


class JenkinsReporter:
    """Jenkins 报告生成器"""

    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'status': 'UNKNOWN',
            'total_records': 0,
            'valid_records': 0,
            'error_records': 0,
            'error_details': []
        }

    def add_validation_result(self, result: ValidationResult):
        """添加验证结果"""
        summary = result.get_summary()
        self.results['total_records'] = summary['total']
        self.results['valid_records'] = summary['valid_count']
        self.results['error_records'] = summary['error_count']

        # 添加错误详情
        for error_item in result.error_records:
            record = error_item['record']
            self.results['error_details'].append({
                'policyNum': str(record.get('policyNum', 'N/A')),
                'msgHead': str(record.get('msgHead', 'N/A')),
                'bizTime': str(record.get('bizTime', 'N/A')),
                'status': str(record.get('status', 'N/A')),
                'error_reason': error_item['error_reason']
            })

        # 确定状态
        if self.results['error_records'] > 0:
            self.results['status'] = 'FAILURE'
        else:
            self.results['status'] = 'SUCCESS'

    def export_json(self, filename: str) -> bool:
        """导出为 JSON 格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            logger.info(f"Jenkins 报告已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"导出 JSON 失败: {e}")
            return False

    def export_junit_xml(self, filename: str) -> bool:
        """
        导出为 JUnit XML 格式（Jenkins 原生支持）

        JUnit XML 格式便于 Jenkins 解析测试结果
        """
        try:
            # 创建根元素
            testsuite = ET.Element('testsuite')
            testsuite.set('name', 'DataValidation')
            testsuite.set('tests', str(self.results['total_records']))
            testsuite.set('failures', str(self.results['error_records']))
            testsuite.set('timestamp', self.results['timestamp'])

            # 添加有效记录
            if self.results['valid_records'] > 0:
                testcase = ET.SubElement(testsuite, 'testcase')
                testcase.set('name', f"Valid Records ({self.results['valid_records']})")
                testcase.set('classname', 'ValidationTest')

            # 添加错误记录
            for i, error in enumerate(self.results['error_details'], 1):
                testcase = ET.SubElement(testsuite, 'testcase')
                testcase.set('name', f"Record {i}: {error['policyNum']}")
                testcase.set('classname', 'ValidationTest')

                # 添加失败信息
                failure = ET.SubElement(testcase, 'failure')
                failure.set('type', 'ValidationError')
                failure.text = (
                    f"Policy: {error['policyNum']}\n"
                    f"Table: {error['msgHead']}\n"
                    f"Reason: {error['error_reason']}"
                )

            # 保存 XML
            tree = ET.ElementTree(testsuite)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            logger.info(f"JUnit XML 报告已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"导出 JUnit XML 失败: {e}")
            return False

    def print_jenkins_summary(self):
        """打印 Jenkins 友好的摘要"""
        print("\n" + "="*70)
        print("JENKINS BUILD SUMMARY")
        print("="*70)
        print(f"Timestamp:     {self.results['timestamp']}")
        print(f"Status:        {self.results['status']}")
        print(f"Total Records: {self.results['total_records']}")
        print(f"Valid Records: {self.results['valid_records']}")
        print(f"Failed Records:{self.results['error_records']}")

        if self.results['error_records'] > 0:
            print("\nFailure Details:")
            print("-" * 70)
            for i, error in enumerate(self.results['error_details'][:10], 1):  # 只显示前 10 个
                print(f"  {i}. Policy: {error['policyNum']}")
                print(f"     Table:  {error['msgHead']}")
                print(f"     Reason: {error['error_reason']}")

            if len(self.results['error_details']) > 10:
                print(f"  ... and {len(self.results['error_details']) - 10} more errors")

        print("="*70 + "\n")

    def get_exit_code(self) -> int:
        """
        获取退出码

        Returns:
            0: 成功（所有数据都有效）
            1: 验证失败（有错误数据）
            2: 执行错误（异常）
        """
        if self.results['status'] == 'SUCCESS':
            return 0
        elif self.results['status'] == 'FAILURE':
            return 1
        else:
            return 2


def create_junit_report(result: ValidationResult, filename: str = 'test-results.xml'):
    """
    快捷函数：创建 JUnit 格式的测试报告

    Args:
        result: ValidationResult 对象
        filename: 输出文件名

    Returns:
        exit code
    """
    reporter = JenkinsReporter()
    reporter.add_validation_result(result)
    reporter.export_junit_xml(filename)
    reporter.print_jenkins_summary()
    return reporter.get_exit_code()

