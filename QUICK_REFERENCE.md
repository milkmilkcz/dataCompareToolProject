# ⚡ 快速参考卡片

## 文件清单（16个）

### 🔧 核心模块（4个）
```
✓ config.py           - 配置和常量
✓ database.py         - MongoDB 连接管理
✓ query.py            - 数据查询接口
✓ validation.py       - 验证和对比逻辑 ⭐ 核心
```

### 🚀 应用程序（3个）
```
✓ main.py             - 交互式工具（推荐首先使用）
✓ cli.py              - 高级命令行工具
✓ test.py             - 测试套件（用于调试）
```

### 🎁 附加模块（1个）
```
✓ advanced.py         - 批量��理、导出、分析
```

### 📚 文档（5个）
```
✓ README.md           - 完整文档（详细）
✓ QUICKSTART.md       - 快速开始（推荐首先阅读）
✓ FRAMEWORK.md        - 框架详解（深入理解）
✓ AGENTS.md           - AI 代理指南
✓ PROJECT_SUMMARY.md  - 项目总体概览（你��这里）
```

### ⚙️ 配置（2个）
```
✓ requirements.txt    - Python 依赖
✓ .env.example        - 环境变量示例
```

### 🔄 ���文件（1个）
```
✓ script.py           - 原始示例脚本
```

---

## 🎯 3 分钟快速开始

### 1️⃣ 安装（30秒）
```bash
pip install -r requirements.txt
```

### 2️⃣ 配置（30秒）
```bash
cp .env.example .env
# 编辑 .env，输入你的 MongoDB 连接字符串
```

### 3️⃣ 运行（1分钟）
```bash
# 方式 A: 交互式（推荐初学者）
python main.py
# 然后输入时间范围...

# 方式 B: 一行命令
python cli.py --today

# 方式 C: 测试
python test.py
```

---

## 📋 核心功能速览

| 功能 | 文件 | 类/函数 | 用途 |
|------|------|--------|------|
| 数据库连接 | database.py | DatabaseConnection | 管理 MongoDB 连接 |
| 数据查询 | query.py | DataLakeMessageQuery | 查询 dataLakeMessage |
| 业务表查询 | query.py | BusinessTableQuery | 查询关联业务表 |
| 验证逻辑 | validation.py | DataValidation | 执行验证和对比 |
| 结果管理 | validation.py | ValidationResult | 存储和统计结果 |
| 导出功能 | advanced.py | AdvancedFeatures | 导出为 JSON/CSV |
| 交互式工具 | main.py | DataComparisonTool | 命令行交互 |
| 命令行工具 | cli.py | CommandLineTool | 参数式运行 |
| 测试套件 | test.py | 多个测试函数 | 快速验证 |

---

## 🔑 常用命令速查

### 验证今天的数据
```bash
python cli.py --today
```

### 验证最近 7 天的数据
```bash
python cli.py --last-days 7
```

### 按日期范围验证
```bash
python cli.py --start 2024-01-01 --end 2024-01-31
```

### 验证并导出为 JSON
```bash
python cli.py --today --export json
```

### 验证并导出为 CSV
```bash
python cli.py --today --export csv
```

### 交互式验证
```bash
python main.py
```

### 运行测试
```bash
python test.py
```

### 增加日志详细度
```bash
python cli.py --today -v
```

---

## 📊 验证规则一览

| 规则 | 检查 | 失败则 |
|------|------|-------|
| msgHead 检查 | msgHead 不能为空 | ❌ 错误 |
| status 检查 | status 必须 = 2 | ❌ 错误 |
| 业务表查询 | 根据 msgHead 和 policyNum 查询 | 未找到则 ❌ 错误 |
| 数据对比 | body 与业务表数据必须完全一致 | 不一致则 ❌ 错误 |

---

## 🛠️ 常见配置修改

### 修改 status 检查值
编辑 `config.py` 第 15 行：
```python
REQUIRED_STATUS = 2  # 改成你需要的值
```

### 修改日志级别
编辑 `.env`：
```env
LOG_LEVEL=DEBUG     # 改成 DEBUG, INFO, WARNING, ERROR
```

### 修改数据库连接
编辑 `.env`：
```env
MONGODB_URI=你的连接字符串
DATABASE_NAME=你的数据库名
```

---

## 🐛 快速调试

### 测试数据库连接
```bash
python test.py
# 查看第一个测试的结果
```

### 查看某条记录的详情
编辑 `test.py`，运行特定测试：
```python
test_query_by_biztime()  # 查看查询结果
```

### 启用详细日志
```bash
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" && python main.py
```

---

## 💾 输出文件示例

验证完成后会生成：

```
validation_errors_20240124_153045.json
─────────────────────────────
{
  "export_time": "2024-01-24T15:30:45.xxx",
  "summary": {
    "total": 100,
    "valid_count": 95,
    "error_count": 5
  },
  "errors": [
    {
      "policyNum": "POL-001",
      "msgHead": "PolicyTable",
      "error_reason": "数据对比失败: 键 'premium' 值不匹配"
    }
  ]
}

validation_errors_20240124_153045.csv
─────────────────────────────
policyNum,msgHead,error_reason
POL-001,PolicyTable,"数据对比失败: 键 'premium' 值不匹配"
...
```

---

## 🎓 学习路径

### 初级（快速上手）
1. 阅读 `QUICKSTART.md` (5 分钟)
2. 运行 `python test.py` (2 分钟)
3. 运行 `python main.py` (3 分钟)

### 中级（理解原理）
1. 阅读 `README.md` (15 分钟)
2. 查看 `validation.py` 的主要方法
3. 浏览其他模块的注释

### 高级（自定义扩展）
1. 阅读 `FRAMEWORK.md`
2. 修改 `validation.py` 添加新规则
3. 在 `advanced.py` 中添加新的导出格式

---

## ✅ 验证清单

在使用前请确认：

- [ ] Python 3.7+ 已安装
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] `.env` 文件已配置
- [ ] MongoDB 连接字符串正确
- [ ] 网络可以访问 MongoDB
- [ ] 已运行 `python test.py` 验证

---

## 🔗 文件关系图

```
用户
  ↓
main.py ⟷ cli.py ⟷ test.py
  ↓          ↓         ↓
validation.py + advanced.py
  ↓
query.py
  ↓
database.py
  ↓
MongoDB
```

---

## 📞 快速问题解答

**Q: 从哪里开始？**
A: 先看 `QUICKSTART.md`，然后运行 `python test.py`。

**Q: 如何验证自己的数据？**
A: 使用 `python cli.py --today` 验证今天的数据。

**Q: 结果在哪里？**
A: 在控制台输出，或使用 `--export json` 导出文件。

**Q: 如何调整验证规则？**
A: 编辑 `config.py` 和 `validation.py`。

**Q: 出错了怎么办？**
A: 运行 `python test.py` 检查各个模块是否正常工作。

---

## 🚀 现在就开始！

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境
cp .env.example .env
# 编辑 .env...

# 3. 测试一下
python test.py

# 4. 验证数据
python main.py
```

---

**一切就绪，开始使用你的数据对比工具吧！🎉**

