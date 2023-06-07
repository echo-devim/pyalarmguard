from detectors.dejavu3.dejavud import DejavuDetection
from detectors.objdetection.objdetection import ObjectDetection
from detectors.audiostats.audiostats import AudioStats
import os
import config

class Detector:

    def __init__(self, logger, microphone, camera):
        self.logger = logger
        self.mic = microphone
        self.cam = camera
        #self.djv = DejavuDetection(logger)
        self.objdet = ObjectDetection(logger)
        self.message = ""

    #def __alarmDetectionCorrelation(self):
    #    """ This method still doesn't work, keeping here for future improvements """
    #    res = self.djv.detect(self.mic.getEvidenceFile(), threshold=50)
    #    if (res != None) and (res["sound_name"] == "alarm"):
    #        self.message = "Alarm detected"
    #        return True
    #    return False

    def __alarmDetectionDBLevel(self):
        # Perform audio fingerprinting and calculate similarity
        # Analyze audio for alarm sound
        audiostats = AudioStats()
        # Keep only high frequencies (alarm sound)
        orig = self.mic.getEvidenceFile()
        wavfile = audiostats.highPassFilter(orig)
        dblevel = audiostats.getProperty(wavfile, "RMS lev dB")
        if os.path.exists(wavfile):
            os.remove(wavfile)
        print(f"RMS dB level: {dblevel}")
        if (dblevel > config.db_threshold):
            self.message = f"Alarm detected with db level {dblevel}"
            return True
        return False


    def alarmDetection(self, type="dblevel"):
        # Record audio sample from microphone
        self.mic.record(config.recording_seconds)
        #if (type == "correlation"):
        #    print("ATTENTION: Audio correlation still not working")
        #    return self.__alarmDetectionCorrelation()
        #else:
        return self.__alarmDetectionDBLevel()


    def humanDetection(self):
        self.cam.takephoto()
        for e in self.objdet.detect(self.cam.getEvidenceFile()):
            conf = e["confidence"]
            if (e["label"] == "person") and (conf > config.object_detection_threshold):
                self.message = f"Human detected with confidence {conf}"
                return True
        return False


