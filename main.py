import logging
from camera import Camera
import time

from kafka_client import Client

logger = logging.getLogger(__name__)
__status = False


def on_start(message):
    global __status
    if __status == True:
        return

    logger.info(f"[{message.timestamp}] Camera started")

    __status = True
    camera = Camera()
    camera.start()
    fps = 30
    while __status:
        start_time = time.time()
        image = camera.read()
        if image is not None:
            client.producer.send(image)
        end_time = time.time()
        idle_time = 1 / fps - (end_time - start_time)
        if idle_time > 0:
            time.sleep(idle_time)


def on_pause(message):
    global __status
    if __status == True:
        logger.info(f"[{message.timestamp}] Camera paused")
        __status = False


if __name__ == "__main__":
    uuid = "ddcd8c24-4fe4-4f87-b197-da65ab63f17f"

    client = Client(uuid)
    client.consumer.handle("start", on_start)
    client.consumer.handle("pause", on_pause)
    logger.info(f"Waiting for message: topic = {uuid}")
