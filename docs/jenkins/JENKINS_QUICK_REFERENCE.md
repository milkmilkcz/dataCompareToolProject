# 📋 Jenkins 集成快速参考

## 📦 新增文件

| 文件 | 用途 |
|------|------|
| `jenkins_reporter.py` | 生成 Jenkins 友好的���告（JUnit XML、JSON） |
| `jenkins_cli.py` | Jenkins 专用命令行工具 |
| `Jenkinsfile` | Jenkins Pipeline 配置文件 |
| `JENKINS_INTEGRATION.md` | 完整的 Jenkins 集成指南 |

---

## 🚀 3 步快速集成

### 1️⃣ 在 Jenkins 创建 Pipeline
```
New Item → Pipeline
配置 Git 仓库 → 指向 Jenkinsfile
```

### 2️⃣ 添加 MongoDB 凭证（可选）
```
Manage Credentials → 添加 Secret text
ID: mongodb-uri
Secret: <你的 MongoDB 连接字符串>
```

### 3️⃣ 运行构建
```
开始构建 → 选择时间范围 → 构建
```

---

## 🎯 常用 CLI 命令

### 验证今天的数据
```bash
python jenkins_cli.py --today --export-junit
```

### 验证最近 7 天并生成所有报告
```bash
python jenkins_cli.py --last-days 7 --export-all --output build/reports
```

### 验证自定义日期范围
```bash
python jenkins_cli.py --start 2024-01-01 --end 2024-01-31 \
    --export-junit --export-json --export-csv --output build/reports
```

### 启用详细日志
```bash
python jenkins_cli.py --today -v --log-file build/logs/validation.log
```

---

## 📊 输出报告

| 报告类型 | 文件名 | 用途 |
|---------|-------|------|
| JUnit XML | `test-results-*.xml` | Jenkins 原生支持，显示测试结果 |
| JSON | `validation-report-*.json` | 结构化数据，便于集成 |
| CSV | `validation-errors-*.csv` | 错误数据，便于分析 |
| 日志 | `validation.log` | 详细的执行日志 |

---

## 🔄 Jenkinsfile 结构

```
Pipeline Stages:
├── 准备环境          (创建虚拟环境)
├── 安装��赖          (pip install)
├── 配置环境          (读取凭证，创建 .env)
├── 测试连接          (验证数据库连接)
├── 执行验证          (运行 jenkins_cli.py)
├── 生成报告          (发布 JUnit、HTML)
└── 上传构件          (归档文件)
```

---

## 🎛️ 参数化选项

| 参数 | 选项 | 说明 |
|------|------|------|
| `TIME_RANGE` | today / this-week / this-month / last-7-days / last-30-days / custom | 验证时间范围 |
| `START_DATE` | YYYY-MM-DD | 开始日期（custom 时使用） |
| `END_DATE` | YYYY-MM-DD | 结束日期（custom 时使用） |
| `EXPORT_REPORTS` | true/false | 是否导出报告 |

---

## 📈 退出码说明

```
0 → ✓ 成功（所有数据验证通过）
1 → ⚠ 失败（有错误数据，标记为 UNSTABLE）
2 → ✗ 错误（执行异常，标记为 FAILURE）
```

---

## 🔐 凭证管理

### 方式 1: Jenkins UI（推荐）
```groovy
withCredentials([string(credentialsId: 'mongodb-uri', variable: 'MONGODB_URI')]) {
    sh 'echo $MONGODB_URI | python jenkins_cli.py --today'
}
```

### 方式 2: 环境变量
```groovy
environment {
    MONGODB_URI = credentials('mongodb-uri')
}
```

### 方式 3: 参数化
```groovy
parameters {
    string(name: 'MONGODB_URI', defaultValue: '', description: 'MongoDB Connection String')
}
```

---

## 🐛 常见问题解决

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 数据库连接失败 | URI 错误或网络不通 | 检查凭证配置 |
| 找不到 Python 包 | 虚拟环境没激活 | 确保每个 sh 步骤激活 |
| 权限被拒绝 | 权限不足 | `chmod -R 755 ${WORKSPACE}` |
| 报告未发布 | 路径错误 | 检查 `--output` 目录 |

---

## 📋 检查清单

在 Jenkins 上部署前：

- [ ] 代码已推送到 Git
- [ ] Jenkinsfile 在仓库根目录
- [ ] MongoDB 凭证已添加到 Jenkins
- [ ] Python 3.7+ 已安装在 Jenkins Agent
- [ ] Jenkins 有 Pipeline 插件
- [ ] 虚拟网络可以访问 MongoDB

---

## 🔗 命令行完整参考

```bash
usage: jenkins_cli.py [-h] [--start START] [--end END] [--last-days LAST_DAYS]
                      [--today] [--this-week] [--this-month]
                      [--export-json] [--export-csv] [--export-junit]
                      [--export-all] [--output OUTPUT] [-v] [--log-file LOG_FILE]

时间范围（选择其一）:
  --start START          开始日期 (YYYY-MM-DD 或 HH:MM:SS)
  --end END              结束日期
  --last-days LAST_DAYS  最近 N 天
  --today                今天的数据
  --this-week            本周的数据
  --this-month           本月的数据

输出选项:
  --export-json          导出 JSON 报告
  --export-csv           导出 CSV 报告
  --export-junit         导出 JUnit XML（推荐）
  --export-all           导出所有格式
  --output OUTPUT        输出目录（默认：当前目录）

日志选项:
  -v, --verbose          详细日志
  --log-file LOG_FILE    日志文件路径
```

---

## 🎨 集成示例

### Slack 通知示例
```groovy
post {
    always {
        script {
            def color = env.VALIDATION_EXIT_CODE == '0' ? 'good' : 'danger'
            slackSend(color: color, message: "验证完成: ${currentBuild.result}")
        }
    }
}
```

### 邮件通知示例
```groovy
post {
    failure {
        emailext(
            subject: "数据验证失败: ${BUILD_NUMBER}",
            body: "请查看 ${BUILD_URL}console",
            to: "admin@example.com"
        )
    }
}
```

### 定时触发示例
```groovy
triggers {
    cron('H 2 * * *')  // 每天凌晨 2 点
}
```

---

## 📊 Jenkins 中查看结果

### JUnit 测试结果
```
点击构建编号
→ Test Result（如果有失败）
→ 查看失败详情
```

### 构件下载
```
点击构建编号
→ Build Artifacts
→ 下载 test-results.xml、validation-report.json 等
```

### 控制台日志
```
点击构建编号
→ Console Output
→ 查看完整��建日志
```

---

## 💡 性能优化建议

1. **并行处理**：禁用（已在 Jenkinsfile 中设置）
   ```groovy
   disableConcurrentBuilds()
   ```

2. **超时设置**：30 分钟
   ```groovy
   timeout(time: 30, unit: 'MINUTES')
   ```

3. **构建历史保留**：最多 30 个
   ```groovy
   buildDiscarder(logRotator(numToKeepStr: '30'))
   ```

4. **缓存虚拟环境**（可选）：
   ```groovy
   sh 'test -d venv || python -m venv venv'
   ```

---

## 🔄 与其他 CI/CD 的适配

### GitLab CI
```yaml
stages:
  - validate

data_validation:
  stage: validate
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - python jenkins_cli.py --today --export-junit
  artifacts:
    reports:
      junit: test-results*.xml
```

### GitHub Actions
```yaml
name: Data Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python jenkins_cli.py --today --export-junit
      - uses: actions/upload-artifact@v2
```

---

## 📞 获取帮助

1. **查看 Jenkinsfile**：`cat Jenkinsfile`
2. **查看日志**：构建 → Console Output
3. **查看报告**：构建 → Build Artifacts
4. **查看完整指南**：`JENKINS_INTEGRATION.md`

---

**现在���以开始在 Jenkins 上运行你的验证工具了！** 🎉

