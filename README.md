## Dr.Trash-HW

#### Dr.Trash Hardware is a python script for capture image, encode to jpeg, and upload to deep learning model from [Dr.Trash](https://github.com/SeoulGreenJacket/Dr.Trash).

#### Capture and encoding are processed via OpenCV and transmission is processed by Kafka.

![License](https://img.shields.io/github/license/SeoulGreenJacket/Dr.Trash-HW?style=for-the-badge)

![GitHub commit activity](https://img.shields.io/github/commit-activity/y/SeoulGreenJacket/Dr.Trash-HW?style=for-the-badge)

## Requirements

To run it, you need to set up [Dr.Trash](https://github.com/SeoulGreenJacket/Dr.Trash) first.

```bash
$ git clone https://github.com/SeoulGreenJacket/Dr.Trash
$ cd Dr.Trash
$ docker-compose up -d
```

You also need a raspberry pi or other device with a camera to run this script.

We use a [raspberry pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/) with a [camera module v2](https://www.raspberrypi.com/products/camera-module-v2/).

## Installation

This requires you to have Git and Python installed.

To set up a development environment to edit or run Dr.Trash-HW:

```bash
$ git clone https://github.com/SeoulGreenJacket/Dr.Trash-HW
$ cd Dr.Trash-HW
$ python -m pip install -r requirements.txt
```

## Run

To run Dr.Trash-HW:

```bash
$ env $(cat .env | xargs) python main.py
```

Now, you can use our [Dr.Trash-FE](https://github.com/SeoulGreenJacket/Dr.Trash-FE) application.
