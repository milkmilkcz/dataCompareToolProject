# Jenkins 快速诊断脚本

Write-Host "========== Jenkins Python 诊断 ==========" -ForegroundColor Cyan

Write-Host ""
Write-Host "1. 检查当前目录"
Write-Host "   $(Get-Location)"

Write-Host ""
Write-Host "2. 测试 Python..."
try {
    $output = python --version 2>&1
    Write-Host "✓ Python 可用: $output"
} catch {
    Write-Host "⚠ Python 执行出错: $_"
}

Write-Host ""
Write-Host "3. 测试 pip..."
try {
    $output = pip --version 2>&1
    Write-Host "✓ pip 可用: $output"
} catch {
    Write-Host "⚠ pip 执行出错: $_"
}

Write-Host ""
Write-Host "4. 检查项目文件..."
$files = @(
    "config\requirements.txt",
    "setup.py",
    "src\data_validation_tool\cli\main.py"
)
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "✓ $f"
    } else {
        Write-Host "✗ 缺失: $f"
    }
}

Write-Host ""
Write-Host "5. 测试依赖导入..."
try {
    python -c "import pymongo; print('✓ pymongo 可用')" 2>&1
} catch {
    Write-Host "⚠ pymongo 不可用，需要安装"
}

Write-Host ""
Write-Host "========== 诊断完成 ==========" -ForegroundColor Cyan

Write-Host ""
Write-Host "如果有问题，请运行："
Write-Host "  pip install -r config\requirements.txt"

