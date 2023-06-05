import time
import logging
from sensors.sensor_microphone import SensorMicrophone
from sensors.sensor_camera import SensorCamera
from carriers.telegram_carrier import CarrierTelegram
from detectors.audiostats.audiostats import AudioStats
from detectors.objdetection.objdetection import ObjectDetection
import sys
import config
import os

def doActions(carriers):
    """ Perform actions request by user on communication channels """
    for c in carriers:
        c.doAction()

def alarmDetection(mic, carriers, logger):
    # Record audio sample from microphone
    mic = SensorMicrophone(logger)
    mic.record(config.recording_seconds)
    # Analyze audio for alarm sound
    audiostats = AudioStats()
    # Keep only high frequencies (alarm sound)
    orig = mic.getEvidenceFile()
    wavfile = audiostats.highPassFilter(orig)
    dblevel = audiostats.getProperty(wavfile, "RMS lev dB")
    if os.path.exists(wavfile):
        os.remove(wavfile)
    print(f"RMS dB level: {dblevel}")
    if (dblevel > config.db_threshold):
        logger.info(f"Alarm detected with db level {dblevel}")
        # Notify and (eventually) attach evidences
        for carrier in carriers:
            if not carrier.notify(f"Alarm detected with db level {dblevel}", mic.getEvidenceFile()):
                logger.error("Cannot send notification")
            else:
                logger.info(f"Notification sent using {carrier.name}")

def humanDetection(camera, objdet, carriers, logger):
    camera.takephoto()
    for e in objdet.detect(camera.getEvidenceFile()):
        conf = e["confidence"]
        if (e["label"] == "person") and (conf > config.object_detection_threshold):
            logger.info(f"Human detected with confidence {conf}")
            # Notify and (eventually) attach evidences
            for carrier in carriers:
                if not carrier.notify(f"Human detected with confidence {conf}", camera.getEvidenceFile()):
                    logger.error("Cannot send notification")
                else:
                    logger.info(f"Notification sent using {carrier.name}")


def main():
    # Init logger
    logging.basicConfig(filename='pyalarmguard.log', encoding='utf-8', level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S')
    # Add handler to log also on standard output
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger("pyalarmguard")
    logger.addHandler(handler)

    tg = CarrierTelegram(logger)
    carriers = [tg]

    logger.info("Starting pyalarmguard")

    cam = SensorCamera(logger)
    mic = SensorMicrophone(logger)

    objdet = ObjectDetection(logger)
    
    while(True):
        try:
            # Check if user requested some action to do
            doActions(carriers)
            if config.human_detection:
                humanDetection(cam, objdet, carriers, logger)
            if config.alarm_detection:
                alarmDetection(mic, carriers, logger)
        except Exception as ex:
            logger.info(f"Exception occurred: {ex}")
        


if __name__ == "__main__":
    main()
