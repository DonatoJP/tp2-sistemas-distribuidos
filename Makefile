SHELL := /bin/bash
PWD := $(shell pwd)

default: build

build:
	docker build --target basic -f ./src/building_blocks.dockerfile -t "building-block:basic" .
	docker build -f ./src/building_blocks.dockerfile -t "building-block:full" .
	docker build -f "./src/input_node.dockerfile" -t "input_node:latest" .
.PHONY: build

# Trabajo completo
system-run-all:
	docker-compose --project-name "tp2-middleware" up -d
	sleep 3s
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
	docker-compose --project-name "tp2-middleware" down -v --remove-orphans
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

# Ejercicio 1
docker-compose-up-1:
	docker-compose -f docker-compose-ej1.yaml --project-name "tp2-middleware" up -d
	sleep 3s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-1

docker-compose-down-1:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v --remove-orphans
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
	sleep 3s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-3

docker-compose-down-3:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v --remove-orphans
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
	sleep 3s
	docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: docker-compose-up-2

docker-compose-down-2:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v --remove-orphans
.PHONY: docker-compose-down-2

docker-compose-ps-2:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: docker-compose-ps-2

docker-compose-logs-2:
	docker-compose --project-name "tp2-middleware" logs -f $(service-2)
.PHONY: docker-compose-logs-2


example-up:
	docker-compose -f "docker-compose-examples.yaml" --project-name "tp2-middleware" up -d
	# sleep 3s
	# docker-compose -f docker-compose-input.yaml --project-name "tp2-middleware" up -d
.PHONY: example-up


example-logs:
	logs -f $(service)
.PHONY: example-logs

example-down:
	docker-compose --project-name "tp2-middleware" stop -t 1
	docker-compose --project-name "tp2-middleware" down -v --remove-orphans
.PHONY: example-down


start-ej1-simple:
	docker-compose --project-name "tp2-middleware" -f docker-compose-ej1-simple.yaml up -d
.PHONY: start-ej1-simple

simple-logs:
	docker-compose --project-name "tp2-middleware" -f docker-compose-ej1-simple.yaml logs -f
.PHONY: simple-logs

simple-ps:
	docker-compose --project-name "tp2-middleware" -f docker-compose-ej1-simple.yaml ps
.PHONY: simple-ps


stop-ej1-simple:
	docker-compose --project-name "tp2-middleware" -f docker-compose-ej1-simple.yaml down
	docker-compose --project-name "tp2-middleware" down -v --remove-orphans
.PHONY: stop-ej1-simple


start-input:
	docker-compose --project-name "tp2-middleware" -f  docker-compose-input.yaml up -d
.PHONY: start-input

example-ps:
	docker-compose --project-name "tp2-middleware" ps
.PHONY: example-ps

rs:
	./dcp down
	sleep 3
	sudo rm -rf storage
	mkdir storage 
	./dcp up -d
.PHONY: rs

rsf:
	./dcfull down
	sleep 3
	sudo rm -rf storage
	mkdir storage 
	./dcfull up -d
.PHONY: rsf

diego82:
	docker kill tp2-middleware_ej2-user-avg-questions-1_1 tp2-middleware_ej1-avg-holder-1_1 tp2-middleware_ej3-joiner-1_1 reviver2
.PHONY: diego82

diego78:
	docker kill vault2 reviver2
.PHONY: diego82

diego86:
	docker kill vault3 reviver3 tp2-middleware_ej2-top-n-users_1 tp2-middleware_ej1-filter-1_1 tp2-middleware_ej3-group-by-holder-1_1
.PHONY: diego82

diego90:
	docker kill vault3 vault2
.PHONY: diego82

logsej2:
	./dcfull logs -f --tail=2000 ej2-user-avg-questions-1 ej2-general-avg-answers ej2-user-avg-answers-1 ej2-general-avg-questions ej2-user-answers-filter-1 ej2-user-questions-filter-1 ej2-top-n-users ej2-user-intersector-1 result-saver2
.PHONY: logsej2

logsMSG:
	./dcfull logs -f --tail=2000 vault3 hvault3 | grep "PROCESSED MESS"
.PHONY: logsMSG
