# 快速开始指南

## 项目文件结构

```
PyCharmMiscProject/
├── config.py                    # 配置管理（数据库连接、常量）
├── database.py                  # MongoDB 连接管理（单例模式）
├── query.py                     # 数据查询模块
├── validation.py                # 数据验证和对比核心逻辑
├── main.py                      # 程序入口
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量示例
├── README.md                    # 完整文档
├── AGENTS.md                    # AI 代理指南
└── QUICKSTART.md                # 本文件
```

## 快速开始（3步）

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置连接
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env（如需要修改数据库连接）
```

### 3. 运行程序
```bash
python main.py
```

## 核心工作流

程序执行流程：
1. 输入查询时间范围（example: `2024-01-01 00:00:00`）
2. 程序从 dataLakeMessage 集合查询该时间范围内的所有数据
3. 对每条数据进行验证：
   - ✓ msgHead 不为空
   - ✓ status 等于 2
   - ✓ 根据 msgHead 找到对应业务表
   - ✓ 根据 policyNum 查询业务表数据
   - ✓ 对比 dataLakeMessage.body 与业务表数据
4. 输出验证结果：valid_count, error_count，以及所有错误详情

## 数据模型示例

### DataLakeMessage 数据示例
```json
{
  "_id": "...",
  "msgHead": "PolicyTable",        // 业务表名称
  "policyNum": "POL-2024-001",     // 保单号
  "status": 2,                     // 状态（必须为2）
  "bizTime": "2024-01-15 10:30:00",// 业务时间
  "body": {
    "policyId": "123",
    "premium": 5000,
    "startDate": "2024-01-01"
  }
}
```

### 业务表数据示例
```json
{
  "_id": "...",
  "policyNum": "POL-2024-001",
  "policyId": "123",
  "premium": 5000,
  "startDate": "2024-01-01"
}
```

对比结果：完全一致 ✓

## 常用编程操作

### 只查询不验证

```python
from core.query import DataLakeMessageQuery, BusinessTableQuery

datalake_query = DataLakeMessageQuery()
records = datalake_query.query_by_biztime_range('2024-01-01 00:00:00', '2024-01-31 23:59:59')
print(f"查询到 {len(records)} 条记录")
```

### 对特定记录进行验证
```python
from validation import DataValidation

validator = DataValidation()
record = records[0]  # 取第一条记录
result = validator.validate_record(record)
print(result.get_summary())
```

### 导出错误数据到文件
```python
import json
from main import DataComparisonTool

tool = DataComparisonTool()
tool.db_conn.connect()
result = tool.validate_by_time_range('2024-01-01 00:00:00', '2024-01-31 23:59:59')

# 导出错误
with open('validation_errors.json', 'w', encoding='utf-8') as f:
    json.dump(result.error_records, f, ensure_ascii=False, indent=2, default=str)

tool.db_conn.close()
```

## 修改验证规则

### 修改 status 检查值
编辑 `config.py`：
```python
REQUIRED_STATUS = 2  # 改成需要的值
```

### 添加新的验证规则
编辑 `validation.py`，在 `DataValidation` 类中添加：
```python
def validate_new_field(self, record):
    """验证新字段"""
    value = record.get('newField')
    if not value:
        return False, "newField 为空"
    return True, None
```

然后在 `validate_basic_fields()` 中调用。

## 常见错误处理

### "无法连接到数据库"
- 检查 MongoDB URI 是否正确
- 检查网络连接
- 检查防火墙设置

### "msgHead 对应的业务表不存在"
- 验证 msgHead 值是否正确
- 检查业务表是否存在于数据库中

### "policyNum 在业务表中不存在"
- 检查 policyNum 是否正确
- 检查业务表中的数据

## 调试技巧

### 增加日志详细度
编辑 `.env`：
```
LOG_LEVEL=DEBUG
```

### 查看原始 SQL/查询
在 `query.py` 中的各个查询方法中添加打印：
```python
print(f"执行查询: {query}")
```

## 下一步

- 查看 `README.md` 了解完整文档
- 查看 `AGENTS.md` 了解架构细节
- 查看各个 Python 文件的详细注释

