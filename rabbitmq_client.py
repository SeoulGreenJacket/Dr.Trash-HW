#!/usr/bin/env python
import pika


class Client:
    def __init__(self, host, port, user, password, vhost, queue):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.queue = queue
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=credentials,
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def close(self):
        self.connection.close()

    def send(self, message, exchange=""):
        self.channel.basic_publish(
            exchange=exchange, routing_key=self.queue, body=message
        )
