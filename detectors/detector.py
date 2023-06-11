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
        self.djv = DejavuDetection(logger)
        self.objdet = ObjectDetection(logger)
        self.message = ""

    def __audioCorrelation(self):
        return self.djv.detect(self.mic.getEvidenceFile(), threshold=0)

    def __alarmDetection(self):
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


    def alarmDetection(self):
        # Record audio sample from microphone
        self.mic.record(config.recording_seconds)
        corr = self.__audioCorrelation()
        print(f"Audio Correlation: {corr}")
        # Check if audio is correlated to noise or environmental sounds
        # if it isn't, check its db level
        if (corr != None):
            if corr["sound_name"].startswith("exclude"):
                return False
            elif corr["sound_name"].startswith("include"):
                return True
        return self.__alarmDetection()


    def humanDetection(self):
        self.cam.takephoto()
        for e in self.objdet.detect(self.cam.getEvidenceFile()):
            conf = e["confidence"]
            if (e["label"] == "person") and (conf > config.object_detection_threshold):
                self.message = f"Human detected with confidence {conf}"
                return True
        return False


