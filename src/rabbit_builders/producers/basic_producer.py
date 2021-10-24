import pika

def build_basic_producer(queue_name, host='rabbitmq-tp2', port='5672'):
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)

    return connection, channel