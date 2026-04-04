# =============================================================================
# AI Digital Human - Makefile
# =============================================================================
# Common development and deployment operations.
# Usage: make <target>
# =============================================================================

.PHONY: help
.DEFAULT_GOAL := help

# Detect compose file (prefer production)
COMPOSE_FILE := docker-compose.prod.yml
ifeq ($(COMPOSE_FILE),)
COMPOSE_FILE := docker-compose.yml
endif

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(BLUE)AI Digital Human - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make deploy          # Deploy to production"
	@echo "  make dev            # Start development environment"
	@echo "  make logs           # View logs"
	@echo "  make clean          # Clean up containers and volumes"
	@echo ""

# =============================================================================
# Development
# =============================================================================

dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker compose -f docker-compose.yml up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API:      http://localhost:8000"

dev-build: ## Rebuild development containers
	@echo "$(BLUE)Rebuilding development containers...$(NC)"
	docker compose -f docker-compose.yml build --no-cache
	docker compose -f docker-compose.yml up -d
	@echo "$(GREEN)Development environment rebuilt!$(NC)"

dev-logs: ## View development logs
	docker compose -f docker-compose.yml logs -f

# =============================================================================
# Production
# =============================================================================

deploy: ## Deploy to production (using docker-compose.prod.yml)
	@echo "$(BLUE)Deploying to production...$(NC)"
	./deploy.sh --production

deploy-dev: ## Deploy to development mode
	@echo "$(BLUE)Deploying to development mode...$(NC)"
	./deploy.sh --development

prod-logs: ## View production logs
	docker compose -f docker-compose.prod.yml logs -f

# =============================================================================
# Operations
# =============================================================================

start: ## Start all services
	@echo "$(BLUE)Starting services...$(NC)"
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)Services started!$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)Services restarted!$(NC)"

logs: ## View logs (default)
	docker compose -f $(COMPOSE_FILE) logs -f

status: ## Show service status
	docker compose -f $(COMPOSE_FILE) ps

# =============================================================================
# Maintenance
# =============================================================================

clean: ## Stop and remove all containers and volumes
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose -f $(COMPOSE_FILE) down -v; \
		echo "$(GREEN)Clean complete!$(NC)"; \
	else \
		echo "$(YELLOW)Clean cancelled.$(NC)"; \
	fi

clean-images: ## Remove all project images
	@echo "$(YELLOW)WARNING: This will remove all project Docker images!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose -f $(COMPOSE_FILE) down --rmi all; \
		echo "$(GREEN)Images removed!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

rebuild: ## Rebuild all containers without cache
	@echo "$(BLUE)Rebuilding all containers...$(NC)"
	docker compose -f $(COMPOSE_FILE) build --no-cache
	@echo "$(GREEN)Rebuild complete!$(NC)"

# =============================================================================
# Development Tools
# =============================================================================

install: ## Install dependencies for local development
	@echo "$(BLUE)Installing dependencies...$(NC)"
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install
	@echo "$(GREEN)Dependencies installed!$(NC)"

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	cd apps/api && ruff check app/
	cd apps/web && npm run lint || true
	@echo "$(GREEN)Lint complete!$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker compose -f $(COMPOSE_FILE) run --rm api pytest
	@echo "$(GREEN)Tests complete!$(NC)"

# =============================================================================
# Info
# =============================================================================

info: ## Show system information
	@echo ""
	@echo "$(BLUE)AI Digital Human - System Info$(NC)"
	@echo ""
	@echo "Docker version:"
	@docker --version
	@echo ""
	@echo "Docker Compose version:"
	@docker compose version
	@echo ""
	@echo "Using compose file: $(COMPOSE_FILE)"
	@echo ""
	@echo "Service status:"
	@docker compose -f $(COMPOSE_FILE) ps
	@echo ""