import cv2
import multiprocessing as mp
import queue
import time


def __encode_process(src, jpegq, running, fps):
    cam = cv2.VideoCapture(src)
    while running.value:
        start_time = time.time()
        _, frame = cam.read()
        _, buffer = cv2.imencode(".jpeg", frame)
        try:
            jpegq.put(buffer, block=True)
        except queue.Full:
            with fps.get_lock():
                fps.value = max(fps.value - 1, 15)
            print(f"[{int(time.time())}] Dropping frame ... {fps.value} fps")
        capture_duration = time.time() - start_time
        if capture_duration < 1 / fps.value:
            with fps.get_lock():
                fps.value = min(fps.value + 1, 30)
            print(f"[{int(time.time())}] Increasing fps ... {fps.value} fps")
            time.sleep(1 / fps.value - capture_duration)
    cam.release()


class Capturer:
    def __init__(self, src=0, fps=20) -> None:
        self.__src = src
        self.__fps = mp.Value("i", fps)
        self.__jpegq = mp.Queue(maxsize=fps)
        self.__running = mp.Value("b", False)

    def read(self):
        if self.__running:
            try:
                jpeg = self.__jpegq.get(block=True, timeout=1 / self.__fps.value)
                return jpeg
            except queue.Empty:
                print(f"[{int(time.time())}] No frame available")
        else:
            raise ValueError("Capturer is not running")

    def start(self):
        with self.__running.get_lock():
            self.__running = True
        encode_process = mp.Process(
            target=__encode_process,
            args=(self.__src, self.__jpegq, self.__running, self.__fps),
        )
        encode_process.start()

    def pause(self):
        with self.__running.get_lock():
            self.__running = False
