#!/bin/bash
# =============================================================================
# AI Digital Human - One-Click Deployment Script
# =============================================================================
# Usage: ./deploy.sh [--production]
#   --production    Use production config (docker-compose.prod.yml)
#   --development    Use development config (docker-compose.yml)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default to production mode
MODE="production"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            MODE="production"
            shift
            ;;
        --development)
            MODE="development"
            shift
            ;;
        --help)
            echo "Usage: ./deploy.sh [--production|--development]"
            echo "  --production   Use production config (recommended)"
            echo "  --development  Use development config"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Digital Human - Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo -e "${YELLOW}Please install Docker first:${NC}"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo "  sudo usermod -aG docker \$USER"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo -e "${YELLOW}Please install Docker Compose first:${NC}"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install docker-compose"
    exit 1
fi

# Set compose file based on mode
if [ "$MODE" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo -e "${GREEN}Using production configuration${NC}"
else
    COMPOSE_FILE="docker-compose.yml"
    echo -e "${YELLOW}Using development configuration${NC}"
fi

# Check if .env exists, create from example if not
if [ ! -f .env ]; then
    echo ""
    echo -e "${YELLOW}No .env file found. Creating from .env.default...${NC}"
    if [ -f .env.default ]; then
        cp .env.default .env
        echo -e "${YELLOW}Please edit .env and add your API keys!${NC}"
    else
        echo -e "${RED}Warning: No .env.default found. Creating basic .env...${NC}"
        cat > .env << 'EOF'
# AI Digital Human - Environment Configuration
# Please fill in your API keys below

# GLM (智谱AI) - Recommended for Chinese support
GLM_API_KEY=your_glm_api_key_here

# MiniMax (海螺AI) - Optional alternative
# MINIMAX_API_KEY=your_minimax_api_key_here
# MINIMAX_GROUP_ID=your_minimax_group_id_here

# Security
SECRET_KEY=change-me-in-production-$(openssl rand -hex 32)

# LLM Provider (glm/minimax/openai)
LLM_PROVIDER=glm
EOF
        echo -e "${RED}Please edit .env and add your API keys!${NC}"
    fi
fi

echo ""
echo -e "${BLUE}Pulling latest images...${NC}"
docker compose -f "$COMPOSE_FILE" pull

echo ""
echo -e "${BLUE}Building containers...${NC}"
docker compose -f "$COMPOSE_FILE" build --no-cache

echo ""
echo -e "${BLUE}Starting services...${NC}"
docker compose -f "$COMPOSE_FILE" up -d

echo ""
echo -e "${BLUE}Waiting for services to be healthy...${NC}"
sleep 10

# Check service status
echo ""
echo -e "${BLUE}Checking service status...${NC}"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Access the application:"
echo -e "  ${BLUE}Frontend:${NC}  http://wen.pmparker.net"
echo -e "  ${BLUE}API:${NC}       http://wen.pmparker.net/api"
echo -e "  ${BLUE}API Docs:${NC}  http://wen.pmparker.net/api/docs"
echo ""
echo -e "Useful commands:"
echo -e "  ${YELLOW}View logs:${NC}    docker compose -f $COMPOSE_FILE logs -f"
echo -e "  ${YELLOW}Stop:${NC}         docker compose -f $COMPOSE_FILE down"
echo -e "  ${YELLOW}Restart:${NC}       docker compose -f $COMPOSE_FILE restart"
echo ""