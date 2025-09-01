#!/bin/bash
# Quick Bot Testing Commands for Linux/Mac

echo "🤖 WorkspaceAI Bot Enhancement Testing"
echo "======================================"

case "$1" in
    "full")
        echo "Running full automated test suite..."
        python tests/automated_bot_testing.py
        ;;
    "quick")
        echo "Running quick validation test..."
        python tests/quick_test_commands.py quick
        ;;
    "context")
        echo "Testing context awareness..."
        python tests/quick_test_commands.py context
        ;;
    "single")
        echo "Testing complex single scenario..."
        python tests/quick_test_commands.py single
        ;;
    "benchmark")
        echo "Running performance benchmark..."
        python tests/quick_test_commands.py benchmark
        ;;
    "report")
        echo "Showing latest test report..."
        python tests/quick_test_commands.py report
        ;;
    "all")
        echo "Running all test types..."
        python tests/quick_test_commands.py quick
        python tests/quick_test_commands.py context
        python tests/quick_test_commands.py single
        python tests/quick_test_commands.py benchmark
        python tests/automated_bot_testing.py
        ;;
    *)
        echo "Usage: ./test_bot.sh [command]"
        echo ""
        echo "Available commands:"
        echo "  full      - Complete automated test suite"
        echo "  quick     - Quick validation (3 scenarios)"
        echo "  context   - Context awareness test"
        echo "  single    - Single complex scenario"
        echo "  benchmark - Performance benchmark"
        echo "  report    - Show latest results"
        echo "  all       - Run all tests"
        echo ""
        echo "Examples:"
        echo "  ./test_bot.sh quick"
        echo "  ./test_bot.sh full"
        echo "  ./test_bot.sh all"
        ;;
esac
