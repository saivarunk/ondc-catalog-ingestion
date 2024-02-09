# Define the default target, which is executed when running just `make` without specifying a target
.DEFAULT_GOAL := help

# Define variables
DOCKER_COMPOSE = docker-compose
PYTHON = python3

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo "Targets:"
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		print "  " $$1 \
	} \
	/##/ { \
		print "    " substr($$0, index($$0, "##") + 3) \
	}' $(MAKEFILE_LIST) | column -t -s ':'

setup: ## Start Docker Compose services
	$(DOCKER_COMPOSE) up setup

start: ## Start Docker Compose services
	$(DOCKER_COMPOSE) up api_server kibana kafdrop kafka -d

stop: ## Stop Docker Compose services
	$(DOCKER_COMPOSE) down

restart: stop start ## Restart Docker Compose services

logs: ## View Docker Compose logs
	$(DOCKER_COMPOSE) logs -f

clean: stop ## Stop Docker Compose services and remove containers, networks, volumes, and images
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE) rm -f
	docker system prune -f

initial_load:
	$(PYTHON) src/scripts/load_data.py

load_async:
	$(PYTHON) src/scripts/load_vectors.py
