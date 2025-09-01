@echo off
REM Quick Bot Testing Commands for Windows

echo 🤖 WorkspaceAI Bot Enhancement Testing
echo ======================================

if "%1"=="full" (
    echo Running full automated test suite...
    python tests/automated_bot_testing.py
    goto :end
)

if "%1"=="quick" (
    echo Running quick validation test...
    python tests/quick_test_commands.py quick
    goto :end
)

if "%1"=="context" (
    echo Testing context awareness...
    python tests/quick_test_commands.py context
    goto :end
)

if "%1"=="single" (
    echo Testing complex single scenario...
    python tests/quick_test_commands.py single
    goto :end
)

if "%1"=="benchmark" (
    echo Running performance benchmark...
    python tests/quick_test_commands.py benchmark
    goto :end
)

if "%1"=="report" (
    echo Showing latest test report...
    python tests/quick_test_commands.py report
    goto :end
)

if "%1"=="all" (
    echo Running all test types...
    python tests/quick_test_commands.py quick
    python tests/quick_test_commands.py context
    python tests/quick_test_commands.py single
    python tests/quick_test_commands.py benchmark
    python tests/automated_bot_testing.py
    goto :end
)

echo Usage: test_bot.bat [command]
echo.
echo Available commands:
echo   full      - Complete automated test suite
echo   quick     - Quick validation (3 scenarios)
echo   context   - Context awareness test
echo   single    - Single complex scenario
echo   benchmark - Performance benchmark
echo   report    - Show latest results
echo   all       - Run all tests
echo.
echo Examples:
echo   test_bot.bat quick
echo   test_bot.bat full
echo   test_bot.bat all

:end
