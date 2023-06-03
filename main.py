#import notifiers.telegram_notifier
import time
import logging
from sensors.sensor_microphone import SensorMicrophone
from notifiers.telegram_notifier import NotifierTelegram
from detectors.audiostats.audiostats import AudioStats
import sys
import config
import os

def doActions(notifiers):
    """ Perform actions request by user on communication channels """
    for n in notifiers:
        n.doAction()

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

    tg = NotifierTelegram(logger)
    notifiers = [tg]

    logger.info("Starting pyalarmguard")

    mic = SensorMicrophone(logger)
    mic.record(config.recording_seconds)
    
    while(True):
        try:
            # Check if user requested some action to do
            doActions(notifiers)
            if config.alarm_detection:
                # Record audio sample from microphone
                mic = SensorMicrophone(logger)
                mic.record(3)
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
                    if not tg.notify(f"Alarm detected with db level {dblevel}", mic.getEvidenceFile()):
                        logger.error("Cannot send notification")
                    else:
                        logger.info("Notification sent using telegram")
        except Exception as ex:
            logger.info(f"Exception occurred: {ex}")
        time.sleep(1)
        


if __name__ == "__main__":
    main()
