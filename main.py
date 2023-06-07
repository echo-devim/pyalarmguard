import time
import logging
from sensors.sensor_microphone import SensorMicrophone
from sensors.sensor_camera import SensorCamera
from carriers.telegram_carrier import CarrierTelegram
from detectors.detector import Detector
import sys
import config
import os

def doActions(carriers):
    """ Perform actions request by user on communication channels """
    for c in carriers:
        c.doAction()

def notify(carriers, logger, message, evidence):
    """ Loop over carriers list and invoke their notification method """
    logger.info(message)
    # Notify and (eventually) attach evidences
    for carrier in carriers:
        if not carrier.notify(message, evidence):
            logger.error("Cannot send notification")
        else:
            logger.info(f"Notification sent using {carrier.name}")

def main():
    appname = "pyalarmguard"
    # Init logger
    logging.basicConfig(filename=f'{appname}.log', encoding='utf-8', level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')
    # Add handler to log also on standard output
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger(f"{appname}")
    logger.addHandler(handler)

    tg = CarrierTelegram(logger)
    carriers = [tg]

    logger.info(f"Starting {appname}")

    cam = SensorCamera(logger)
    mic = SensorMicrophone(logger)

    detector = Detector(logger, mic, cam)
    
    while(True):
        try:
            # Check if user requested some action to do
            doActions(carriers)

            # Perform detection with audio/image analysis
            if config.human_detection and detector.humanDetection():
                notify(carriers, logger, detector.message, cam.getEvidenceFile())

            if config.alarm_detection and detector.alarmDetection():
                notify(carriers, logger, detector.message, mic.getEvidenceFile())

        except Exception as ex:
            logger.info(f"Exception occurred: {ex}")


if __name__ == "__main__":
    main()
