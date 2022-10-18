from kafka import KafkaConsumer, KafkaProducer


class Consumer:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(topic, bootstrap_servers="seheon.codes:29092")
        self.handlers = []

    def consume(self):
        for message in self.consumer:
            for msg, handler, args in self.handlers:
                if message.value == msg:
                    handler(args)

    def handle(self, message, handler, args=None):
        self.handlers.append((message, handler, args))


class Producer:
    def __init__(self, topic):
        self.producer = KafkaProducer(bootstrap_servers="seheon.codes:29092")
        self.topic = topic

    def send(self, msg):
        self.producer.send(self.topic, msg)

    def close(self):
        self.producer.close()


class Client:
    def __init__(self, topic):
        self.topic = topic
        self.producer = Producer(topic)
        self.consumer = Consumer(topic)
