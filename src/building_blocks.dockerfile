FROM python:3
WORKDIR /app
RUN pip3 install pika
RUN apt-get -q update && apt-get -qy install netcat
RUN wget 'https://raw.githubusercontent.com/eficode/wait-for/master/wait-for'

COPY /src .
ENTRYPOINT [ "/bin/sh" ]