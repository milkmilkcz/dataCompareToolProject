# Data Validation Tool

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Jenkins](https://img.shields.io/badge/Jenkins-Ready-green.svg)](https://jenkins.io/)

**MongoDB 数据对比验证工具** - 支持 Jenkins CI/CD 集成的企业级数据质量验证解决方案。

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd data-validation-tool

# 安装依赖
pip install -r config/requirements.txt

# 或安装包
pip install -e .
```

### 配置

```bash
# 复制环境配置
cp config/.env.example .env

# 编辑配置
nano .env
```

### 使用

```bash
# 交互式验证
python -m data_validation_tool.cli.main

# 命令行验证
python -m data_validation_tool.cli.cli --today

# Jenkins 验证
python -m data_validation_tool.cli.jenkins_cli --today --export-junit
```

## 📋 功能特性

### ✅ 核心功能
- **MongoDB 数据查询** - 支持按时间范围查询 dataLakeMessage
- **多字段验证** - 支持 policyNum 和 agreementNum 字段
- **深度数据对比** - 递归对比嵌套数据结构
- **灵活配置** - 可配置验证规则和字段映射

### ✅ 企业级特性
- **Jenkins 集成** - 原生支持 CI/CD 流水线
- **JUnit 报告** - 标准测试报告格式
- **多格式导出** - JSON、CSV、XML 报告
- **凭证管理** - 安全的数据库连接

### ✅ 开发友好
- **模块化设计** - 清晰的包结构
- **类型提示** - 完整的类型注解
- **日志系统** - 结构化日志输出
- **测试套件** - 完整的单元测试

## 📁 项目结构

```
data-validation-tool/
├── src/data_validation_tool/          # 主包
│   ├── __init__.py                   # 包初始化
│   ├── core/                         # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py                 # 配置管理
│   │   ├── database.py               # 数据库连接
│   │   ├── query.py                  # 数据查询
│   │   └── validation.py             # 数据验证
│   ├── cli/                          # 命令行工具
│   │   ├── __init__.py
│   │   ├── main.py                   # 交互式工具
│   │   ├── cli.py                    # 高级命令行
│   │   ├── jenkins_cli.py            # Jenkins 工具
│   │   └── jenkins_build.py          # 本地构建模拟
│   └── utils/                        # 工具模块
│       ├── __init__.py
│       ├── advanced.py               # 高级功能
│       └── jenkins_reporter.py       # Jenkins 报告
├── tests/                            # 测试
│   ├── __init__.py
│   └── test_suite.py                 # 测试套件
├── docs/                             # 文档
│   ├── README.md                     # 项目文档
│   ├── QUICKSTART.md                 # 快速开始
│   ├── FRAMEWORK.md                  # 架构说明
│   └── jenkins/                      # Jenkins 文档
├── config/                           # 配置
│   ├── .env.example                  # 环境示例
│   └── requirements.txt              # 依赖列表
├── scripts/                          # 脚本
│   └── original_script.py            # 原始脚本
├── .gitignore                        # Git 忽略
├── Jenkinsfile                       # Jenkins Pipeline
├── setup.py                          # 包安装
├── MANIFEST.in                       # 包文件清单
└── pyproject.toml                    # 项目配置（可选）
```

## 🎯 使用场景

### 1. 数据质量监控
```bash
# 每天定时验证
python -m data_validation_tool.cli.jenkins_cli --today --export-junit
```

### 2. 业务数据验证
```bash
# 验证特定时间范围
python -m data_validation_tool.cli.cli --start 2024-01-01 --end 2024-01-31
```

### 3. 开发调试
```bash
# 运行测试
python -m pytest tests/

# 本地构建模拟
python -m data_validation_tool.cli.jenkins_build --time-range today
```

## 🔧 配置说明

### 环境变量 (.env)

```env
# MongoDB 连接
MONGODB_URI=mongodb+srv://user:pass@host/db?params
DATABASE_NAME=your_database

# 验证配置
REQUIRED_STATUS=2
DATA_LAKE_MESSAGE_COLLECTION=dataLakeMessage

# 日志配置
LOG_LEVEL=INFO
```

### 验证规则配置

编辑 `src/data_validation_tool/core/config.py`：

```python
# 状态验证
REQUIRED_STATUS = 2

# 集合名称
DATA_LAKE_MESSAGE_COLLECTION = 'dataLakeMessage'

# 忽略字段
IGNORE_FIELDS = {'_id', 'createdAt', 'updatedAt'}
```

## 📊 报告格式

### JUnit XML (Jenkins 原生)
```xml
<testsuite name="DataValidation" tests="100" failures="5">
    <testcase name="Valid Records (95)" classname="ValidationTest"/>
    <testcase name="Record 1: POL-001" classname="ValidationTest">
        <failure type="ValidationError">错误详情</failure>
    </testcase>
</testsuite>
```

### JSON 报告
```json
{
  "timestamp": "2024-01-24T15:30:45",
  "status": "FAILURE",
  "total_records": 100,
  "valid_records": 95,
  "error_records": 5,
  "error_details": [...]
}
```

## 🚀 Jenkins 集成

### Pipeline 配置

```groovy
pipeline {
    agent any
    stages {
        stage('数据验证') {
            steps {
                sh '''
                    python -m data_validation_tool.cli.jenkins_cli \\
                        --today --export-junit --export-json \\
                        --output build/reports
                '''
            }
            post {
                always {
                    junit 'build/reports/test-results*.xml'
                    publishHTML([
                        reportDir: 'build/reports',
                        reportFiles: 'validation-report*.json',
                        reportName: '验证报告'
                    ])
                }
            }
        }
    }
}
```

### 参数化构建

```groovy
parameters {
    choice(name: 'TIME_RANGE', choices: ['today', 'this-week', 'this-month'])
    booleanParam(name: 'EXPORT_REPORTS', defaultValue: true)
}
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_suite.py::test_database_connection

# 带覆盖率
python -m pytest --cov=src/data_validation_tool tests/
```

## 📚 文档

- **[快速开始](docs/QUICKSTART.md)** - 5分钟上手
- **[完整文档](docs/README.md)** - 详细功能说明
- **[架构设计](docs/FRAMEWORK.md)** - 系统设计说明
- **[Jenkins 集成](docs/jenkins/JENKINS_INTEGRATION.md)** - CI/CD 集成指南

## 🤝 贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持

- 📧 邮箱: dev@example.com
- 📖 文档: [完整文档](docs/)
- 🐛 问题: [GitHub Issues](https://github.com/your-org/data-validation-tool/issues)

---

**⭐ 如果这个项目对你有帮助，请给我们一个 star！**
