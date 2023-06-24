from detectors.dejavu3.dejavud import DejavuDetection
from detectors.objdetection.objdetection import ObjectDetection
from detectors.audiostats.audiostats import AudioStats
from detectors.signalprocessing import SignalProcessing
import os
import config
import glob

class Detector:

    def __init__(self, logger, microphone, camera):
        self.logger = logger
        self.mic = microphone
        self.cam = camera
        #self.djv = DejavuDetection(logger)
        self.sigproc = SignalProcessing()
        self.objdet = ObjectDetection(logger)
        self.message = ""

    def __audioCorrelation(self):
        match = None
        for wavfile in glob.glob(f"{config.data_directory}/samples/*.wav"):
            label = os.path.basename(wavfile).split(".")[0]
            similarity = self.sigproc.calculateSimilarity(self.mic.getEvidenceFile(), wavfile, False, True)
            if similarity > 0.85:
                if not label.startswith("noise_white"):
                    self.logger.info(f"Similarity with {label} : {similarity}")
                match = label
                break
        #return self.djv.detect(self.mic.getEvidenceFile(), threshold=0)
        return match

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
            # Avoid false positive performing audio correlation
            corr = self.__audioCorrelation()
            print(f"Correlation result: {corr}")
            # Check if audio is correlated to some kind of known noise
            if corr == None or not corr.startswith("noise"):
                self.message = f"Alarm detected with db level {dblevel}"
                return True
        return False


    def alarmDetection(self):
        # Record audio sample from microphone
        self.mic.record(config.recording_seconds)
        # Perform alarm detection
        return self.__alarmDetection()


    def objDetection(self, label, imagepath = ""):
        if imagepath == "":
            self.cam.takephoto()
        for e in self.objdet.detect(self.cam.getEvidenceFile()):
            conf = e["confidence"]
            if (e["label"] == label) and (conf > config.object_detection_threshold):
                self.message = f"{label} detected with confidence {conf}"
                return True
        return False

    def humanDetection(self, imagepath = ""):
        return self.objDetection("person", imagepath)

    #def catDetection(self, imagepath = ""):
    #    return self.objDetection("cat", imagepath)


