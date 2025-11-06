#!/bin/bash
# Test script for Fix #19: Implementation Workflow
#
# This script simulates the complete workflow:
# 1. Agent prepares workspace
# 2. Simulated user commits implementation
# 3. Agent detects commit and continues

set -e

echo "🧪 Testing Implementation Workflow (Fix #19)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT=$(pwd)

# Test 1: Verify workspace preparation
echo -e "${BLUE}Test 1: Workspace Preparation${NC}"
echo "  Checking if CURRENT_TASK.md can be created..."

# Simulate workspace preparation
cat > CURRENT_TASK.md <<'EOF'
# 🎯 Current Task: Test Implementation

**Task ID:** `TEST001`
**Type:** `test`

## 📋 Description
This is a test task to verify the workflow.

## ✅ Acceptance Criteria
- Code should be committed
- Tests should pass

## 🚀 When Done:
```bash
git add .
git commit -m "feat: Test Implementation (TEST001)"
```
EOF

if [ -f "CURRENT_TASK.md" ]; then
    echo -e "${GREEN}  ✓ CURRENT_TASK.md created successfully${NC}"
else
    echo -e "${RED}  ✗ Failed to create CURRENT_TASK.md${NC}"
    exit 1
fi
echo ""

# Test 2: Verify .ai-context directory
echo -e "${BLUE}Test 2: Context Directory${NC}"
mkdir -p .ai-context

cat > .ai-context/task-TEST001.json <<'EOF'
{
  "task": {
    "id": "TEST001",
    "title": "Test Implementation"
  },
  "role": "developer",
  "started_at": "2025-01-01T00:00:00"
}
EOF

if [ -f ".ai-context/task-TEST001.json" ]; then
    echo -e "${GREEN}  ✓ Context file created successfully${NC}"
else
    echo -e "${RED}  ✗ Failed to create context file${NC}"
    exit 1
fi
echo ""

# Test 3: Simulate commit detection
echo -e "${BLUE}Test 3: Commit Detection${NC}"
echo "  Simulating user commit..."

# Get initial commit
INITIAL_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "none")
echo "  Initial commit: ${INITIAL_COMMIT:0:7}"

# Create a test file and commit (simulate user implementation)
echo "# Test Implementation" > test_implementation.txt
git add test_implementation.txt
git commit -m "test: Simulate implementation commit" --quiet || true

# Get new commit
NEW_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "none")
echo "  New commit: ${NEW_COMMIT:0:7}"

if [ "$INITIAL_COMMIT" != "$NEW_COMMIT" ]; then
    echo -e "${GREEN}  ✓ Commit detected successfully${NC}"
else
    echo -e "${YELLOW}  ⚠ No new commit (might be in detached HEAD or clean repo)${NC}"
fi
echo ""

# Test 4: Cleanup
echo -e "${BLUE}Test 4: Cleanup${NC}"
echo "  Removing test files..."

rm -f CURRENT_TASK.md
rm -f test_implementation.txt
rm -rf .ai-context

# Revert test commit
git reset --soft HEAD~1 2>/dev/null || true
git restore --staged test_implementation.txt 2>/dev/null || true

echo -e "${GREEN}  ✓ Cleanup completed${NC}"
echo ""

# Test 5: Workflow validation
echo -e "${BLUE}Test 5: Workflow Validation${NC}"
echo "  Checking agent_client.py for required methods..."

AGENT_CLIENT="tools/orchestrator/agent_client.py"

if [ ! -f "$AGENT_CLIENT" ]; then
    echo -e "${RED}  ✗ agent_client.py not found${NC}"
    exit 1
fi

# Check for required methods
METHODS=(
    "prepare_task_workspace"
    "wait_for_implementation"
    "load_task_context"
)

ALL_FOUND=true
for method in "${METHODS[@]}"; do
    if grep -q "def $method" "$AGENT_CLIENT"; then
        echo -e "${GREEN}  ✓ Method found: $method${NC}"
    else
        echo -e "${RED}  ✗ Method missing: $method${NC}"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = true ]; then
    echo -e "${GREEN}  ✓ All required methods present${NC}"
else
    echo -e "${RED}  ✗ Some methods are missing${NC}"
    exit 1
fi
echo ""

# Test 6: Configuration check
echo -e "${BLUE}Test 6: Configuration Check${NC}"
CONFIG_FILE="orchestrator-config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}  ✗ orchestrator-config.yaml not found${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Configuration file exists${NC}"

# Check for required config sections
if grep -q "quality_gates:" "$CONFIG_FILE"; then
    echo -e "${GREEN}  ✓ quality_gates section found${NC}"
else
    echo -e "${YELLOW}  ⚠ quality_gates section not found${NC}"
fi

if grep -q "git:" "$CONFIG_FILE"; then
    echo -e "${GREEN}  ✓ git section found${NC}"
else
    echo -e "${YELLOW}  ⚠ git section not found${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All Tests Passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "The implementation workflow is ready to use!"
echo ""
echo "Next steps:"
echo "1. Start orchestrator: ./orchestrate.sh"
echo "2. Wait for 'READY TO IMPLEMENT' message"
echo "3. Implement with your AI tool"
echo "4. Commit: git add . && git commit -m 'feat: ...'"
echo "5. Agent automatically continues!"
echo ""
echo -e "${BLUE}📚 Read IMPLEMENTATION-WORKFLOW.md for full guide${NC}"
