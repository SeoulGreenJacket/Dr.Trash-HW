from multiprocessing import Process, BoundedSemaphore, Value
import os
from threading import Thread, Semaphore
import time
import cv2
from kafka import KafkaProducer


class Camera:
    def __init__(self, uuid, src=0, fps=30) -> None:
        print("Initializing camera ...", end="")
        self.__fps = fps
        self.__uuid = uuid
        self.__cam = Value(cv2.VideoCapture, src)
        self.__status = Value("b", False)
        self.__camera_semaphore = BoundedSemaphore(fps)
        self.__kafka_client = None
        self.__capture_semaphore = None
        self.__processes = []
        print("\r                     ", end="\r")
        print("Camera initialized")

    def __del__(self) -> None:
        self.cam.release()

    def __main_thread(self) -> None:
        print("Wait for camera to be ready ...", end="")
        for _ in range(self.__fps):
            self.__camera_semaphore.acquire()
        _, _ = self.__cam.value.read()
        print("                               ", end="")
        print("\rStart capturing ...")
        while self.__status:
            try:
                self.__camera_semaphore.release()
            except ValueError:
                print("[WARN] Converting process is too slow.")
            time.sleep(1 / self.__fps)

    def __camera_process(self) -> None:
        self.__kafka_client = KafkaProducer(bootstrap_servers=os.environ["KAFKA_HOST"])
        self.__capture_semaphore = Semaphore(10)
        while self.__status and self.__capture_semaphore.acquire():
            if self.__camera_semaphore.acquire():
                Thread(target=self.__camera_thread).start()

    def __camera_thread(self) -> None:
        if self.__status:
            retval, raw = self.__cam.value.read()
            if retval == False:
                raise Exception("Failed to capture frame from camera")
            retval, frame = cv2.imencode(".jpeg", raw)
            if retval == False:
                raise Exception("Failed to convert raw frame to jpeg")
            self.__kafka_client.send(self.__uuid, frame.tobytes())
        self.__capture_semaphore.release()

    def start(self) -> None:
        self.__status = True
        for _ in range(4):
            self.__processes.append(Process(target=self.__camera_process))
            self.__processes[-1].start()
        Thread(target=self.__main_thread).start()

    def pause(self) -> None:
        self.__status = False
        for i in range(4):
            self.__processes[i].join()
            self.__processes[i].close()
        self.__kafka_client.send(self.__uuid, b"end")
        self.__processes.clear()
