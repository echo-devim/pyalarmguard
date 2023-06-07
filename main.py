import time
import logging
from sensors.sensor_microphone import SensorMicrophone
from sensors.sensor_camera import SensorCamera
from carriers.telegram_carrier import CarrierTelegram
from detectors.detector import Detector
import sys
import config
import os
from datetime import datetime

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

            if config.capture_all:
                if config.captures > 0:
                    cam.takephoto()
                    now = datetime.now()
                    dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
                    os.rename(cam.getEvidenceFile(), f"{config.photo_evidence_path}/photo{dt_string}.jpg")
                else:
                    config.capture_all = False
                    config.captures = config.DEFAULT_CAPTURES

            # Perform detection with audio/image analysis
            if config.human_detection and detector.humanDetection():
                notify(carriers, logger, detector.message, cam.getEvidenceFile())
                config.capture_all = True
            
            with config.mic_mutex:
                if config.alarm_detection and (not config.is_recording) and detector.alarmDetection(type="dblevel"):
                    notify(carriers, logger, detector.message, mic.getEvidenceFile(format="opus"))

        except Exception as ex:
            logger.info(f"Exception occurred: {ex}")


if __name__ == "__main__":
    main()
