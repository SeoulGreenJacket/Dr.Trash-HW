from use_video_class import UsbVideoClass
import logging
import socket

import imagezmq
import time
import cv2 as cv

if __name__ == "__main__":
    sender = imagezmq.ImageSender(connect_to="tcp://host:port")
    rpi_name = socket.gethostname()

    logging.basicConfig(level=logging.DEBUG)
    video = UsbVideoClass()
    video.start()
    while True:
        image = video.read()
        if image is not None:
            sender.send_image(rpi_name, image)
