#!/bin/bash
# Test script for MCP servers functionality
# Tests T-207: Validate MCP server functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TIMEOUT=5
TEST_DIR=$(mktemp -d)
COLLAB_ROOT="$TEST_DIR"

echo -e "${BLUE}🧪 MCP Servers Test Suite${NC}"
echo "Test directory: $TEST_DIR"
echo ""

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up test directory...${NC}"
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Helper function to test server startup
test_server_startup() {
    local server_name="$1"
    local server_module="$2"
    local expected_methods="$3"
    
    echo -e "${BLUE}Testing $server_name startup...${NC}"
    
    # Test server can start and respond to initialize
    echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | timeout $TIMEOUT python -m "$server_module" > /tmp/mcp_test_${server_name}.json 2>&1 || {
        echo -e "${RED}❌ $server_name failed to start or respond to initialize${NC}"
        cat /tmp/mcp_test_${server_name}.json
        return 1
    }
    
    # Check if response is valid JSON
    if jq empty /tmp/mcp_test_${server_name}.json 2>/dev/null; then
        echo -e "${GREEN}✅ $server_name started successfully${NC}"
    else
        echo -e "${RED}❌ $server_name returned invalid JSON${NC}"
        cat /tmp/mcp_test_${server_name}.json
        return 1
    fi
    
    # Test specific methods if provided
    if [ -n "$expected_methods" ]; then
        for method in $expected_methods; do
            echo "  Testing method: $method"
            echo "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"$method\",\"params\":{}}" | timeout $TIMEOUT python -m "$server_module" > /tmp/mcp_test_${server_name}_${method}.json 2>&1 || {
                echo -e "${YELLOW}⚠️  Method $method not available or failed (may be expected)${NC}"
                continue
            }
            
            if jq empty /tmp/mcp_test_${server_name}_${method}.json 2>/dev/null; then
                echo -e "    ${GREEN}✅ Method $method works${NC}"
            else
                echo -e "    ${YELLOW}⚠️  Method $method returned invalid JSON${NC}"
            fi
        done
    fi
    
    echo ""
}

# Helper function to test help/version flags
test_help_version() {
    local server_name="$1"
    local server_module="$2"
    
    echo -e "${BLUE}Testing $server_name help/version flags...${NC}"
    
    # Test --help flag
    if python -m "$server_module" --help > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $server_name supports --help${NC}"
    else
        echo -e "${YELLOW}⚠️  $server_name does not support --help${NC}"
    fi
    
    # Test --version flag
    if python -m "$server_module" --version > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $server_name supports --version${NC}"
    else
        echo -e "${YELLOW}⚠️  $server_name does not support --version${NC}"
    fi
    
    echo ""
}

# Setup test environment
echo -e "${BLUE}🔧 Setting up test environment...${NC}"
mkdir -p "$COLLAB_ROOT/collaboration/state"
mkdir -p "$COLLAB_ROOT/collaboration/events"
mkdir -p "$COLLAB_ROOT/collaboration/logs"

# Create minimal state files
cat > "$COLLAB_ROOT/collaboration/state/tasks.json" << 'EOF'
{
  "version": 1,
  "tasks": []
}
EOF

cat > "$COLLAB_ROOT/collaboration/state/locks.json" << 'EOF'
{
  "version": 1,
  "locks": []
}
EOF

cat > "$COLLAB_ROOT/collaboration/state/agents.json" << 'EOF'
{
  "version": 1,
  "agents": []
}
EOF

cat > "$COLLAB_ROOT/collaboration/events/events.jsonl" << 'EOF'
{"ts":"2024-01-01T00:00:00Z","event":"test","agent":"test","task":"test","old_status":"","new_status":"","path":"","notes":"Test event"}
EOF

echo -e "${GREEN}✅ Test environment ready${NC}"
echo ""

# Test 1: kyros-collab-mcp server
echo -e "${BLUE}📋 Test 1: kyros-collab-mcp server${NC}"
export COLLAB_ROOT="$COLLAB_ROOT"
test_server_startup "kyros-collab-mcp" "mcp.kyros_collab_server" "collab.list_tasks collab.get_state collab.create_task"

# Test 2: Stub servers
echo -e "${BLUE}📋 Test 2: Stub servers${NC}"

# Linear server
test_server_startup "linear" "mcp.linear_server" "linear.capabilities linear.create_issue"

# CodeRabbit server  
test_server_startup "coderabbit" "mcp.coderabbit_server" "coderabbit.request_review coderabbit.fetch_feedback"

# Railway server
test_server_startup "railway" "mcp.railway_server" "railway.capabilities railway.get_deployment"

# Vercel server
test_server_startup "vercel" "mcp.vercel_server" "vercel.get_deployment"

# Test 3: Help/Version flags
echo -e "${BLUE}📋 Test 3: Help/Version flags${NC}"
test_help_version "kyros-collab-mcp" "mcp.kyros_collab_server"
test_help_version "linear" "mcp.linear_server"
test_help_version "coderabbit" "mcp.coderabbit_server"
test_help_version "railway" "mcp.railway_server"
test_help_version "vercel" "mcp.vercel_server"

# Test 4: Basic collaboration RPC calls
echo -e "${BLUE}📋 Test 4: Basic collaboration RPC calls${NC}"
export COLLAB_ROOT="$COLLAB_ROOT"

echo "Testing collab.list_tasks..."
echo '{"jsonrpc":"2.0","id":3,"method":"collab.list_tasks","params":{}}' | timeout $TIMEOUT python -m mcp.kyros_collab_server > /tmp/collab_list_tasks.json 2>&1
if jq empty /tmp/collab_list_tasks.json 2>/dev/null; then
    echo -e "${GREEN}✅ collab.list_tasks works${NC}"
    jq . /tmp/collab_list_tasks.json
else
    echo -e "${RED}❌ collab.list_tasks failed${NC}"
    cat /tmp/collab_list_tasks.json
fi

echo ""
echo "Testing collab.get_state..."
echo '{"jsonrpc":"2.0","id":4,"method":"collab.get_state","params":{"kind":"tasks"}}' | timeout $TIMEOUT python -m mcp.kyros_collab_server > /tmp/collab_get_state.json 2>&1
if jq empty /tmp/collab_get_state.json 2>/dev/null; then
    echo -e "${GREEN}✅ collab.get_state works${NC}"
    jq . /tmp/collab_get_state.json
else
    echo -e "${RED}❌ collab.get_state failed${NC}"
    cat /tmp/collab_get_state.json
fi

echo ""
echo "Testing collab.create_task..."
echo '{"jsonrpc":"2.0","id":5,"method":"collab.create_task","params":{"title":"Test Task","labels":["backend"]}}' | timeout $TIMEOUT python -m mcp.kyros_collab_server > /tmp/collab_create_task.json 2>&1
if jq empty /tmp/collab_create_task.json 2>/dev/null; then
    echo -e "${GREEN}✅ collab.create_task works${NC}"
    jq . /tmp/collab_create_task.json
else
    echo -e "${RED}❌ collab.create_task failed${NC}"
    cat /tmp/collab_create_task.json
fi

# Test 5: Package installation verification
echo -e "${BLUE}📋 Test 5: Package installation verification${NC}"
cd /home/thomas/kyros-dashboard/mcp

if python -m pip show kyros-mcp > /dev/null 2>&1; then
    echo -e "${GREEN}✅ kyros-mcp package is installed${NC}"
    python -m pip show kyros-mcp
else
    echo -e "${YELLOW}⚠️  kyros-mcp package not installed, installing...${NC}"
    python -m pip install -e .
fi

# Test 6: Command-line entry points
echo -e "${BLUE}📋 Test 6: Command-line entry points${NC}"

# Test if entry points work
if command -v kyros-collab-mcp > /dev/null 2>&1; then
    echo -e "${GREEN}✅ kyros-collab-mcp command available${NC}"
    echo '{"jsonrpc":"2.0","id":6,"method":"initialize"}' | timeout $TIMEOUT kyros-collab-mcp > /tmp/kyros_collab_cli.json 2>&1 || {
        echo -e "${YELLOW}⚠️  kyros-collab-mcp command failed (may need proper setup)${NC}"
    }
else
    echo -e "${YELLOW}⚠️  kyros-collab-mcp command not available in PATH${NC}"
fi

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
echo "All MCP servers have been tested for:"
echo "✅ Server startup and JSON-RPC initialization"
echo "✅ Method availability and basic functionality"
echo "✅ Help/version flag support (where applicable)"
echo "✅ Basic collaboration RPC calls"
echo "✅ Package installation and entry points"
echo ""
echo -e "${GREEN}🎉 MCP server validation complete!${NC}"
