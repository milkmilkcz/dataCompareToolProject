# Jenkins 集成指南

## 概述

此项目已针对 Jenkins CI/CD 流程进行了完整优化，支持：

✓ 参数化构建  
✓ JUnit XML 报告支持  
✓ 结构化日志输出  
✓ 自动退出码处理  
✓ 报告归档  
✓ 凭证管理

---

## 快速集成步骤

### 1. 在 Jenkins 中创建新的 Pipeline 项目

```
新建 → Pipeline
```

### 2. 配置 Git 仓库

```
Pipeline → Definition：Pipeline script from SCM
SCM：Git
Repository URL：<你的代码仓库>
Branch：*/main 或其他分支
Script Path：Jenkinsfile
```

### 3. 配置 MongoDB 凭证（可选）

```
Jenkins 首页 → Manage Jenkins → Manage Credentials → 添加凭证

类型：Secret text
ID：mongodb-uri
Secret：<你的 MongoDB 连接字符串>
```

### 4. 构建项目

```
立即构建 → 选择参数 → 开始构建
```

---

## Jenkinsfile 说明

### 主要 Stage

#### 1. 准备环境
- 创建 Python 虚拟环境
- 升级 pip

#### 2. 安装依赖
- 安装 requirements.txt 中的包

#### 3. 配置环境
- 从 Jenkins 凭证读取 MongoDB URI
- 创建 .env 文件

#### 4. 测试连接
- 验证数据库连接是否成功

#### 5. 执行验证
- 根据参数执行数据对比
- 生成报告

#### 6. 生成报告
- 发布 JUnit 测试报告
- 生成 HTML 报告

#### 7. 上传构件
- 归档报告和日志

### 退出码处理

| 退出码 | 含义 |
|--------|------|
| 0 | ✓ 成功，所有数据验证��过 |
| 1 | ⚠ 验证失败，有错误数据（标记为 UNSTABLE）|
| 2 | ✗ 执行错误或异常（标记为 FAILURE）|

---

## 参数化选项

### TIME_RANGE（时间范围）
- `today` - 今天的数据
- `this-week` - 本周的数据
- `this-month` - 本月的数据
- `last-7-days` - 最近 7 天
- `last-30-days` - 最近 30 天
- `custom` - 自定义日期范围

### START_DATE / END_DATE
- 仅在 `TIME_RANGE=custom` 时使用
- 格式：`YYYY-MM-DD`

### EXPORT_REPORTS
- `true` - 导出所有格式的报告
- `false` - 仅输出日志，不生成报告

---

## Jenkins CLI 命令

直接调用 Jenkins CLI 进行验证：

```bash
# 验证今天的数据，导出所有报告
python jenkins_cli.py --today --export-all --output build/reports

# 验证指定日期范围
python jenkins_cli.py --start 2024-01-01 --end 2024-01-31 \
    --export-junit --export-json --export-csv \
    --output build/reports

# 启用详细日志
python jenkins_cli.py --today --verbose --log-file build/logs/validation.log

# 仅导出 JUnit XML（Jenkins 原生支持）
python jenkins_cli.py --last-days 7 --export-junit --output build/reports
```

### 命令行选项

```
时间范围（选择其一）:
  --start DATE      开始日期 (YYYY-MM-DD)
  --end DATE        结束日期 (YYYY-MM-DD)
  --last-days N     最近 N 天
  --today           今天的数据
  --this-week       本周的数据
  --this-month      本月的数据

输出选项:
  --export-json     导出 JSON 报告
  --export-csv      导出 CSV 报告
  --export-junit    导出 JUnit XML（推荐）
  --export-all      导出所有格式
  --output DIR      输出目录（默认：当前目录）

日志选项:
  -v, --verbose     详细日志
  --log-file FILE   日志文件路径
```

---

## 输出报告说明

### JUnit XML (`test-results-*.xml`)
- Jenkins 原生支持的格式
- 可在 Jenkins UI 中显示测试结果
- 包含：测试数量、失败数量、失败详情

### JSON 报告 (`validation-report-*.json`)
- 结构化的验证结果
- 包含：时间戳、状态、记录统计、错误详情
- 适合后续处理和集成

### CSV 错误日志 (`validation-errors-*.csv`)
- 便于电子表格软件打开
- 包含：保单号、业务表、错误原因等

### ���志文件 (`validation.log`)
- 详细的执行日志
- 用于故障排查

---

## 与 Jenkins 集成的高级用法

### 1. 配置邮件通知

在 Jenkinsfile 中修改 `post` 段：

```groovy
post {
    failure {
        mail to: 'devops@example.com',
             subject: "数据验证失败: ${JOB_NAME} #${BUILD_NUMBER}",
             body: """
请查看以下链接获取详情:
${BUILD_URL}console

构建日志:
${BUILD_LOG_EXCERPT}
             """
    }
    
    unstable {
        mail to: 'devops@example.com',
             subject: "数据验证有错误: ${JOB_NAME} #${BUILD_NUMBER}",
             body: "验证发现 ${VALIDATION_ERROR_COUNT} 条错误数据。\n${BUILD_URL}"
    }
}
```

### 2. 定时构建

在 Jenkins 项目配置中设置定时触发器：

```
构建触发器 → 定时构建

H 2 * * *    （每天凌晨 2 点执行）
H 0 * * 0    （每周一凌晨执行）
H 0 1 * *    （每月 1 号凌晨执行）
```

### 3. 触发其他 Job

在 Jenkinsfile 中调用其他 Job：

```groovy
stage('触发后续处理') {
    when {
        expression { env.VALIDATION_EXIT_CODE == '1' }
    }
    steps {
        build job: 'data-repair-job', parameters: [
            string(name: 'REPORT_URL', value: "${BUILD_URL}artifact/build/reports/"),
            string(name: 'BUILD_NUMBER', value: "${BUILD_NUMBER}")
        ]
    }
}
```

### 4. Slack 通知

```groovy
def color = env.VALIDATION_EXIT_CODE == '0' ? 'good' : 'danger'
slackSend(
    color: color,
    message: """
数据验证 - ${JOB_NAME} #${BUILD_NUMBER}
状态: ${currentBuild.result}
查看详情: ${BUILD_URL}
    """
)
```

---

## 凭证管理

### 方式 1: Jenkins UI 凭证

```
Manage Jenkins → Manage Credentials → 添加凭证

类型: Secret text
ID: mongodb-uri
Secret: mongodb+srv://user:pass@host/db?params
```

然后在 Jenkinsfile 中使用：

```groovy
withCredentials([string(credentialsId: 'mongodb-uri', variable: 'MONGODB_URI')]) {
    sh 'export MONGODB_URI=$MONGODB_URI && python jenkins_cli.py --today'
}
```

### 方式 2: 环境变量

在 Jenkins 项目配置中设置全局环境变量：

```
Configuration → Build Environment → 提供参数

MONGODB_URI=<连接字符串>
LOG_LEVEL=INFO
```

### 方式 3: .env 文件（不推荐在 CI/CD 中使用）

```groovy
sh '''
    cat > .env << EOF
MONGODB_URI=${MONGODB_URI}
DATABASE_NAME=sit
LOG_LEVEL=DEBUG
EOF
'''
```

---

## 故障排查

### 问题 1: "无法连接数据库"

**原因**：MongoDB URI 不正确或网络不通

**解决**：
```groovy
stage('测试连接') {
    steps {
        sh '''
            python -c "
from pymongo import MongoClient
try:
    client = MongoClient('${MONGODB_URI}', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✓ 连接成功')
except Exception as e:
    print(f'✗ 连接失败: {e}')
    exit(1)
"
        '''
    }
}
```

### 问题 2: "找不到 Python 包"

**原因**：虚拟环境没有正确激活

**解决**：确保每个 sh 步骤都激活虚拟环境
```bash
. venv/Scripts/activate || . venv/bin/activate
```

### 问题 3: "权限被拒绝"

**原因**：Jenkins 用户对工作目录没有写权限

**解决**：
```bash
chmod -R 755 ${WORKSPACE}
```

### 问题 4: "报告没有发布"

**原因**：报告文件路径不正确

**解决**：
```groovy
// 调试：打印文件列表
sh 'find build/ -type f -name "*.xml" -o -name "*.json" -o -name "*.csv"'
```

---

## 最佳实践

### 1. 使用虚拟环境隔离依赖
```groovy
python -m venv venv
```

### 2. 记录详细日志便于调试
```groovy
--verbose --log-file build/logs/validation.log
```

### 3. 保留历史报告
```groovy
buildDiscarder(logRotator(numToKeepStr: '30'))
```

### 4. 设置合理的超时时间
```groovy
timeout(time: 30, unit: 'MINUTES')
```

### 5. 不允许并行构建（避免数据库冲突）
```groovy
disableConcurrentBuilds()
```

### 6. 使用凭证管理敏感信息
```groovy
withCredentials([...]) {
    // 不要在日志中打印密钥
}
```

### 7. 定期备份报告
```groovy
archiveArtifacts artifacts: 'build/reports/**'
```

---

## 与 GitLab CI/CD 的适配

虽然提供的是 Jenkinsfile，但也可以用于 GitLab CI：

`.gitlab-ci.yml` 示例：
```yaml
stages:
  - validate

data_validation:
  stage: validate
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - cp .env.example .env
    - echo "MONGODB_URI=$MONGODB_URI" >> .env
    - python jenkins_cli.py --today --export-all --output reports
  artifacts:
    reports:
      junit: reports/test-results*.xml
    paths:
      - reports/**
    expire_in: 30 days
  only:
    - main
  retry:
    max: 2
```

---

## 常见问题

**Q: 如何跳过某个 stage？**
A: 使用 `when` 条件：
```groovy
stage('上传构件') {
    when {
        expression { params.EXPORT_REPORTS }
    }
    steps { ... }
}
```

**Q: 如何在 stage 之间传递数据？**
A: 使用环境变量：
```groovy
env.VALIDATION_RESULTS = readFile('build/reports/validation-report.json')
```

**Q: 如何修改 stage 的执行条件？**
A: 使用 `when` 指令：
```groovy
when {
    branch 'main'
    expression { env.BUILD_NUMBER as Integer > 100 }
}
```

**Q: 如何在 Jenkins 中查看详细日志？**
A: 点击构建编号 → Console Output

---

## 参考资源

- [Jenkinsfile 官方文档](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Jenkins Pipeline 插件](https://plugins.jenkins.io/workflow-aggregator/)
- [JUnit 格式规范](https://github.com/junit-team/junit5/wiki/JUnit-Platform-Reporting)

---

**现在可以将此项目集成到你的 Jenkins CI/CD 流程了！** 🚀

