#!/bin/bash
# Quick start script for Task Board

set -e

echo "🚀 Starting Task Board..."
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to task-board directory
cd "$(dirname "$0")"

# Check if already running
if docker ps | grep -q task-board; then
    echo "✅ Task board is already running"
    PORT=$(docker port task-board 9090 2>/dev/null | cut -d':' -f2 || echo "9090")
    echo "📍 URL: http://localhost:$PORT"
    exit 0
fi

# Start with docker-compose
echo "🐳 Starting Docker container..."
docker-compose up -d

# Wait for container to be healthy
echo "⏳ Waiting for service to start..."
sleep 3

# Find the actual port
PORT=$(docker port task-board 9090 2>/dev/null | cut -d':' -f2 || echo "9090")

echo
echo "=" * 60
echo "✅ Task Board Started Successfully!"
echo "=" * 60
echo "📍 URL: http://localhost:$PORT"
echo "📊 Monitoring: memory-bank/work/backlog.yaml"
echo
echo "💡 Tip: Leave this running while agent works"
echo "🛑 To stop: cd tools/task-board && docker-compose down"
echo "=" * 60

# Try to open browser (optional)
if command -v open > /dev/null; then
    echo
    read -p "Open browser now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "http://localhost:$PORT"
    fi
fi
