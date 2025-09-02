@echo off
REM Quick Tool Detection Testing - Windows Batch Script
echo 🎯 WorkspaceAI Tool Detection Testing
echo ===========================================

:menu
echo.
echo Available Tests:
echo 1. Quick Tool Detection Test (10 scenarios)
echo 2. Interactive Testing Session
echo 3. Run Original Quick Test 
echo 4. Run Context Test
echo 5. Run Single Scenario Test
echo 6. Show Latest Results
echo 7. Exit
echo.
set /p choice="Choose test (1-7): "

if "%choice%"=="1" (
    echo.
    echo Running Quick Tool Detection Test...
    python tests/quick_tool_test.py
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo Starting Interactive Testing Session...
    python tests/interactive_tool_detection.py
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo Running Original Quick Test...
    python tests/quick_test_commands.py quick
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo Running Context Test...
    python tests/quick_test_commands.py context
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo Running Single Scenario Test...
    python tests/quick_test_commands.py single
    goto menu
)

if "%choice%"=="6" (
    echo.
    echo Showing Latest Results...
    python tests/quick_test_commands.py report
    goto menu
)

if "%choice%"=="7" (
    echo.
    echo 👋 Testing complete!
    exit /b 0
)

echo ❌ Invalid choice. Please try again.
goto menu
