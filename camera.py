import logging
import time
import cv2
from threading import Thread, Lock


class Camera:
    def __init__(self, src=0, fps=30):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Use camera source: {src}")
        self.cam = cv2.VideoCapture(src)
        self.target_fps = fps
        self.frame = None
        self.captured_at = 0.0
        self.__frame_lock = Lock()
        self.__status = False

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
                self.logger.warning(
                    f"Capture thread is too slow: {idle_time * 1000} ms delayed"
                )

    def __convert_thread(self, raw):
        if self.__status:
            retval, frame = cv2.imencode(".jpeg", raw)
            if retval == False:
                raise Exception("Failed to convert raw frame to jpeg")
            self.__frame_lock.acquire()
            self.frame = frame
            self.__frame_lock.release()

    def start(self, fps=None):
        self.__status = True
        if fps is not None:
            self.target_fps = fps
        Thread(target=self.__capture_thread).start()

    def stop(self):
        self.__status = False
        self.frame = None

    def read(self):
        return self.frame
