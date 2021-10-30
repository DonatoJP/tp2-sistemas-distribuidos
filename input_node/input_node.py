import csv, pika, json, os

def main():
    file_to_read = os.environ["FILE_TO_PROCESS"] # 'data/red_answers.csv'
    chunk_size = int(os.environ["CHUNK_SIZE"])

    host = 'rabbitmq-tp2'
    port = '5672'
    queue_name = os.environ["OUTPUT_QUEUE_NAME"]

    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)


    lines_to_write = []
    with open(file_to_read, 'r') as file:
        reader = csv.DictReader(file)
        end = False
        while not end:
            count = 0
            while (count < chunk_size):
                try:
                    lines_to_write.append(json.dumps(next(reader)))
                except StopIteration:
                    end = True
                    break
                count += 1
            if (len(lines_to_write) > 0):
                message = '\n'.join(lines_to_write)
                channel.basic_publish(exchange='',
                    routing_key=queue_name,
                    body=message)

                lines_to_write = []

if __name__ == '__main__':
    main()
