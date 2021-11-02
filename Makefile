SHELL := /bin/bash
PWD := $(shell pwd)

default: build

build:
	docker build -f ./src/building_blocks.dockerfile -t "building-block:latest" .
	docker build -f "input_node/input_node.dockerfile" -t "input_node:latest" .
.PHONY: build

# Trabajo completo
system-run-all:
	docker-compose --project-name "tp2-middleware" up -d
	sleep 2s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: system-run-all

system-up:
	docker-compose --project-name "tp2-middleware" up -d
.PHONY: system-up

inject-data:
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: inject-data

system-down:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v
.PHONY: system-down

system-ps:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: system-ps

system-logs:
	docker-compose --project-name "tp2-middleware" logs -f $(service)
.PHONY: system-logs

follow-output:
	time docker-compose --project-name "tp2-middleware" logs -f ej1-avg-holder-1 ej2-top-n-users ej3-group-by-holder-1
.PHONY: follow-output

service="ej1-avg-holder-1 ej2-top-n-users ej3-group-by-holder-1"
system-control-output: system-logs
.PHONY: system-control-output


# Ejercicio 1
docker-compose-up-1:
	docker-compose -f docker-compose-ej1.yaml --project-name "tp2-middleware" up -d
	sleep 2s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-1

docker-compose-down-1:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v
.PHONY: docker-compose-down-1

docker-compose-ps-1:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: docker-compose-ps-1

docker-compose-logs-1:
	docker-compose --project-name "tp2-middleware" logs -f $(service-1)
.PHONY: docker-compose-logs-1


# Ejercicio 3
docker-compose-up-3:
	docker-compose -f docker-compose-ej3.yaml --project-name "tp2-middleware" up -d
	sleep 2s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-3

docker-compose-down-3:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v
.PHONY: docker-compose-down-3

docker-compose-ps-3:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: docker-compose-ps-3

docker-compose-logs-3:
	docker-compose --project-name "tp2-middleware" logs -f $(service-3)
.PHONY: docker-compose-logs-3

# Ejercicio 2
docker-compose-up-2:
	docker-compose -f docker-compose-ej2.yaml --project-name "tp2-middleware" up -d
	sleep 2s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-2

docker-compose-down-2:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v
.PHONY: docker-compose-down-2

docker-compose-ps-2:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: docker-compose-ps-2

docker-compose-logs-2:
	docker-compose --project-name "tp2-middleware" logs -f $(service-2)
.PHONY: docker-compose-logs-2

