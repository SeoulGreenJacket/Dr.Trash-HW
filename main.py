from kafka import KafkaConsumer, KafkaProducer
from camera import Camera
import os

__status = False
__camera = Camera(os.environ["CAMERA_UUID"])
__uuid = os.environ["CAMERA_UUID"]
__consumer = KafkaConsumer(
    f"{os.environ['CAMERA_UUID']}-control",
    bootstrap_servers=os.environ["KAFKA_HOST"],
    group_id="camera",
)
__producer = KafkaProducer(bootstrap_servers=os.environ["KAFKA_HOST"])


def on_start(message, usage_id):
    global __status
    if __status == True:
        return
    __producer.send(os.environ["KAFKA_TOPIC_TRACKER"], f"{usage_id}_{__uuid}".encode())
    __camera.start()
    __status = True
    print(f"[{message.timestamp}] Camera started")


def on_pause(message):
    global __status
    if __status == False:
        return
    __status = False
    __camera.pause()
    __producer.send(__uuid, b"end")
    print(f"[{message.timestamp}] Camera paused")


if __name__ == "__main__":
    print("[INFO] Ready to receive control messages")
    for message in __consumer:
        tokens = message.value.decode("utf-8").split("-")
        if tokens[0] == "start":
            on_start(message, usage_id=tokens[1])
        elif tokens[0] == "pause":
            on_pause(message)
    print("[INFO] Consumer stopped")
