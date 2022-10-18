from kafka import KafkaConsumer
from camera import Camera
import os

__status = False
__camera = Camera(os.environ["CAMERA_ID"])
__consumer = KafkaConsumer(
    f"{os.environ['CAMERA_ID']}-control",
    bootstrap_servers=os.environ["KAFKA_HOST"],
    group_id="camera",
)


def on_start(message):
    global __status
    if __status == True:
        return
    __camera.start()
    __status = True
    print(f"[{message.timestamp}] Camera started")


def on_pause(message):
    global __status
    if __status == False:
        return
    __camera.pause()
    __status = False
    print(f"[{message.timestamp}] Camera paused")


if __name__ == "__main__":
    print("Waiting for message...")
    for message in __consumer:
        if message.value == b"start":
            on_start(message)
        elif message.value == b"pause":
            on_pause(message)
    print("Consumer stopped")
