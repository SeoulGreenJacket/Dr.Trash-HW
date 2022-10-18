from kafka import KafkaConsumer, KafkaProducer


class Consumer:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(
            topic, bootstrap_servers="seheon.codes:29092", group_id="camera"
        )
        self.handlers = []

    def consume(self):
        for message in self.consumer:
            for value, func in self.handlers:
                if message.value == value:
                    func(message)

    def handle(self, message, handler):
        self.handlers.append((message, handler))
        self.consumer.commit()


class Producer:
    def __init__(self, topic):
        self.producer = KafkaProducer(bootstrap_servers="seheon.codes:29092")
        self.__topic = topic

    def send(self, msg):
        self.producer.send(self.__topic, msg)

    def close(self):
        self.producer.close()


class Client:
    def __init__(self, topic):
        self.topic = topic
        self.producer = Producer(topic)
        self.consumer = Consumer(topic + "-control")
