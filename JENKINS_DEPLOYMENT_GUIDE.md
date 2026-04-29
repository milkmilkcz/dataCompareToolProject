# 🚀 Jenkins 部署完整指南

## 📋 目录
1. [Jenkins 初始化](#jenkins-初始化)
2. [安装必要插件](#安装必要插件)
3. [配置凭证](#配置凭证)
4. [创建 Pipeline 任务](#创建-pipeline-任务)
5. [参数化构建](#参数化构建)
6. [运行和监控](#运行和监控)
7. [故障排除](#故障排除)

---

## Jenkins 初始化

### 步骤 1: 访问 Jenkins

1. **打开浏览器** → `http://localhost:8080`

2. **获取初始管理员密码**
   ```powershell
   # 在 PowerShell 中运行
   Get-Content C:\Users\chenleo\.jenkins\secrets\initialAdminPassword
   ```
   复制输出的密码

3. **粘贴密码**
   - 在 Jenkins 界面输入密码
   - 点击 "Continue"

### 步骤 2: 安装推荐插件

1. 在解锁页面，选择 **"Install suggested plugins"**
2. 等待插件安装完成（2-5 分钟）

### 步骤 3: 创建管理员账户

1. 填写表单：
   - 用户名: `admin` (或自定义)
   - 密码: ****** (自定义强密码)
   - 确认密码: ****
   - 邮箱: your@email.com
   
2. 点击 **"Save and Continue"**

### 步骤 4: 配置 Jenkins URL

- Jenkins URL: `http://localhost:8080/` (默认)
- 点击 **"Save and Finish"**

---

## 安装必要插件

### 步骤 1: 进入插件管理

1. 点击左菜单 **"Manage Jenkins"**
2. 选择 **"Manage Plugins"** (或 "Plugin Manager")
3. 点击 **"Available plugins"** 标签

### 步骤 2: 安装必要的插件

搜索并安装以下插件：

| 插件名 | 用途 | 必需 |
|--------|------|------|
| **Pipeline** | Pipeline 支持 | ✓ 必需 |
| **Git** | Git 集成 | ✓ 必需 |
| **JUnit Plugin** | JUnit 报告 | ✓ 必需 |
| **Email Extension** | 邮件通知 | 可选 |
| **GitHub** | GitHub 集成 | 可选 |
| **Performance Plugin** | 性能报告 | 可选 |

**安装步骤**：
1. 在搜索框输入插件名
2. 勾选插件
3. 点击 **"Install without restart"** 或 **"Download and Install"**
4. 等待安装完成

### 步骤 3: 重启 Jenkins (可选)

```powershell
# 如果需要重启
.\start-jenkins.ps1 -Restart
```

---

## 配置凭证

### 步骤 1: 进入凭证管理

1. 点击 **"Manage Jenkins"**
2. 选择 **"Credentials"** (或 "Manage Credentials")
3. 点击 **"System"**
4. 点击 **"Global credentials (unrestricted)"**

### 步骤 2: 添加 MongoDB 凭证

1. 点击左侧 **"Add Credentials"**

2. **配置项**:
   - Kind: **Secret text** (或 Username with password)
   - Scope: **Global**
   - Secret: `mongodb://user:pass@host:27017/database`
   - ID: `mongodb-uri` (重要！必须与 Jenkinsfile 中一致)
   - Description: MongoDB Connection String

3. 点击 **"Create"**

### 步骤 3: 添加 Git 凭证 (如果需要)

如果项目托管在 GitHub，添加 GitHub 凭证：

1. 点击 **"Add Credentials"**

2. **配置项**:
   - Kind: **GitHub Personal Access Token** (或 Username with password)
   - Token: (GitHub PAT)
   - ID: `github-credentials`
   - Description: GitHub Access

3. 点击 **"Create"**

---

## 创建 Pipeline 任务

### 步骤 1: 新建任务

1. 主页 → **"New Item"** (或 "Create a job")
2. 输入任务名称: `DataValidation` (或与项目相关的名称)
3. 选择 **"Pipeline"**
4. 点击 **"OK"**

### 步骤 2: 配置 Pipeline

#### 方式 A: 从 Git 仓库读取 Jenkinsfile (推荐)

1. **Pipeline** 部分，选择定义方式:
   - Definition: **Pipeline script from SCM**

2. **SCM 配置**:
   - SCM: **Git**
   - Repository URL: `https://github.com/your-org/data-validation-tool.git` (本地可用 file:// 路径)
   - Branch: `*/main` 或 `*/master`
   - Script Path: `Jenkinsfile` (默认)

3. **如果是本地项目** (不用 Git):
   - Repository URL: `file:///C:/Users/chenleo/PyCharmMiscProject`

#### 方式 B: 直接粘贴 Jenkinsfile 内容

1. **Pipeline** 部分，选择定义方式:
   - Definition: **Pipeline script**

2. **Script** 区域:
   - 复制 Jenkinsfile 的全部内容
   - 粘贴到任务配置中

### 步骤 3: 保存任务

点击 **"Save"**

---

## 参数化构建

### 任务参数配置

在任务配置中（Pipeline 部分之前），会看到构建参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| TIME_RANGE | Choice | today | 时间范围选择 |
| START_DATE | String | 2024-01-01 | 自定义开始日期 |
| END_DATE | String | 2024-01-31 | 自定义结束日期 |
| EXPORT_REPORTS | Boolean | true | 是否导出报告 |

### 时间范围选项说明

- **today** - 验证今天的数据
- **this-week** - 验证本周数据
- **this-month** - 验证本月数据
- **last-7-days** - 最近 7 天
- **last-30-days** - 最近 30 天
- **custom** - 自定义日期范围 (需要填 START_DATE 和 END_DATE)

---

## 运行和监控

### 步骤 1: 运行任务

#### 方法 1: Jenkins 页面运行

1. 打开任务页面
2. 点击 **"Build with Parameters"** (或 "Build Now")
3. 选择参数:
   - TIME_RANGE: `today`
   - EXPORT_REPORTS: ✓ 勾选
4. 点击 **"Build"**

#### 方法 2: 使用启动菜单运行

```powershell
.\launcher.ps1
# 选择选项 11 - 生成验证报告
```

### 步骤 2: 监控构建

1. **查看构建进度**
   - 点击左侧 "Build History" 中的构建号
   - 选择 "Console Output" 查看实时日志

2. **查看构建结果**
   - 等待构建完成
   - 查看 "Build Artifacts" 中的报告文件

3. **查看生成的报告**
   - JUnit 报告自动发布
   - JSON/CSV 报告在 "Artifacts" 中下载

---

## 完整的 Pipeline 阶段说明

### 1. 准备环境 (Prepare Environment)
```
✓ 创建 Python 虚拟环境
✓ 升级 pip 和 setuptools
✓ 显示构建信息
```

### 2. 安装依赖 (Install Dependencies)
```
✓ 激活虚拟环境
✓ 安装 requirements.txt 中的依赖
  - pymongo (MongoDB 驱动)
  - python-dotenv (环境变量)
  - openpyxl (Excel 导出)
```

### 3. 配置环境 (Configure Environment)
```
✓ 从 Jenkins 凭证读取 MongoDB URI
✓ 创建 .env 文件
✓ 设置数据库连接参数
```

### 4. 测试连接 (Test Connection)
```
✓ 验证 MongoDB 连接
✓ 如果连接失败，构建中止
```

### 5. 执行验证 (Execute Validation)
```
✓ 根据参数选择验证范围
✓ 运行数据验证
✓ 生成报告 (如果启用)
```

### 6. 生成报告 (Generate Report)
```
✓ 发布 JUnit XML 报告
✓ 发布 HTML 报告
✓ 存储构件
```

### 7. 上传构件 (Archive Artifacts)
```
✓ 保存所有报告文件
✓ 保存日志文件
✓ 可供后续下载
```

---

## 构建输出和报告

### 报告位置

构建完成后，可以在 Jenkins 中找到：

1. **JUnit 报告**
   - Jenkins 自动发布
   - 点击 "Test Result" 查看

2. **JSON 报告**
   - 位置: `build/reports/validation-report-*.json`
   - 在 "Artifacts" 中下载

3. **CSV 报告**
   - 位置: `build/reports/validation-errors-*.csv`
   - 在 "Artifacts" 中下载

4. **日志文件**
   - 位置: `build/logs/validation.log`
   - 构建日志页面中查看

### 报告内容

#### JUnit 报告 (XML)
```xml
<testsuite name="DataValidation" tests="100">
  <testcase name="Valid Records" classname="ValidationTest"/>
  <testcase name="Record 1" classname="ValidationTest">
    <failure type="ValidationError">错误详情</failure>
  </testcase>
</testsuite>
```

#### JSON 报告
```json
{
  "timestamp": "2024-01-24T15:30:45",
  "status": "SUCCESS",
  "total_records": 100,
  "valid_records": 95,
  "error_records": 5,
  "error_details": [...]
}
```

---

## 定时执行 (可选)

### 配置定时构建

1. 打开任务配置
2. 找到 **"Build Triggers"**
3. 选择 **"Build periodically"** 或 **"Poll SCM"**

### Cron 表达式示例

```
# 每天凌晨 2 点
0 2 * * *

# 每小时
0 * * * *

# 每周一 3 点
0 3 * * 1

# 工作日每天 8 点
0 8 * * 1-5

# 每 15 分钟
*/15 * * * *
```

---

## 邮件通知 (可选)

### 配置邮件通知

1. 点击 **"Manage Jenkins"** → **"Configure System"**
2. 找到 **"E-mail Notification"** 部分
3. 配置 SMTP 服务器
4. 在任务中添加 Post-build Action

### Post-build 邮件配置

在任务配置中添加：

```groovy
post {
    success {
        emailext(
            subject: "✓ 数据验证成功: ${JOB_NAME} #${BUILD_NUMBER}",
            body: "构建成功，报告已生成。\nURL: ${BUILD_URL}",
            to: "team@example.com"
        )
    }
    failure {
        emailext(
            subject: "✗ 数据验证失败: ${JOB_NAME} #${BUILD_NUMBER}",
            body: "构建失败，请查看日志。\nURL: ${BUILD_URL}console",
            to: "team@example.com"
        )
    }
}
```

---

## 高级配置

### 多分支 Pipeline

支持从不同 Git 分支自动创建 Pipeline：

1. 创建 **"Multibranch Pipeline"** 任务
2. 配置 Git 仓库
3. Jenkins 自动为每个分支创建任务

### 蓝海视图 (Blue Ocean)

安装 Blue Ocean 插件获得更好的可视化：

1. 点击 **"Manage Plugins"**
2. 搜索 **"Blue Ocean"**
3. 安装并重启

然后访问: `http://localhost:8080/blue/`

---

## 故障排除

### 问题1: MongoDB 连接失败

**症状**: 构建在 "Test Connection" 阶段失败

**解决方案**:
1. 检查 MongoDB 是否运行
2. 验证 MongoDB URI 凭证
3. 检查网络连接

```powershell
# 测试 MongoDB 连接
python -m data_validation_tool.cli.cli --today
```

### 问题2: 找不到 Jenkinsfile

**症状**: "Failed to load Jenkinsfile"

**解决方案**:
```
1. 检查 Jenkinsfile 是否在项目根目录
2. 检查 Git 仓库 URL
3. 检查分支名称
4. 如有需要，使用本地文件路径: file:///C:/path/to/project
```

### 问题3: Python 虚拟环境错误

**症状**: "venv not found" 或虚拟环境损坏

**解决方案**:
```groovy
// 在 Jenkinsfile 中添加清理步骤
stage('Cleanup') {
    steps {
        deleteDir()  // 删除整个工作区
    }
}
```

### 问题4: 权限错误

**症状**: "Permission denied"

**解决方案**:
```powershell
# 以管理员身份运行 Jenkins
# 或设置 Jenkins 用户权限
```

### 问题5: 超时问题

**症状**: "Build timeout after X minutes"

**解决方案**:
1. 增加 Jenkinsfile 中的超时时间
2. 优化验证性能
3. 检查是否有卡死的进程

---

## Jenkins 维护

### 备份 Jenkins 配置

```powershell
# 备份 Jenkins 主目录
Copy-Item -Path C:\Users\chenleo\.jenkins -Destination C:\Jenkins\backup -Recurse
```

### 查看 Jenkins 日志

```powershell
# 实时查看
Get-Content C:\Jenkins\jenkins-startup.log -Wait

# 查看历史
Get-Content C:\Jenkins\jenkins-startup.log -Tail 100
```

### 清理构建历史

1. 打开任务配置
2. 找到 **"Discard old builds"**
3. 设置保留天数或构建数

---

## 监控和告警

### 构建失败告警

```groovy
post {
    failure {
        script {
            echo "✗ 构建失败，已通知团队"
            // 可添加邮件、Slack 等通知
        }
    }
}
```

### 性能监控

1. 安装 "Performance Plugin"
2. 添加性能报告
3. 监控构建时间趋势

---

## 最佳实践

### 1. 凭证管理
- ✓ 使用 Jenkins 凭证管理敏感信息
- ✓ 不在 Jenkinsfile 中硬编码密码
- ✓ 定期更新凭证

### 2. 构建最优化
- ✓ 缓存依赖包
- ✓ 并行执行可独立的任务
- ✓ 限制日志保留

### 3. 错误处理
- ✓ 添加完善的错误处理
- ✓ 提供清晰的错误消息
- ✓ 自动回滚失败的构建

### 4. 监控和告警
- ✓ 配置邮件通知
- ✓ 设置构建失败告警
- ✓ 监控构建时间趋势

---

## 快速参考

### Jenkins 常用 URL

```
Jenkins 主页:           http://localhost:8080
任务列表:               http://localhost:8080/
任务配置:               http://localhost:8080/job/DataValidation/configure
构建日志:               http://localhost:8080/job/DataValidation/lastBuild/console
蓝海视图:               http://localhost:8080/blue/
插件管理:               http://localhost:8080/pluginManager
系统配置:               http://localhost:8080/configure
```

### Groovy 常用脚本片段

```groovy
// 设置环境变量
environment {
    PYTHON_PATH = "${WORKSPACE}/venv/bin"
}

// 条件执行
when {
    expression { params.TIME_RANGE == 'custom' }
}

// 错误处理
try {
    sh 'python -m pytest tests/'
} catch (Exception e) {
    echo "Tests failed: ${e}"
    currentBuild.result = 'FAILURE'
}

// 并行执行
parallel {
    'Test' {
        sh 'python -m pytest tests/'
    }
    'Lint' {
        sh 'python -m flake8 src/'
    }
}
```

---

## 下一步

1. ✅ 初始化 Jenkins
2. ✅ 安装必要插件
3. ✅ 配置凭证
4. ✅ 创建 Pipeline 任务
5. ✅ 运行第一次构建
6. 📊 监控构建结果
7. 🔄 设置定时执行
8. 📧 配置通知

---

## 相关文档

- [Jenkinsfile 说明](./Jenkinsfile)
- [项目 README](./README.md)
- [启动指南](./LAUNCHER_GUIDE.md)
- [Python 脚本说明](./SCRIPTS_README.md)

---

**现在你已掌握如何在 Jenkins 上部署此项目！** 🎉

访问 http://localhost:8080 开始吧！

---

**版本**: 1.0.0  
**创建日期**: 2026-04-28  
**更新**: Jenkins Pipeline 完整部署指南

