#!/bin/bash
set -e

# AI Multi-Agent Orchestration Entry Point
#
# Usage:
#   Terminal 1: ./orchestrate.sh
#   Terminal 2: ./orchestrate.sh
#   Terminal 3: ./orchestrate.sh
#   ... (each terminal becomes an AI agent)

PROJECT_ROOT=$(pwd)
ORCHESTRATOR_URL="http://localhost:8765"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🤖 AI Multi-Agent Orchestration System${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if infrastructure is running
check_infrastructure() {
    echo -e "${BLUE}🔍 Checking infrastructure...${NC}"

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running!${NC}"
        echo -e "${YELLOW}   Please start Docker Desktop and try again.${NC}"
        exit 1
    fi

    # Check if orchestrator is responding
    if curl -s "$ORCHESTRATOR_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Orchestrator is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Orchestrator not running${NC}"
        return 1
    fi
}

# Start infrastructure
start_infrastructure() {
    echo -e "${BLUE}📦 Starting infrastructure...${NC}"

    # Check if docker-compose.yml exists
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "${RED}❌ docker-compose.yml not found!${NC}"
        exit 1
    fi

    # Start Docker services
    echo -e "${BLUE}   Starting Redis and Orchestrator API...${NC}"
    docker-compose up -d redis orchestrator-api

    # Wait for services to be ready
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"

    max_wait=30
    wait_count=0

    while ! curl -s "$ORCHESTRATOR_URL/health" > /dev/null 2>&1; do
        sleep 1
        wait_count=$((wait_count + 1))

        if [ $wait_count -ge $max_wait ]; then
            echo -e "${RED}❌ Orchestrator failed to start within ${max_wait}s${NC}"
            echo -e "${YELLOW}   Check logs: docker-compose logs orchestrator-api${NC}"
            exit 1
        fi

        echo -ne "${BLUE}   Waiting... ${wait_count}s${NC}\r"
    done

    echo -e "${GREEN}✅ Infrastructure ready!${NC}"
    echo ""
}

# Show orchestrator status
show_status() {
    echo -e "${BLUE}📊 Orchestrator Status:${NC}"

    status_json=$(curl -s "$ORCHESTRATOR_URL/status")

    if [ $? -eq 0 ]; then
        # Extract stats using basic parsing (no jq required)
        total_agents=$(echo "$status_json" | grep -o '"total_agents":[0-9]*' | cut -d':' -f2)
        active_agents=$(echo "$status_json" | grep -o '"active_agents":[0-9]*' | cut -d':' -f2)
        total_tasks=$(echo "$status_json" | grep -o '"total_tasks":[0-9]*' | cut -d':' -f2)
        completed_tasks=$(echo "$status_json" | grep -o '"completed_tasks":[0-9]*' | cut -d':' -f2)
        current_phase=$(echo "$status_json" | grep -o '"current_phase":[0-9]*' | cut -d':' -f2)

        echo -e "   Agents: ${GREEN}${active_agents:-0}${NC} active, ${total_agents:-0} total"
        echo -e "   Tasks: ${GREEN}${completed_tasks:-0}${NC}/${total_tasks:-0} completed"
        echo -e "   Phase: ${BLUE}${current_phase:-N/A}${NC}"
    else
        echo -e "${RED}   Failed to get status${NC}"
    fi

    echo ""
}

# Run agent client
run_agent() {
    echo -e "${GREEN}🔌 Connecting to orchestrator...${NC}"
    echo ""

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found!${NC}"
        exit 1
    fi

    # Create virtual environment if needed
    VENV_DIR="$PROJECT_ROOT/.venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
        python3 -m venv "$VENV_DIR"
    fi

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Install required Python packages from requirements.txt
    # Check if packages are installed by testing multiple imports
    PACKAGES_INSTALLED=true
    for pkg in redis requests yaml flask; do
        if ! python3 -c "import $pkg" 2>/dev/null; then
            PACKAGES_INSTALLED=false
            break
        fi
    done

    if [ "$PACKAGES_INSTALLED" = false ]; then
        if [ -f "tools/orchestrator/requirements.txt" ]; then
            echo -e "${YELLOW}📦 Installing required Python packages...${NC}"
            pip install -q -r tools/orchestrator/requirements.txt
        else
            # Fallback: install minimal packages
            echo -e "${YELLOW}📦 Installing required Python packages...${NC}"
            pip install -q requests pyyaml redis flask gitpython anthropic
        fi
    fi

    # Run agent client
    python3 tools/orchestrator/agent_client.py \
        --orchestrator-url="$ORCHESTRATOR_URL" \
        --project-root="$PROJECT_ROOT"
}

# Main execution
main() {
    # Check infrastructure
    if ! check_infrastructure; then
        # Infrastructure not running, start it
        start_infrastructure
    fi

    # Show status
    show_status

    # Run agent
    run_agent
}

# Handle arguments
case "${1:-}" in
    status)
        check_infrastructure
        show_status
        ;;
    stop)
        echo -e "${BLUE}🛑 Stopping infrastructure...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Infrastructure stopped${NC}"
        ;;
    logs)
        docker-compose logs -f orchestrator-api
        ;;
    cleanup)
        echo -e "${BLUE}🧹 Cleaning up stuck tasks...${NC}"
        if ! check_infrastructure; then
            echo -e "${RED}❌ Orchestrator not running!${NC}"
            exit 1
        fi

        # Trigger cleanup via API
        cleanup_result=$(curl -s -X POST "$ORCHESTRATOR_URL/cleanup" 2>&1)

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Cleanup completed${NC}"
            echo "$cleanup_result" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Recovered: {d.get('recovered', 0)} tasks\"); print(f\"   Failed reset: {d.get('failed_reset', 0)} tasks\")" 2>/dev/null || echo "$cleanup_result"
        else
            echo -e "${RED}❌ Cleanup failed${NC}"
        fi
        ;;
    reset)
        echo -e "${YELLOW}⚠️  Resetting orchestrator state (full reset)...${NC}"
        docker-compose down
        docker volume rm $(basename $(pwd))_redis-data 2>/dev/null || true
        echo -e "${GREEN}✅ State reset${NC}"
        ;;
    test-persistence)
        echo -e "${BLUE}🧪 Testing Redis persistence...${NC}"
        bash tools/orchestrator/test_redis_persistence.sh
        ;;
    test-workflow)
        echo -e "${BLUE}🧪 Testing implementation workflow...${NC}"
        bash tools/orchestrator/test_implementation_flow.sh
        ;;
    help|--help|-h)
        echo "AI Multi-Agent Orchestration System"
        echo ""
        echo "Usage:"
        echo "  ./orchestrate.sh                Start an AI agent (run in multiple terminals)"
        echo "  ./orchestrate.sh status         Show orchestrator status"
        echo "  ./orchestrate.sh cleanup        Clean stuck tasks (keep completed tasks)"
        echo "  ./orchestrate.sh reset          Full reset (delete all Redis data)"
        echo "  ./orchestrate.sh stop           Stop infrastructure"
        echo "  ./orchestrate.sh logs           View orchestrator logs"
        echo "  ./orchestrate.sh test-persistence  Test Redis data persistence"
        echo "  ./orchestrate.sh test-workflow  Test implementation workflow (Fix #19)"
        echo "  ./orchestrate.sh help           Show this help"
        echo ""
        echo "Difference between cleanup and reset:"
        echo "  cleanup: Recovers stuck/failed tasks → pending (keeps progress)"
        echo "  reset:   Deletes ALL data, fresh start (loses all progress)"
        echo ""
        ;;
    *)
        main
        ;;
esac
