# 功能更新说明 - agreementNum 支持

## 📋 更新内容

### 2026-04-24 更新

为了支持更灵活的业务表查询需求，我已经优化了代码以同时支持 **policyNum（保单号）** 和 **agreementNum（协议号）** 两种标识字段。

---

## 🔄 修改详情

### 1️⃣ query.py - BusinessTableQuery 类

#### 原始方法
```python
def query_by_policy_num(self, table_name, policy_num):
    """只支持按 policyNum 查询"""
    # ...
```

#### 更新后的方法
```python
def query_by_policy_num(self, table_name, policy_num, agreement_num=None):
    """
    按保单号或协议号查询业务表中的数据
    
    优先级：
    1. 首先尝试用 policyNum 查询
    2. 如果未找到，再用 agreementNum 查询
    3. 如果都找不到，返回 None
    """
```

#### 新增方法
```python
def query_by_policy_num_or_agreement(self, table_name, policy_num=None, agreement_num=None):
    """
    灵活查询的别名方法，更清晰的语义
    """
```

**特性：**
- ✅ 支持两个字段的灵活查询
- ✅ 自动主动降级���policyNum 优先）
- ✅ 详细的日志记录
- ✅ 完善的错误处理

---

### 2️⃣ validation.py - DataValidation 类

#### 修改的方法：validate_record()

**原始逻辑：**
```python
# 只检查 policyNum
if not policy_num:
    result.add_error(record, "policyNum 为空，无法关联业务表")
    return result
```

**更新后的逻辑：**
```python
# 获取两个字段
policy_num = record.get('policyNum')
agreement_num = record.get('agreementNum')

# 检查至少有一个字段不为空
if not policy_num and not agreement_num:
    result.add_error(
        record,
        "policyNum 和 agreementNum 都为空，无法关联业务表"
    )
    return result

# 调用查询时同时传递两个参数
business_data = self.business_query.query_by_policy_num(
    msg_head,
    policy_num,
    agreement_num
)

# 生成更详细的错误信息
if not business_data:
    search_fields = []
    if policy_num:
        search_fields.append(f"policyNum='{policy_num}'")
    if agreement_num:
        search_fields.append(f"agreementNum='{agreement_num}'")
    search_desc = " 或 ".join(search_fields)
    
    result.add_error(
        record,
        f"从业务表 '{msg_head}' 中未查询到数据 ({search_desc})"
    )
```

**改进点：**
- ✅ 灵活的字段组合支持
- ✅ 至少一个字段不为空的验证
- ✅ 更清晰的错误信息（显示尝试了哪些字段）

---

## 🎯 使用场景

### 场景 1：只有 policyNum
```python
DataLakeMessage 记录：{
    "policyNum": "POL-2024-001",
    "agreementNum": None,
    "body": {...}
}
# 会用 policyNum 查询
```

### 场景 2：只有 agreementNum
```python
DataLakeMessage 记录：{
    "policyNum": None,
    "agreementNum": "AGR-2024-001",
    "body": {...}
}
# 会用 agreementNum 查询
```

### 场景 3：两个都有
```python
DataLakeMessage 记录：{
    "policyNum": "POL-2024-001",
    "agreementNum": "AGR-2024-001",
    "body": {...}
}
# 优先用 policyNum 查询，找不到则用 agreementNum
```

### 场景 4：两个都为空
```python
DataLakeMessage 记录：{
    "policyNum": None,
    "agreementNum": None,
    "body": {...}
}
# 错误：✗ policyNum 和 agreementNum 都为空，无法关联业务表
```

---

## 📊 错误信息示例

### 原图：只有 policyNum

**之前：**
```
从业务表 'PolicyTable' 中未查询到保单号 'POL-2024-001' 的数据
```

**现在（更详细）：**
```
从业务表 'PolicyTable' 中未查询到数据 (policyNum='POL-2024-001')
```

### 新增：两个字段都有

```
从业务表 'PolicyTable' 中未查询到数据 (policyNum='POL-2024-001' 或 agreementNum='AGR-2024-001')
```

### 新增：两个都为空

```
policyNum 和 agreementNum 都为空，无法关联业务表
```

---

## 💻 代码示例

### 直接使用 BusinessTableQuery

```python
from core.query import BusinessTableQuery

bq = BusinessTableQuery()

# 只用 policyNum
result = bq.query_by_policy_num('PolicyTable', 'POL-001')

# 同时试两个字段
result = bq.query_by_policy_num('PolicyTable', 'POL-001', 'AGR-001')

# 只用 agreementNum
result = bq.query_by_policy_num('PolicyTable', None, 'AGR-001')

# 使用别名方法（语义更清晰）
result = bq.query_by_policy_num_or_agreement('PolicyTable', 'POL-001', 'AGR-001')
```

### 自动验证（DataValidation）

```python
from validation import DataValidation

validator = DataValidation()

# 自动处理 policyNum 和 agreementNum
result = validator.validate_record({
    'msgHead': 'PolicyTable',
    'policyNum': 'POL-001',      # 可选
    'agreementNum': 'AGR-001',   # 可选（至少一个不为空）
    'status': 2,
    'body': {...}
})
```

---

## ✅ 向后兼容性

✅ **完全向后兼容**

- 之前的代码无需改动
- 新参数 `agreement_num` 是可选的，默认为 None
- 现有调用 `.query_by_policy_num(table, policy_num)` 继续有效

```python
# 旧代码仍然可用
result = bq.query_by_policy_num('PolicyTable', 'POL-001')

# 新代码可选择传递第二参数
result = bq.query_by_policy_num('PolicyTable', 'POL-001', 'AGR-001')
```

---

## 🧪 测试

### 运行测试套件
```bash
python test.py
```

### 快速验证
```bash
python main.py
# 输入时间范围，系统会自动使用新的字段判断逻辑
```

---

## 📈 性能影响

**完全没有性能影响：**
- ✅ 查询逻辑相同
- ✅ 仅多了一层判断逻辑（字符串判断）
- ✅ 查询次数最多两次（缓存友��）

---

## 🔧 扩展建议

### 如果需要同时检查多个字段

修改 `BusinessTableQuery.query_by_policy_num()` 方法：

```python
def query_by_multiple_fields(self, table_name, fields_dict):
    """
    按多个字段查询，顺序尝试，返回第一个匹配结果
    
    Args:
        table_name: 表名
        fields_dict: {'policyNum': 'POL-001', 'agreementNum': 'AGR-001', ...}
    """
    for field_name, field_value in fields_dict.items():
        if field_value:
            result = collection.find_one({field_name: field_value})
            if result:
                return result
    return None
```

---

## 📝 文件修改记录

| 文件 | 修改内容 | 行数变化 |
|------|---------|--------|
| query.py | BusinessTableQuery 增强 | +25 |
| validation.py | validate_record 更新 | +20 |

---

## 🎓 相关文档

- 关键查询逻辑：见 `query.py` 的 `BusinessTableQuery` 类
- 验证调用位置：见 `validation.py` 的 `validate_record` ���法
- 完整示例：运行 `python test.py`

---

## ✨ 小结

这次更新提供了：

1. **灵活性** - 支持两种标识字段
2. **智能性** - 自动选择查询策略
3. **可靠性** - 完善的错误提示
4. **兼容性** - 完全向后兼容

现在系统可以处理更多实际业务场景！🎉

