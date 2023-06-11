from detectors.dejavu3.dejavu.dejavu import Dejavu
from detectors.dejavu3.dejavu.recognize import FileRecognizer
from detectors.dejavu3.dejavu.dejavu import loggerer

class DejavuDetection:

    def __init__(self, logger):
        self.dburl = "sqlite:///audio.db"
        self.djv = Dejavu(dburl=self.dburl)
        self.djv.fingerprint_directory("detectors/dejavu3/samples", [".mp3", ".wav"])
        

    def detect(self, filepath, threshold=30):
        """
        Find possible matches between audio files
        return None if there aren't matches (greather than threshold)
        """

        # Recognize audio from a file
        sound = self.djv.recognize(
            FileRecognizer, filepath
        )
        if (sound != None) and (sound["matches"] < threshold):
                sound = None
        return sound



