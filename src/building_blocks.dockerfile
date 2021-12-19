FROM python:3 as basic
WORKDIR /app
RUN pip3 install pika
RUN apt-get -q update && apt-get -qy install netcat
# RUN wget 'https://raw.githubusercontent.com/eficode/wait-for/master/wait-for'

COPY /src .
COPY /src/reviver .
ENTRYPOINT ["/bin/sh", "./wait-for", "rabbitmq-tp2:5672", "--", "python"]

FROM basic as full
RUN pip3 install nltk
RUN python -m nltk.downloader vader_lexicon