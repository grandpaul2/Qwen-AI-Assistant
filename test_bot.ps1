# Quick Bot Testing Commands for PowerShell
param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

Write-Host "🤖 WorkspaceAI Bot Enhancement Testing" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

switch ($Command.ToLower()) {
    "full" {
        Write-Host "Running full automated test suite..." -ForegroundColor Yellow
        python tests/automated_bot_testing.py
    }
    "quick" {
        Write-Host "Running quick validation test..." -ForegroundColor Yellow
        python tests/quick_test_commands.py quick
    }
    "context" {
        Write-Host "Testing context awareness..." -ForegroundColor Yellow
        python tests/quick_test_commands.py context
    }
    "single" {
        Write-Host "Testing complex single scenario..." -ForegroundColor Yellow
        python tests/quick_test_commands.py single
    }
    "benchmark" {
        Write-Host "Running performance benchmark..." -ForegroundColor Yellow
        python tests/quick_test_commands.py benchmark
    }
    "report" {
        Write-Host "Showing latest test report..." -ForegroundColor Yellow
        python tests/quick_test_commands.py report
    }
    "all" {
        Write-Host "Running all test types..." -ForegroundColor Yellow
        python tests/quick_test_commands.py quick
        python tests/quick_test_commands.py context
        python tests/quick_test_commands.py single
        python tests/quick_test_commands.py benchmark
        python tests/automated_bot_testing.py
    }
    default {
        Write-Host "Usage: .\test_bot.ps1 [command]" -ForegroundColor Green
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor White
        Write-Host "  full      - Complete automated test suite" -ForegroundColor Gray
        Write-Host "  quick     - Quick validation (3 scenarios)" -ForegroundColor Gray
        Write-Host "  context   - Context awareness test" -ForegroundColor Gray
        Write-Host "  single    - Single complex scenario" -ForegroundColor Gray
        Write-Host "  benchmark - Performance benchmark" -ForegroundColor Gray
        Write-Host "  report    - Show latest results" -ForegroundColor Gray
        Write-Host "  all       - Run all tests" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor White
        Write-Host "  .\test_bot.ps1 quick" -ForegroundColor Gray
        Write-Host "  .\test_bot.ps1 full" -ForegroundColor Gray
        Write-Host "  .\test_bot.ps1 all" -ForegroundColor Gray
    }
}
