import csv, pika, json, os
from utils.workload import Task

def main():
    file_to_read = os.environ["FILE_TO_PROCESS"] # 'data/red_answers.csv'
    chunk_size = int(os.environ["CHUNK_SIZE"])
    centinels_to_send = int(os.environ["CENTINELS_TO_SEND"])

    host = 'rabbitmq-tp2'
    port = '5672'
    queue_name = os.environ["OUTPUT_QUEUE_NAME"]

    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, arguments={"x-max-priority": 2})


    lines_to_write = []
    print(f"Start process with file={file_to_read}, chunk_size={chunk_size}, output to {queue_name}...")
    iterations = 0
    with open(file_to_read, 'r') as file:
        reader = csv.DictReader(file)
        end = False
        while not end:
            iterations += 1
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
                task = Task(1, message)
                task_ser = task.serialize()
                channel.basic_publish(exchange='',
                    routing_key=queue_name,
                    body=task_ser,
                    properties=pika.BasicProperties(priority=2))

                lines_to_write = []
    
    print(f"Finished in {iterations} iterations. Sending {centinels_to_send} centinels...")
    for _ in range(0, centinels_to_send):
        channel.basic_publish(exchange='',
            routing_key=queue_name,
            body="END")

    channel.close()

if __name__ == '__main__':
    main()
