# Сборка Tetris.exe через PyInstaller
# 1) Положите Expressway Free.ttf в папку fonts\
# 2) Запуск: powershell -ExecutionPolicy Bypass -File build.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$fontFiles = Get-ChildItem -Path "fonts" -Include *.ttf,*.otf -File -ErrorAction SilentlyContinue
if (-not $fontFiles) {
    Write-Host "Предупреждение: в fonts\ нет .ttf/.otf — exe соберётся со шрифтом Segoe UI." -ForegroundColor Yellow
}

python -m pip install -r requirements-build.txt

$addData = @(
    "Interface;Interface",
    "fonts;fonts"
)

$addDataArgs = $addData | ForEach-Object { "--add-data", $_ }

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name Tetris `
    @addDataArgs `
    --collect-submodules PyQt6 `
    main.py

Write-Host ""
Write-Host "Готово: dist\Tetris\Tetris.exe"
Write-Host "Переносите на другой ПК всю папку dist\Tetris"
