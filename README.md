# Sistemas Distribuidos I - Trabajo Practico 2
## Middlewares

### Comandos

- Para buildear imagenes necesarias

```
make
```

- Para levantar el sistema

```
make system-up
```

- Para injectar data

```
make inject-data
```

- Para monitorear estado de recursos

```
make system-ps
```

- Para ver salida de cada container

```
make systems-logs service="<NOMBRE CONTAINER>"
```

- Para ver salida los ultimos nodos de cada flujo

```
make follow-output
```

- Para bajar el sistema

```
make follow-output
```

- Para levantar e injectar los datos de un solo comando

```
make system-run-all
```

- Para correr cada ejercicio por separado

```
# Numero final corresponde a cada punto
make docker-compose-up-1
make docker-compose-up-2
make docker-compose-up-3
```