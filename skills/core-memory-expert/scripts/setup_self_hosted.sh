#!/usr/bin/env bash
#
# Setup RedPlanet Core Self-Hosted Instance
#
# Automates self-hosting setup:
# 1. Checks Docker prerequisites
# 2. Clones Core repository
# 3. Configures environment variables
# 4. Launches containers
# 5. Verifies services
#
# Usage:
#     bash setup_self_hosted.sh [--clone-dir ./core] [--openai-key sk-...]
#
# Examples:
#     bash setup_self_hosted.sh
#     bash setup_self_hosted.sh --clone-dir ~/projects/core
#     bash setup_self_hosted.sh --openai-key sk-abc123
#
# Requirements:
#     - Docker 20.10.0+
#     - Docker Compose 2.20.0+
#     - OpenAI API key
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CLONE_DIR="./core"
OPENAI_KEY=""
REPO_URL="https://github.com/RedPlanetHQ/core.git"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clone-dir)
            CLONE_DIR="$2"
            shift 2
            ;;
        --openai-key)
            OPENAI_KEY="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Usage: $0 [--clone-dir DIR] [--openai-key KEY]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🚀 RedPlanet Core Self-Hosted Setup${NC}"
echo "======================================"
echo ""

# Check Docker
echo -e "${BLUE}🔍 Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    echo "   Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
echo -e "${GREEN}✅ Docker found: $DOCKER_VERSION${NC}"

# Check Docker Compose
echo -e "${BLUE}🔍 Checking Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found${NC}"
    echo "   Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

COMPOSE_VERSION=$(docker compose version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
echo -e "${GREEN}✅ Docker Compose found: $COMPOSE_VERSION${NC}"

# Check OpenAI key
echo ""
echo -e "${BLUE}🔑 Checking OpenAI API Key...${NC}"
if [ -z "$OPENAI_KEY" ]; then
    echo -e "${YELLOW}⚠️  No OpenAI key provided via --openai-key${NC}"
    echo ""
    read -rsp "Enter OpenAI API key (sk-...): " OPENAI_KEY
    echo ""
    if [ -z "$OPENAI_KEY" ]; then
        echo -e "${RED}❌ OpenAI API key required for Core extraction quality${NC}"
        exit 1
    fi
fi

if [[ ! "$OPENAI_KEY" =~ ^sk- ]]; then
    echo -e "${RED}❌ Invalid OpenAI key format (should start with sk-)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ OpenAI API key provided${NC}"

# Clone repository
echo ""
echo -e "${BLUE}📦 Cloning Core repository...${NC}"

if [ -d "$CLONE_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory already exists: $CLONE_DIR${NC}"
    read -rp "Remove and re-clone? (y/N): " RECLONE
    if [[ "$RECLONE" =~ ^[Yy]$ ]]; then
        echo "   Removing existing directory..."
        rm -rf "$CLONE_DIR"
    else
        echo "   Using existing directory"
        cd "$CLONE_DIR"
    fi
else
    git clone "$REPO_URL" "$CLONE_DIR"
    cd "$CLONE_DIR"
fi

echo -e "${GREEN}✅ Repository ready: $CLONE_DIR${NC}"

# Configure environment
echo ""
echo -e "${BLUE}⚙️  Configuring environment...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -rp "Overwrite? (y/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo "   Keeping existing .env"
    else
        echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
        echo -e "${GREEN}✅ Created .env with OpenAI key${NC}"
    fi
else
    echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
    echo -e "${GREEN}✅ Created .env with OpenAI key${NC}"
fi

# Launch services
echo ""
echo -e "${BLUE}🐳 Launching Docker containers...${NC}"
echo "   This may take a few minutes on first run..."
echo ""

docker compose up -d

# Wait for services
echo ""
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 10

# Verify services
echo ""
echo -e "${BLUE}🔍 Verifying services...${NC}"

if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers running${NC}"
    docker compose ps
else
    echo -e "${RED}❌ Some containers failed to start${NC}"
    docker compose ps
    echo ""
    echo "Check logs with: docker compose logs"
    exit 1
fi

# Print success summary
echo ""
echo "======================================"
echo -e "${GREEN}✅ SETUP COMPLETED${NC}"
echo "======================================"
echo ""
echo "Core is now running at:"
echo "  • Web interface: http://localhost:3000"
echo "  • API endpoint: http://localhost:3000/api"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in browser"
echo "  2. Create account or sign in"
echo "  3. Configure MCP to point to localhost:"
echo "     claude mcp add --transport http core-memory \\"
echo "       http://localhost:3000/api/v1/mcp?source=Claude-Code"
echo ""
echo "Useful commands:"
echo "  • View logs: docker compose logs -f"
echo "  • Stop services: docker compose down"
echo "  • Restart: docker compose restart"
echo ""
echo "======================================"
