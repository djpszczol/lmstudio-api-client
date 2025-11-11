#!/bin/bash
# Demo script to showcase LM Studio CLI Client features

echo "🎨 LM Studio CLI Client Demo"
echo "================================"
echo ""

# Test 1: Single message
echo "📝 Test 1: Single message query"
./lm.sh -m "What is Python?"
echo ""
echo "Press Enter to continue..."
read

# Test 2: List sessions
echo "📋 Test 2: List all sessions"
./lm.sh -l
echo ""
echo "Press Enter to continue..."
read

# Test 3: Show statistics
echo "📊 Test 3: Show usage statistics"
./lm.sh --stats
echo ""
echo "Press Enter to continue..."
read

# Test 4: Interactive mode demo
echo "🎭 Test 4: Starting interactive mode"
echo "Try these commands:"
echo "  - Ask a question"
echo "  - Type '/help' to see all commands"
echo "  - Type '/stats' to see statistics"
echo "  - Type '/exit' to quit"
echo ""
./lm.sh
