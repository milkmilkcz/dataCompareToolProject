import logging
import json
from .config import REQUIRED_STATUS
from .query import DataLakeMessageQuery

logger = logging.getLogger(__name__)


class ValidationResult:
    """验证结果类"""

    def __init__(self):
        self.valid_records = []
        self.error_records = []
        self.skipped_records = []  # 跳过验证的记录（版本不匹配等）

    def add_valid(self, record):
        """添加有效记录"""
        self.valid_records.append(record)

    def add_error(self, record, error_reason):
        """添加错误记录"""
        self.error_records.append({
            'record': record,
            'error_reason': error_reason
        })

    def add_skipped(self, record, skip_reason):
        """添加跳过验证的记录"""
        self.skipped_records.append({
            'record': record,
            'skip_reason': skip_reason
        })

    def get_summary(self):
        """获取验证摘要"""
        return {
            'total': len(self.valid_records) + len(self.error_records) + len(self.skipped_records),
            'valid_count': len(self.valid_records),
            'error_count': len(self.error_records),
            'skipped_count': len(self.skipped_records),
            'valid_records': self.valid_records,
            'error_records': self.error_records,
            'skipped_records': self.skipped_records
        }

    def print_summary(self):
        """打印验证摘要"""
        summary = self.get_summary()
        print("\n" + "="*50)
        print("数据验证结果摘要")
        print("="*50)
        print(f"总记录数: {summary['total']}")
        print(f"有效记录: {summary['valid_count']}")
        print(f"错误记录: {summary['error_count']}")
        print(f"跳过验证: {summary['skipped_count']}")
        print("="*50)


class DataValidation:
    """数据验证模块"""

    def __init__(self):
        self.datalake_query = DataLakeMessageQuery()
        # 缓存已加载的JSON schema，避免重复加载
        self._schema_cache = {}

    def validate_msg_head(self, record):
        """
        验证 msgHead 不能为空

        Returns:
            (是否有效, 错误信息)
        """
        msg_head = record.get('msgHead')
        if not msg_head:
            return False, f"msgHead 为空"
        return True, None

    def validate_status(self, record):
        """
        验证 status 必须为指定值
        Returns:
            (是否有效, 错误信息)
        """
        status = record.get('status')

        if status is None:
            return False, "status 不能为空"

        if isinstance(status, str):
            if not status.isdigit():
                return False, f"status 值非法（非数字字符串）: {status}"
            status = int(status)

        if not isinstance(status, int):
            return False, f"status 类型错误，期望 int，实际为 {type(status).__name__}"

        if status != REQUIRED_STATUS:
            return False, f"status 值为 {status}，期望值为 {REQUIRED_STATUS}"

        return True, None

    def validate_basic_fields(self, record):
        """
        验证基础字段

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        # 验证 msgHead
        valid, error = self.validate_msg_head(record)
        if not valid:
            errors.append(error)

        # 验证 status
        valid, error = self.validate_status(record)
        if not valid:
            errors.append(error)

        return len(errors) == 0, errors

    def validate_record(self, record):
        """
        验证单条记录

        Args:
            record: dataLakeMessage 中的记录

        Returns:
            ValidationResult 对象
        """
        result = ValidationResult()

        # 第1步：验证基础字段
        basic_valid, basic_errors = self.validate_basic_fields(record)
        if not basic_valid:
            error_msg = "; ".join(basic_errors)
            result.add_error(record, f"基础字段验证失败: {error_msg}")
            return result

        # 第2步：获取业务表名
        msg_head = record.get('msgHead')

        # 第3步：加载对应的JSON schema
        schema = self._load_json_schema(msg_head)
        if schema is None:
            result.add_error(record, f"无法加载 '{msg_head}' 对应的JSON schema")
            return result

        # schema 只取一级 key
        if isinstance(schema, dict) and msg_head in schema:
            schema = schema[msg_head]
        else:
            result.add_error(record, f"JSON schema 文件中未找到一级 key '{msg_head}'")
            return result

        # 第4步：获取 body 数据
        datalake_body = record.get('body', {})
        if not isinstance(datalake_body, dict):
            try:
                datalake_body = json.loads(datalake_body) if isinstance(datalake_body, str) else {}
            except:
                result.add_error(record, "body 字段格式错误，无法解析")
                return result

        # 第5步：验证key是否存在
        keys_valid, error_msg = self._validate_keys_exist(datalake_body, schema)
        if not keys_valid:
            result.add_error(record, f"字段验证失败: {error_msg}")
        else:
            result.add_valid(record)

        return result

    def validate_records(self, records):
        """
        验证多条记录

        按 msgHead 分组处理，每组内的记录都验证key是否存在

        Args:
            records: 记录列表

        Returns:
            ValidationResult 对象
        """
        final_result = ValidationResult()

        # 第1步：按 msgHead 分组
        grouped_records = {}
        for record in records:
            msg_head = record.get('msgHead', '')
            group_key = msg_head

            if group_key not in grouped_records:
                grouped_records[group_key] = []
            grouped_records[group_key].append(record)

        total_groups = len(grouped_records)
        logger.info(f"共发现 {total_groups} 个记录组")

        # 第2步：处理每个组
        for i, (group_key, group_records) in enumerate(grouped_records.items(), 1):
            print(f"[进度] 处理记录组 {i}/{total_groups}: {group_key} (包含 {len(group_records)} 条记录)")

            for j, record in enumerate(group_records, 1):
                print(f"[进度] 验证记录 {j}/{len(group_records)}: {record.get('policyNum', 'N/A')}")
                record_result = self.validate_record(record)
                final_result.valid_records.extend(record_result.valid_records)
                final_result.error_records.extend(record_result.error_records)
                final_result.skipped_records.extend(record_result.skipped_records)
            print(f"[进度] 组 {group_key} 完成: 验证{len(group_records)}个")

        print(f"[进度] 验证完成，共处理 {total_groups} 个记录组")
        return final_result

    def validate_by_biztime_range(self, start_biztime, end_biztime):
        """
        按 bizTime 范围验证数据

        Args:
            start_biztime: 开始时间
            end_biztime: 结束时间

        Returns:
            ValidationResult 对象
        """
        # 查询数据
        records = self.datalake_query.query_by_biztime_range(start_biztime, end_biztime)

        if not records:
            logger.warning(f"未查询到时间范围内的数据")
            result = ValidationResult()
            result.print_summary()
            return result

        # 验证数据
        result = self.validate_records(records)
        result.print_summary()
        return result

    # 可以忽略的字段（审计 / 系统字段）
    IGNORE_FIELDS = {
        "id",
        "_id",
    }

    def _load_json_schema(self, msg_head):
        """
        加载对应msgHead的JSON schema

        Args:
            msg_head: 消息头，如 "agreement"

        Returns:
            JSON schema dict 或 None
        """
        # 检查缓存
        if msg_head in self._schema_cache:
            return self._schema_cache[msg_head]

        json_path = f"C:\\Users\\chenleo\\PyCharmMiscProject\\JSON\\{msg_head}.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
                # 缓存加载的schema
                self._schema_cache[msg_head] = schema
                return schema
        except FileNotFoundError:
            logger.error(f"未找到对应的JSON文件: {json_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON文件解析失败: {json_path}, 错误: {e}")
            return None

    def _validate_keys_exist(self, data, schema, path=""):
        """
        递归验证data中的所有key是否在schema中存在

        Args:
            data: dataLakeMessage的body数据
            schema: JSON schema
            path: 当前路径，用于错误信息

        Returns:
            (是否通过, 错误信息)
        """
        if not isinstance(data, dict):
            return True, None  # 非dict类型跳过

        if not isinstance(schema, dict):
            return True, None  # schema不是dict，跳过

        for key, value in data.items():
            if key in self.IGNORE_FIELDS:
                continue

            full_path = f"{path}.{key}" if path else key

            if key not in schema:
                return False, f"字段 '{full_path}' 在schema中不存在"

            # 递归检查嵌套结构
            if isinstance(value, dict) and isinstance(schema[key], dict):
                result, error = self._validate_keys_exist(value, schema[key], full_path)
                if not result:
                    return False, error
            elif isinstance(value, list) and isinstance(schema[key], list) and schema[key]:
                # 如果是list，检查每个元素
                if not value:  # 空list跳过
                    continue
                # 假设schema[key]是[element_schema]的形式
                element_schema = schema[key][0] if schema[key] else {}
                for i, item in enumerate(value):
                    if isinstance(item, dict) and isinstance(element_schema, dict):
                        result, error = self._validate_keys_exist(item, element_schema, f"{full_path}[{i}]")
                        if not result:
                            return False, error

        return True, None
