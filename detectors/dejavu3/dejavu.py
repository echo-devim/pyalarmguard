from dejavu.dejavu import Dejavu
from dejavu.recognize import FileRecognizer
from dejavu.dejavu import loggerer

class DejavuDetection:

    def __init__(self, logger):
        self.dburl = "sqlite:///audio.db"
        self.djv = Dejavu(dburl=self.dburl)
        self.djv.fingerprint_directory("samples", [".mp3", ".wav"])
        

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



