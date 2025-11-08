#!/bin/bash
# Quick test script for single agent

echo "🧪 Testing Single Agent Setup"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ ERROR: docker-compose.yml not found!"
    echo "   You're in: $(pwd)"
    echo "   Run this from: .../template/"
    exit 1
fi

echo "✅ In correct directory"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Check orchestrator
echo "🔍 Checking orchestrator..."
if ! curl -s http://localhost:8765/health > /dev/null 2>&1; then
    echo "⚠️  Orchestrator not running, starting it..."
    docker-compose up -d redis orchestrator-api
    sleep 8
fi

HEALTH=$(curl -s http://localhost:8765/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Orchestrator is healthy"
else
    echo "❌ Orchestrator is not healthy"
    exit 1
fi
echo ""

# Check tasks
echo "📋 Checking tasks..."
TASKS=$(curl -s http://localhost:8765/status | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"{d['stats']['pending_tasks']} pending, {d['stats']['completed_tasks']} completed, {d['stats']['failed_tasks']} failed\")")
echo "   Tasks: $TASKS"
echo ""

# Check Python venv
if [ ! -d ".venv" ]; then
    echo "⚠️  Creating Python virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Check packages
if ! python3 -c "import redis" 2>/dev/null; then
    echo "📦 Installing Python packages..."
    pip install -q -r tools/orchestrator/requirements.txt
fi
echo "✅ Python packages installed"
echo ""

echo "======================================"
echo "✅ ALL CHECKS PASSED!"
echo ""
echo "🚀 Ready to start agent. Run:"
echo "   ./orchestrate.sh"
echo ""
echo "Or test with:"
echo "   python3 tools/orchestrator/agent_client.py --orchestrator-url=http://localhost:8765 --project-root=$(pwd)"
