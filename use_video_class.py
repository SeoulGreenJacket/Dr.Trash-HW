import logging
import time
import cv2 as cv
from threading import Thread, Lock


class CaptureFailedException(Exception):
    def __str__(self):
        return "Failed to capture frame from camera"


class ConvertFailedException(Exception):
    def __init__(self, convert_to):
        self.convert_to = convert_to

    def __str__(self, convert_to):
        return f"Failed to convert raw frame to {convert_to}"


class UsbVideoClass:
    def __init__(self, src=0, fps=30):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cam = cv.VideoCapture(src)
        self.target_fps = fps
        self.real_fps = 0
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
                raise CaptureFailedException()
            Thread(target=self.__convert_thread, args=(raw, time.time())).start()
            end_time = time.time()
            idle_time = 1 / self.target_fps - (end_time - start_time)
            if idle_time > 0:
                time.sleep(idle_time)
            else:
                logging.warning(
                    f"Capture thread is too slow: {idle_time * 1000} ms delayed"
                )

    def __convert_thread(self, raw, at):
        if self.__status:
            retval, frame = cv.imencode(".jpeg", raw)
            if retval == False:
                raise ConvertFailedException("jpeg")
            self.__frame_lock.acquire()
            self.frame = frame
            self.real_fps = 1 / (at - self.captured_at)
            self.captured_at = at
            self.__frame_lock.release()

    def start(self, fps=None):
        self.__status = True
        if fps is not None:
            self.target_fps = fps
        Thread(target=self.__capture_thread).start()

    def stop(self):
        self.__status = False

    def read(self):
        return self.frame


class FrameHandler:
    def __call__(self, frame, at):
        pass
