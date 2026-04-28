"""
Setup script for data-validation-tool
"""

from setuptools import setup, find_packages

with open("config/requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("docs/README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="data-validation-tool",
    version="1.0.0",
    author="Data Validation Team",
    author_email="dev@example.com",
    description="MongoDB 数据���比验证工具，支持 Jenkins CI/CD 集成",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/data-validation-tool",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
        "jenkins": [
            "lxml>=4.6.0",  # For XML processing
        ],
    },
    entry_points={
        "console_scripts": [
            "data-validation=main:main",
            "data-validation-cli=cli:main",
            "data-validation-jenkins=jenkins_cli:main",
            "data-validation-build=jenkins_build:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
