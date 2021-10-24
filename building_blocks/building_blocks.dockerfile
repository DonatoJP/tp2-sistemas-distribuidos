FROM python:3
WORKDIR /app/building_blocks
RUN pip3 install pika
RUN apt-get -q update && apt-get -qy install netcat
RUN wget 'https://raw.githubusercontent.com/eficode/wait-for/master/wait-for'

COPY /building_blocks .
ENTRYPOINT [ "/bin/sh" ]