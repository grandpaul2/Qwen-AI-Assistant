# Quick Tool Detection Testing - PowerShell Script
Write-Host "🎯 WorkspaceAI Tool Detection Testing" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

function Show-Menu {
    Write-Host ""
    Write-Host "Available Tests:" -ForegroundColor Yellow
    Write-Host "1. Quick Tool Detection Test (10 scenarios)" -ForegroundColor White
    Write-Host "2. Interactive Testing Session" -ForegroundColor White
    Write-Host "3. Run Original Quick Test" -ForegroundColor White
    Write-Host "4. Run Context Test" -ForegroundColor White
    Write-Host "5. Run Single Scenario Test" -ForegroundColor White
    Write-Host "6. Show Latest Results" -ForegroundColor White
    Write-Host "7. Exit" -ForegroundColor White
    Write-Host ""
}

function Run-Test {
    param($TestCommand)
    
    Write-Host ""
    Write-Host "Running: $TestCommand" -ForegroundColor Green
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    try {
        & python $TestCommand
    }
    catch {
        Write-Host "❌ Error running test: $_" -ForegroundColor Red
    }
}

# Main menu loop
do {
    Show-Menu
    $choice = Read-Host "Choose test (1-7)"
    
    switch ($choice) {
        "1" {
            Run-Test "tests/quick_tool_test.py"
        }
        "2" {
            Run-Test "tests/interactive_tool_detection.py"
        }
        "3" {
            Run-Test "tests/quick_test_commands.py quick"
        }
        "4" {
            Run-Test "tests/quick_test_commands.py context"
        }
        "5" {
            Run-Test "tests/quick_test_commands.py single"
        }
        "6" {
            Run-Test "tests/quick_test_commands.py report"
        }
        "7" {
            Write-Host ""
            Write-Host "👋 Testing complete!" -ForegroundColor Green
            break
        }
        default {
            Write-Host "❌ Invalid choice. Please try again." -ForegroundColor Red
        }
    }
} while ($choice -ne "7")

Write-Host ""
Write-Host "For manual testing, start the bot with: python main.py" -ForegroundColor Cyan
