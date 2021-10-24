import pika

def build_basic_consumer(queue_name, callback_func, host='rabbitmq-tp2', port='5672', auto_ack=True):
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback_func, auto_ack=auto_ack)

    return connection, channel