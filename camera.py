from multiprocessing import Process, Queue, Value
import os
import queue
from threading import Thread
import time
import cv2
from kafka import KafkaProducer


class Camera:
    def __init__(self, uuid, src=0, fps=30) -> None:
        print("Initializing camera ...", end="")
        self.__target_fps = fps
        self.__fps = fps
        self.__uuid = uuid
        self.__cam = cv2.VideoCapture(src)
        self.__status = Value("b", False)
        self.__frame = None
        self.__kafka_client = None
        self.__processes = []
        self.__num_process = 8
        self.__num_threads = 10
        print("\r                       ", end="\r")
        print("Camera initialized")

    def __del__(self) -> None:
        self.__cam.release()

    def __main_thread(self) -> None:
        self.__fps = self.__target_fps
        while self.__status:
            start_time = time.time()
            try:
                retval, frame = self.__cam.read()
                if retval == False:
                    raise Exception("Failed to capture frame from camera")
                self.__frame.put(frame, block=False)
            except queue.Full:
                print(
                    f"[{int(time.time())}] Converting process is too slow. Dropping frame ... ({self.__fps} fps)",
                )
                self.__fps = max(20, self.__fps - 1)
            except ValueError:  # Queue is closed
                break
            capture_duration = time.time() - start_time
            if capture_duration < 1 / self.__fps:
                time.sleep(1 / self.__fps - capture_duration)
                if self.__fps < self.__target_fps:
                    print(
                        f"[{int(time.time())}] Converting process is fast enough. Increasing fps ... ({self.__fps} fps)"
                    )
                    self.__fps += 1

    def __camera_process(self) -> None:
        threads = []
        self.__kafka_client = KafkaProducer(bootstrap_servers=os.environ["KAFKA_HOST"])
        for _ in range(self.__num_threads):
            threads.append(Thread(target=self.__camera_thread))
            threads[-1].start()
        for thread in threads:
            thread.join()
        self.__kafka_client.close()

    def __camera_thread(self) -> None:
        while self.__status:
            raw = self.__frame.get(block=True)
            retval, frame = cv2.imencode(".jpeg", raw)
            if retval == False:
                raise Exception("Failed to convert raw frame to jpeg")
            self.__kafka_client.send(self.__uuid, frame.tobytes())

    def start(self) -> None:
        self.__status = True
        self.__frame = Queue(maxsize=self.__fps)
        for _ in range(self.__num_process):
            self.__processes.append(Process(target=self.__camera_process))
            self.__processes[-1].start()
        Thread(target=self.__main_thread).start()

    def pause(self) -> None:
        self.__status = False
        self.__frame.close()
        self.__frame.join_thread()
        for p in self.__processes:
            p.kill()
            p.join()
            p.close()
        self.__processes.clear()
