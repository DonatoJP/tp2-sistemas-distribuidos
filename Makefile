SHELL := /bin/bash
PWD := $(shell pwd)

default: build

build:
	docker build -f ./src/building_blocks.dockerfile -t "building-block:latest" .
	docker build -f "input_node/input_node.dockerfile" -t "input_node:latest" .
.PHONY: build

docker-compose-up:
	docker-compose --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up

docker-compose-down:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down
.PHONY: docker-compose-down

docker-compose-ps:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: docker-compose-ps

docker-compose-logs:
	docker-compose --project-name "tp2-middleware" logs -f $(service)
.PHONY: docker-compose-logs


docker-compose-up-2:
	docker-compose -f docker-compose-ej2.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-2

docker-compose-down-2:
	docker-compose -f docker-compose-ej2.yaml --project-name "tp2-middleware" stop -t 1
	docker-compose -f docker-compose-ej2.yaml --project-name "tp2-middleware" down
.PHONY: docker-compose-down-2

docker-compose-ps-2:
	docker-compose -f docker-compose-ej2.yaml --project-name "tp2-middleware" ps
.PHONY: docker-compose-ps-2

docker-compose-logs-2:
	docker-compose -f docker-compose-ej2.yaml --project-name "tp2-middleware" logs -f $(service)
.PHONY: docker-compose-logs-2