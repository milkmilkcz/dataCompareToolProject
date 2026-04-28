#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地 Jenkins 构建模拟脚本

用于在本地测试 Jenkins 集成，模拟 Jenkins 环境
"""

import os
import sys
import subprocess
import argparse
import shutil
from datetime import datetime
from pathlib import Path


class LocalJenkinsBuild:
    """本地 Jenkins 构建模拟器"""

    def __init__(self, workspace: str = '.'):
        self.workspace = Path(workspace).resolve()
        self.venv_path = self.workspace / 'venv'
        self.build_dir = self.workspace / 'build'
        self.reports_dir = self.build_dir / 'reports'
        self.logs_dir = self.build_dir / 'logs'

        print(f"工作目录: {self.workspace}")

    def setup_virtual_env(self):
        """设置虚拟环境"""
        print("\n[1/7] 准备环境")
        print("-" * 50)

        if self.venv_path.exists():
            print(f"虚拟环境已存在: {self.venv_path}")
        else:
            print("创建虚拟环境...")
            result = subprocess.run(
                [sys.executable, '-m', 'venv', str(self.venv_path)],
                cwd=str(self.workspace)
            )
            if result.returncode != 0:
                print("✗ 虚拟环境创建失败")
                return False

        print("✓ 虚拟环境准备完成")
        return True

    def install_dependencies(self):
        """安装依赖"""
        print("\n[2/7] 安装依赖")
        print("-" * 50)

        pip_cmd = self._get_pip_cmd()

        print("升级 pip...")
        result = subprocess.run(
            [pip_cmd, 'install', '--upgrade', 'pip', 'setuptools'],
            cwd=str(self.workspace)
        )
        if result.returncode != 0:
            print("✗ pip 升级失败")
            return False

        print("安装项目依赖...")
        result = subprocess.run(
            [pip_cmd, 'install', '-r', 'requirements.txt'],
            cwd=str(self.workspace)
        )
        if result.returncode != 0:
            print("✗ 依赖安装失败")
            return False

        print("✓ 依赖安装完成")
        return True

    def setup_env_file(self, mongodb_uri: str = None):
        """配置 .env 文件"""
        print("\n[3/7] 配置环境")
        print("-" * 50)

        env_file = self.workspace / '.env'

        if not mongodb_uri:
            if env_file.exists():
                print(f"✓ 使用现有的 .env 文件")
                return True

            example_file = self.workspace / '.env.example'
            if example_file.exists():
                print(f"复制 .env.example 为 .env...")
                shutil.copy(example_file, env_file)
                print(f"✓ .env 文件已创建，请修改其中的 MONGODB_URI")
                return True
            else:
                print("✗ .env.example 不存在")
                return False
        else:
            print("创建 .env 文件...")
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(f"MONGODB_URI={mongodb_uri}\n")
                f.write("DATABASE_NAME=sit\n")
                f.write("LOG_LEVEL=INFO\n")
            print("✓ .env 文件已创建")
            return True

    def test_connection(self):
        """测试数据库连接"""
        print("\n[4/7] 测试连接")
        print("-" * 50)

        python_cmd = self._get_python_cmd()

        test_code = """
import sys
from database import get_db_connection

print("测试数据库连接...")
conn = get_db_connection()
if conn.connect():
    print("✓ 数据库连接成功")
    conn.close()
    sys.exit(0)
else:
    print("✗ 数据库连接失败")
    sys.exit(1)
"""

        result = subprocess.run(
            [python_cmd, '-c', test_code],
            cwd=str(self.workspace)
        )

        return result.returncode == 0

    def execute_validation(self, time_range: str = 'today',
                          export_all: bool = True):
        """执行验证"""
        print("\n[5/7] 执行验证")
        print("-" * 50)

        # 创建输出目录
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        python_cmd = self._get_python_cmd()

        cmd = [python_cmd, 'jenkins_cli.py']

        # 添加时间范围参数
        if time_range == 'today':
            cmd.append('--today')
        elif time_range == 'this-week':
            cmd.append('--this-week')
        elif time_range == 'this-month':
            cmd.append('--this-month')
        else:
            cmd.extend(['--last-days', str(time_range)])

        # 添加导出选项
        if export_all:
            cmd.extend(['--export-all', '--output', str(self.reports_dir)])

        # 添加日志
        cmd.extend(['--log-file', str(self.logs_dir / 'validation.log')])

        print(f"命令: {' '.join(cmd)}")
        print()

        result = subprocess.run(cmd, cwd=str(self.workspace))

        return result.returncode

    def generate_reports(self):
        """生成报告"""
        print("\n[6/7] 生成报告")
        print("-" * 50)

        # 查找生成的报告文件
        xml_files = list(self.reports_dir.glob('test-results*.xml'))
        json_files = list(self.reports_dir.glob('validation-report*.json'))
        csv_files = list(self.reports_dir.glob('validation-errors*.csv'))

        print(f"JUnit XML 文件: {len(xml_files)}")
        for f in xml_files:
            print(f"  - {f.name}")

        print(f"JSON 报告文件: {len(json_files)}")
        for f in json_files:
            print(f"  - {f.name}")

        print(f"CSV 报告文件: {len(csv_files)}")
        for f in csv_files:
            print(f"  - {f.name}")

        if xml_files or json_files or csv_files:
            print("✓ 报告生成完成")
            return True
        else:
            print("⚠ 未生成任何报告（可能是时间范围内没有数据）")
            return True

    def upload_artifacts(self):
        """上传构件"""
        print("\n[7/7] 上传构件")
        print("-" * 50)

        if not self.reports_dir.exists():
            print("✗ 报告目录不存在")
            return False

        artifact_files = []
        artifact_files.extend(self.reports_dir.glob('**/*'))
        artifact_files.extend(self.logs_dir.glob('**/*'))

        print(f"收集构件: {len(artifact_files)} 个文件")
        for f in artifact_files[:5]:
            print(f"  - {f.relative_to(self.workspace)}")
        if len(artifact_files) > 5:
            print(f"  ... 以及 {len(artifact_files) - 5} 个其他文件")

        print("✓ 构件上传完成（本地模拟）")
        return True

    def run_full_build(self, time_range: str = 'today',
                      mongodb_uri: str = None,
                      test_connection: bool = True):
        """运行完整的构建流程"""
        print("\n" + "="*70)
        print("本地 Jenkins 构建模拟")
        print("="*70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"工作目录: {self.workspace}")
        print()

        # 执行各个步骤
        if not self.setup_virtual_env():
            return 2

        if not self.install_dependencies():
            return 2

        if not self.setup_env_file(mongodb_uri):
            return 2

        if test_connection:
            if not self.test_connection():
                print("✗ 数据库连接测试失败")
                return 2

        exit_code = self.execute_validation(time_range)

        if not self.generate_reports():
            return 2

        if not self.upload_artifacts():
            return 2

        print("\n" + "="*70)
        print("构建完成")
        print("="*70)
        print(f"报告输出目录: {self.reports_dir}")
        print(f"日志输出目录: {self.logs_dir}")
        print()

        return exit_code

    def _get_pip_cmd(self) -> str:
        """获取 pip 命令"""
        if sys.platform == 'win32':
            return str(self.venv_path / 'Scripts' / 'pip')
        else:
            return str(self.venv_path / 'bin' / 'pip')

    def _get_python_cmd(self) -> str:
        """获取 python 命令"""
        if sys.platform == 'win32':
            return str(self.venv_path / 'Scripts' / 'python')
        else:
            return str(self.venv_path / 'bin' / 'python')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='本地 Jenkins 构建模拟器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:

  # 模拟今天的构建
  python jenkins_build.py

  # 模拟最近 7 天的构建
  python jenkins_build.py --time-range last-7-days

  # 指定 MongoDB URI
  python jenkins_build.py --mongodb-uri "mongodb+srv://user:pass@host/db"

  # 跳过连接测试（快速运行）
  python jenkins_build.py --skip-test
        '''
    )

    parser.add_argument(
        '--time-range',
        choices=['today', 'this-week', 'this-month', '7', '30'],
        default='today',
        help='验证时间范围'
    )
    parser.add_argument(
        '--mongodb-uri',
        help='MongoDB 连接字符串'
    )
    parser.add_argument(
        '--workspace',
        default='.',
        help='工作目录'
    )
    parser.add_argument(
        '--skip-test',
        action='store_true',
        help='跳过数据库连接测试'
    )

    args = parser.parse_args()

    try:
        build = LocalJenkinsBuild(workspace=args.workspace)
        exit_code = build.run_full_build(
            time_range=args.time_range,
            mongodb_uri=args.mongodb_uri,
            test_connection=not args.skip_test
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断构建")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n✗ 构建异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()

