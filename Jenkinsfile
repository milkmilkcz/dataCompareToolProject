// Jenkinsfile - 数据对比验证工具 Pipeline

pipeline {
    agent any

    // 环境变量
    environment {
        PYTHON_VERSION = '3.9'
        VIRTUAL_ENV = "${WORKSPACE}/venv"
        PATH = "${VIRTUAL_ENV}/Scripts:${PATH}"
        PYTHONUNBUFFERED = '1'
    }

    // 参数化构建
    parameters {
        choice(
            name: 'TIME_RANGE',
            choices: ['today', 'this-week', 'this-month', 'last-7-days', 'last-30-days', 'custom'],
            description: '验证时间范围'
        )
        string(
            name: 'START_DATE',
            defaultValue: '2024-01-01',
            description: '开始日期 (YYYY-MM-DD)，仅当 TIME_RANGE=custom 时使用'
        )
        string(
            name: 'END_DATE',
            defaultValue: '2024-01-31',
            description: '结束日期 (YYYY-MM-DD)，仅当 TIME_RANGE=custom 时使用'
        )
        booleanParam(
            name: 'EXPORT_REPORTS',
            defaultValue: true,
            description: '是否导出验证报告'
        )
    }

    options {
        // 最多保留 30 次构建
        buildDiscarder(logRotator(numToKeepStr: '30'))
        // 超时设置（30分钟）
        timeout(time: 30, unit: 'MINUTES')
        // 不允许并行构建
        disableConcurrentBuilds()
        // 在构建开始时打印时间戳
        timestamps()
    }

    stages {
        stage('准备环境') {
            steps {
                script {
                    echo "========== 开始数据对比验证 =========="
                    echo "构建编号: ${BUILD_NUMBER}"
                    echo "构建时间: ${BUILD_TIMESTAMP}"
                    echo "验证范围: ${params.TIME_RANGE}"
                }

                // 创建虚拟环境
                sh '''
                    echo "创建 Python 虚拟环境..."
                    python -m venv venv
                    . venv/Scripts/activate || . venv/bin/activate
                    pip install --upgrade pip setuptools
                '''
            }
        }

        stage('安装依赖') {
            steps {
                sh '''
                    echo "安装项目依赖..."
                    . venv/Scripts/activate || . venv/bin/activate
                    pip install -r config/requirements.txt
                '''
            }
        }

        stage('配置环境') {
            steps {
                script {
                    echo "配置 MongoDB 连接..."
                    // 从 Jenkins 凭证或环境变量获取
                    withCredentials([string(credentialsId: 'mongodb-uri', variable: 'MONGODB_URI')]) {
                        sh '''
                            # 创建 .env 文件
                            cat > .env << EOF
MONGODB_URI=${MONGODB_URI}
DATABASE_NAME=sit
LOG_LEVEL=INFO
EOF
                            echo ".env 文件已创建"
                        '''
                    }
                }
            }
        }

        stage('测试连接') {
            steps {
                sh '''
                    echo "测试数据库连接..."
                    . venv/Scripts/activate || . venv/bin/activate
                    python -c "
import sys
sys.path.insert(0, 'src')
from data_validation_tool.core.database import get_db_connection
conn = get_db_connection()
if conn.connect():
    print('✓ 数据库连接成功')
    conn.close()
else:
    print('✗ 数据库连接失败')
    sys.exit(1)
"
                '''
            }
        }

        stage('执行验证') {
            steps {
                script {
                    // 根据参数选择验证命令
                    def validateCmd = '. venv/Scripts/activate || . venv/bin/activate\n'
                    validateCmd += 'python jenkins_cli.py'

                    if (params.TIME_RANGE == 'today') {
                        validateCmd += ' --today'
                    } else if (params.TIME_RANGE == 'this-week') {
                        validateCmd += ' --this-week'
                    } else if (params.TIME_RANGE == 'this-month') {
                        validateCmd += ' --this-month'
                    } else if (params.TIME_RANGE == 'last-7-days') {
                        validateCmd += ' --last-days 7'
                    } else if (params.TIME_RANGE == 'last-30-days') {
                        validateCmd += ' --last-days 30'
                    } else if (params.TIME_RANGE == 'custom') {
                        validateCmd += " --start ${params.START_DATE} --end ${params.END_DATE}"
                    }

                    // 添加导出选项
                    if (params.EXPORT_REPORTS) {
                        validateCmd += ' --export-all --output build/reports'
                    }

                    validateCmd += ' --log-file build/logs/validation.log'

                    // 创建日志���录
                    sh 'mkdir -p build/reports build/logs'

                    // 执行验证（允许失败，以便后续处理报告）
                    def exitCode = sh(script: validateCmd, returnStatus: true)

                    // 存储退出码供后续使用
                    env.VALIDATION_EXIT_CODE = exitCode
                    echo "验证退出码: ${exitCode}"
                }
            }
        }

        stage('生成报告') {
            when {
                expression {
                    return params.EXPORT_REPORTS
                }
            }
            steps {
                script {
                    echo "生成构建报告..."

                    // 发布 JUnit 报告（如果存在）
                    junit(
                        testResults: 'build/reports/test-results*.xml',
                        allowEmptyResults: true
                    )

                    // 发布其他报告
                    publishHTML([
                        reportDir: 'build/reports',
                        reportFiles: 'validation-report*.json',
                        reportName: '验证报告'
                    ])
                }
            }
        }

        stage('上传构件') {
            when {
                expression {
                    return params.EXPORT_REPORTS
                }
            }
            steps {
                script {
                    echo "上传构件..."
                    archiveArtifacts(
                        artifacts: 'build/reports/**,build/logs/**',
                        fingerprint: true,
                        allowEmptyArchive: true
                    )
                }
            }
        }
    }

    post {
        always {
            script {
                echo "========== 清理环境 =========="

                // 收集日志
                sh '''
                    if [ -f build/logs/validation.log ]; then
                        echo "\n========== 验证日志 =========="
                        cat build/logs/validation.log
                    fi
                '''

                // 清理虚拟环境（可选）
                // sh 'rm -rf venv'
            }
        }

        success {
            script {
                def exitCode = env.VALIDATION_EXIT_CODE?.toInteger() ?: 0
                if (exitCode == 0) {
                    echo "✓ 构建成功，所有数据验证通过"
                    // 可选：发送通知
                } else if (exitCode == 1) {
                    echo "⚠ 验证发现错误，请查��报告"
                    // 标记为不稳定
                    currentBuild.result = 'UNSTABLE'
                }
            }
        }

        failure {
            script {
                echo "✗ 构建失败"
                // 可选：发送失败通知
                // mail to: 'devops@example.com',
                //      subject: "数据验证失败: ${JOB_NAME} ${BUILD_NUMBER}",
                //      body: "请查看 ${BUILD_URL}console 获取详情"
            }
        }

        unstable {
            script {
                echo "⚠ 构建不稳定，有验证错误"
            }
        }
    }
}
