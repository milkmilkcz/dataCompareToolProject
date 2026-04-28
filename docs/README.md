# 数据对比工具

## 项目概述

这是一个 MongoDB 数据对比工具，用于：
1. 连接 MongoDB 数据库
2. 根据 bizTime 查询 dataLakeMessage 集合中的数据
3. 验证数据质量（msgHead 不为空、status 为指定值）
4. 根据 msgHead 和 policyNum 关联业务表数据
5. 对比 dataLakeMessage 中的 body 与业务表数据是否一致

## 项目结构

```
├── config.py              # 配置文件（数据库连接、常量定义等）
├── database.py            # 数据库连接模块（单例模式）
├── query.py               # 数据查询模块
├── validation.py          # 数据验证和对比模块
├── main.py                # 主程序入口
├── .env.example           # 环境变量示例
├── requirements.txt       # Python 依赖
└── README.md              # 本文件
```

## 安装依赖

```bash
# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置

1. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 根据需要修改 `.env` 中的配置：
   - `MONGODB_URI`: MongoDB 连接字符串
   - `DATABASE_NAME`: 数据库名称
   - `LOG_LEVEL`: 日志级别

## 使用方法

### 方式1：交互式运行

```bash
python main.py
```

程序会提示：
- 输入开始时间（格式：YYYY-MM-DD HH:MM:SS）
- 输入结束时间（格式：YYYY-MM-DD HH:MM:SS）
- 自动查询该时间范围内的数据并进行验证

### 方式2：编程方式使用

```python
from main import DataComparisonTool

# 创建工具实例
tool = DataComparisonTool()
tool.db_conn.connect()

# 执行验证
result = tool.validate_by_time_range('2024-01-01 00:00:00', '2024-01-31 23:59:59')

# 查看结果
print(result.get_summary())

# 关闭连接
tool.db_conn.close()
```

## 验证规则

### 1. 基础字段验证
- **msgHead**: 不能为空
- **status**: 必须等于配置值（默认为 2）

### 2. 数据关联验证
- 使用 msgHead 作为业务表名称
- 使用 policyNum 在业务表中查询对应数据

### 3. 深度数据对比
- 对比 dataLakeMessage.body 与业务表数据
- 检查是否存在字段缺失或值不匹配

## 输出说明

验证完成后，会显示：
- 总记录数
- 有效记录数
- 错误记录数
- 错误记录的详细信息（包括错误原因、保单号、业务表等）

## 核心类说明

### DatabaseConnection
单例模式的数据库连接管理器
- `connect()`: 连接数据库
- `get_collection(name)`: 获取集合
- `close()`: 关闭连接

### DataLakeMessageQuery
dataLakeMessage 集合查��接口
- `query_by_biztime_range(start, end)`: 按时间范围查询
- `query_by_biztime_exact(biztime)`: 按确切时间查询
- `query_by_policy_num(num)`: 按保单号查询

### BusinessTableQuery
业务表查询接口
- `query_by_policy_num(table_name, policy_num)`: 按保单号查询

### DataValidation
数据验证和对比核心类
- `validate_record(record)`: 验证单��记录
- `validate_records(records)`: 验证多条记录
- `validate_by_biztime_range(start, end)`: 按时间范围验证

### ValidationResult
验证结果容器
- `add_valid(record)`: 添加有效记录
- `add_error(record, reason)`: 添加错误记录
- `get_summary()`: 获取摘要
- `print_summary()`: 打印摘要

## 扩展功能

### 1. 添加更多验证规则

在 `ValidationResult` 类中添加新的验证方法：

```python
def validate_custom_field(self, record):
    """自定义验证"""
    value = record.get('customField')
    if not value:
        return False, "customField 为空"
    return True, None
```

### 2. 批量导出错误数据

```python
import json

result = tool.validate_by_time_range(start_time, end_time)
with open('errors.json', 'w', encoding='utf-8') as f:
    json.dump(result.error_records, f, ensure_ascii=False, indent=2)
```

### 3. 自定义数据对比规则

在 `DataValidation` 类中修改 `deep_compare_data` 方法，添加自定义比对逻辑。

## 常见问题

### Q: 连接 MongoDB 失败怎么办？
A: 检查：
1. MongoDB URI 是否正确
2. 网络连接是否正常
3. 防火墙是否允许连接

### Q: 找不到业务表数据怎么办？
A: 检查：
1. msgHead 对应的表是否存在
2. policyNum 是否正确
3. 业务表中是否真的没有该保单数据

### Q: 如何修改状态检查值？
A: 在 `config.py` 中修改 `REQUIRED_STATUS` 常量。

## 日志

程序会在控制台输出详细的日志信息，包括：
- 数据库连接状态
- 查询结果摘要
- 验证过程中的每一步
- 错误详情

可以通过 `.env` 中的 `LOG_LEVEL` 调整日志详细程度。

## 许可证

MIT

