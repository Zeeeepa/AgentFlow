#!/bin/bash
#
# Quick test script for Z.AI + AgentFlow Research Workflow
#
# Usage: ./scripts/test_zai_workflow.sh
#

set -e

echo "=================================="
echo "Z.AI + AgentFlow Workflow Test"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

echo "✅ Python3 found"

# Set Z.AI credentials
export ANTHROPIC_AUTH_TOKEN="${ANTHROPIC_AUTH_TOKEN:-665b963943b647dc9501dff942afb877.A47LrMc7sgGjyfBJ}"
export ANTHROPIC_BASE_URL="${ANTHROPIC_BASE_URL:-https://api.z.ai/api/anthropic}"
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-glm-4.6}"

echo "✅ Z.AI credentials configured"
echo "   Base URL: $ANTHROPIC_BASE_URL"
echo "   Model: $ANTHROPIC_MODEL"

# Run simple test
echo ""
echo "Running simple workflow test..."
python3 scripts/research_report_workflow.py --test

echo ""
echo "✅ Test completed successfully!"
