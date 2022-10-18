from kafka import KafkaConsumer, KafkaProducer


class Consumer:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(topic, bootstrap_servers="seheon.codes:29092")
        self.handlers = []

    def consume(self):
        for message in self.consumer:
            for value, func in self.handlers:
                if message.value == value:
                    func(message)

    def handle(self, message, handler):
        self.handlers.append((message, handler))


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
