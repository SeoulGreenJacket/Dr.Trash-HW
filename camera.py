import time
import cv2
from threading import Thread
from kafka import KafkaProducer


class Camera:
    def __init__(self, uuid, src=0, fps=20):
        print("Initializing camera ...", end="")
        self.cam = cv2.VideoCapture(src)
        self.target_fps = fps
        self.captured_at = 0.0
        self.__status = False
        self.__kafka_client = KafkaProducer(bootstrap_servers="seheon.codes:29092")
        self.__kafka_topic = uuid
        print("\r                     ", end="\r")
        print("Camera initialized")

    def __del__(self):
        self.cam.release()

    def __capture_thread(self):
        while self.__status:
            start_time = time.time()
            retval, raw = self.cam.read()
            if retval == False:
                raise Exception("Failed to capture frame from camera")
            Thread(target=self.__convert_thread, args=(raw,)).start()
            end_time = time.time()
            idle_time = 1 / self.target_fps - (end_time - start_time)
            if idle_time > 0:
                time.sleep(idle_time)
            else:
                print(
                    f"Capture thread is too slow: {-idle_time * 1000:6.2f} ms delayed"
                )

    def __convert_thread(self, raw):
        if self.__status:
            retval, frame = cv2.imencode(".jpeg", raw)
            if retval == False:
                raise Exception("Failed to convert raw frame to jpeg")
            frame_bytes = str(frame.tobytes()).encode()
            self.__kafka_client.send(self.__kafka_topic, frame_bytes)

    def start(self, fps=None):
        self.__status = True
        if fps is not None:
            self.target_fps = fps
        Thread(target=self.__capture_thread).start()

    def pause(self):
        self.__status = False
        self.frame = None
