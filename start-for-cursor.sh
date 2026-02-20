#!/usr/bin/env bash
# Start MCP servers and remind you to reload Cursor
# Run this after restarting Docker so Cursor can see the MCP servers again.
#
# Why: Cursor connects to MCP servers only at startup. If Docker (and the
# servers) weren't running when you opened Cursor, those servers won't appear
# until you reload the window. This script starts the stack and tells you to reload.

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting MCP servers for Cursor...${NC}"
echo ""

if [ -f deploy.sh ]; then
    ./deploy.sh start all
else
    docker compose up -d
fi

# Wait for MCP ports to be reachable (so Cursor has something to connect to)
PORTS="8000 8001 8002 8003 8004 8005 8006"
MAX_WAIT=90
ELAPSED=0

echo ""
echo -e "${YELLOW}Waiting for MCP ports (up to ${MAX_WAIT}s)...${NC}"

for port in $PORTS; do
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        if (command -v nc >/dev/null 2>&1 && nc -z 127.0.0.1 $port 2>/dev/null) || \
           (command -v curl >/dev/null 2>&1 && curl -s -o /dev/null --connect-timeout 1 "http://127.0.0.1:$port/" 2>/dev/null); then
            echo -e "  ${GREEN}✓${NC} port $port"
            break
        fi
        sleep 2
        ELAPSED=$((ELAPSED + 2))
    done
done

echo ""
echo -e "${GREEN}MCP servers are up.${NC}"
echo ""
echo -e "${YELLOW}To see them in Cursor, reload the window:${NC}"
echo "  • Mac:    Cmd+Shift+P  →  \"Developer: Reload Window\"  →  Enter"
echo "  • Win/Linux: Ctrl+Shift+P  →  \"Developer: Reload Window\"  →  Enter"
echo ""
echo "After reload, Cursor will reconnect to the MCP servers."
echo ""
