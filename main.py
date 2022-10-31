from kafka import KafkaConsumer, KafkaProducer
from capturer import Capturer
import os
from imagezmq import ImageSender
import threading

FPS = 30

CAMERA_UUID = os.environ["CAMERA_UUID"]
KAFKA_HOST = os.environ["KAFKA_HOST"]
TRACKER_TOPIC = os.environ["KAFKA_TOPIC_TRACKER"]


producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)
status = "blocked"

capturer = Capturer(0, FPS)


def __sender_process(host, port):
    sender = ImageSender(connect_to=f"tcp://{host}:{port}")

    global status
    while status == "running":
        jpeg = capturer.read()
        sender.send_jpg(CAMERA_UUID, jpeg)
    sender.send_jpg(CAMERA_UUID, b"END")
    sender.close()


def on_ready(message, usage_id):
    global status
    if status == "blocked":
        status = "ready"
        producer.send(TRACKER_TOPIC, f"{usage_id}_{CAMERA_UUID}".encode())
        print(f"[{message.timestamp}] Camera ready")


def on_start(message, host, port):
    global status
    if status == "ready":
        status = "running"
        capturer.start()
        threading.Thread(target=__sender_process, args=(host, port)).start()
        print(f"[{message.timestamp}] Camera started")


def on_pause(message):
    global status
    if status == "running":
        status = "blocked"
        capturer.pause()
        print(f"[{message.timestamp}] Camera paused")


if __name__ == "__main__":
    consumer = KafkaConsumer(
        f"{CAMERA_UUID}-control",
        bootstrap_servers=KAFKA_HOST,
        group_id="camera",
    )
    print("[INFO] Ready to receive control messages")

    for message in consumer:
        tokens = message.value.decode("utf-8").split("-")
        if tokens[0] == "ready":
            on_ready(message, usage_id=tokens[1])
        elif tokens[0] == "start":
            on_start(message, host=tokens[1], port=tokens[2])
        elif tokens[0] == "pause":
            on_pause(message)
        elif tokens[0] == "stop":
            on_pause(message)
            break

    consumer.close()
    print("[INFO] Consumer stopped")
