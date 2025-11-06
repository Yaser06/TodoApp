#!/bin/bash
# Fix #18: Redis Persistence Test Script
#
# This script tests if Redis data persists across container restarts

set -e

echo "🧪 Testing Redis Persistence..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test key
TEST_KEY="orchestrator:persistence:test"
TEST_VALUE="persistence_works_$(date +%s)"

echo "Step 1: Writing test data to Redis..."
docker exec ai-orchestrator-redis redis-cli SET "$TEST_KEY" "$TEST_VALUE"

# Verify write
WRITTEN_VALUE=$(docker exec ai-orchestrator-redis redis-cli GET "$TEST_KEY")
if [ "$WRITTEN_VALUE" != "$TEST_VALUE" ]; then
    echo -e "${RED}❌ Failed to write test data${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Test data written: $TEST_VALUE${NC}"
echo ""

echo "Step 2: Forcing Redis to save (BGSAVE)..."
docker exec ai-orchestrator-redis redis-cli BGSAVE
sleep 2
echo -e "${GREEN}✓ Background save initiated${NC}"
echo ""

echo "Step 3: Checking AOF file..."
AOF_EXISTS=$(docker exec ai-orchestrator-redis sh -c '[ -f /data/orchestrator.aof ] && echo "yes" || echo "no"')
if [ "$AOF_EXISTS" = "yes" ]; then
    AOF_SIZE=$(docker exec ai-orchestrator-redis sh -c 'ls -lh /data/orchestrator.aof | awk "{print \$5}"')
    echo -e "${GREEN}✓ AOF file exists: $AOF_SIZE${NC}"
else
    echo -e "${YELLOW}⚠️  AOF file not found (may not be created yet)${NC}"
fi
echo ""

echo "Step 4: Restarting Redis container..."
docker restart ai-orchestrator-redis
echo "Waiting for Redis to start..."
sleep 5

# Wait for Redis to be ready
MAX_WAIT=30
WAIT_COUNT=0
while ! docker exec ai-orchestrator-redis redis-cli ping > /dev/null 2>&1; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ Redis failed to start within ${MAX_WAIT}s${NC}"
        exit 1
    fi
    echo -ne "   Waiting... ${WAIT_COUNT}s\r"
done
echo -e "${GREEN}✓ Redis restarted and ready${NC}"
echo ""

echo "Step 5: Reading test data from Redis..."
RESTORED_VALUE=$(docker exec ai-orchestrator-redis redis-cli GET "$TEST_KEY")

if [ "$RESTORED_VALUE" = "$TEST_VALUE" ]; then
    echo -e "${GREEN}✅ SUCCESS: Data persisted across restart!${NC}"
    echo "   Original:  $TEST_VALUE"
    echo "   Restored:  $RESTORED_VALUE"
    echo ""
    echo -e "${GREEN}✅ Redis persistence is working correctly!${NC}"

    # Cleanup
    docker exec ai-orchestrator-redis redis-cli DEL "$TEST_KEY"

    exit 0
else
    echo -e "${RED}❌ FAILED: Data was lost after restart!${NC}"
    echo "   Original:  $TEST_VALUE"
    echo "   Restored:  $RESTORED_VALUE"
    echo ""
    echo -e "${RED}❌ Redis persistence is NOT working!${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check if volume is properly mounted:"
    echo "   docker volume inspect ai-project-starter-kit_redis-data"
    echo ""
    echo "2. Check Redis logs:"
    echo "   docker logs ai-orchestrator-redis"
    echo ""
    echo "3. Verify AOF file:"
    echo "   docker exec ai-orchestrator-redis ls -la /data/"

    exit 1
fi
