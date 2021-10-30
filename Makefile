SHELL := /bin/bash
PWD := $(shell pwd)

default: build

build:
	docker build -f ./src/building_blocks.dockerfile -t "building-block:latest" .
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
	docker-compose --project-name "tp2-middleware" logs -f
.PHONY: docker-compose-logs