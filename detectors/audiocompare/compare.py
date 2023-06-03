#!/usr/bin/python3
# compare.py

from detectors.audiocompare.correlation import AudioCorrelation

class AudioCompare:
    """ Compare wav file with one of the sounds saved in 'samples' directory """

    def __init__(self):
        self.sample_dir = "/opt/pyalarmguard/detectors/audiocompare/samples" #absolute path required
        self.audio_correlation = AudioCorrelation()
    
    def compare(self, source, dest):
        return self.audio_correlation.correlate(source, dest)
    
    def isSimilarTo(self, inputfile, soundname, threshold = 0.71):
        cmpres = self.compare(inputfile, f"{self.sample_dir}/{soundname}.wav")
        return (cmpres > threshold)