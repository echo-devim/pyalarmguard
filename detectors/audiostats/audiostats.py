
import subprocess
import config

class AudioStats:
    """ SoX wrapper class """

    def highPassFilter(self, wavfile):
        """ Apply high-pass filter to wav file """
        newwavfile = wavfile.replace(".wav","_filtered.wav")
        subprocess.run(['sox', wavfile, newwavfile, 'sinc', config.high_pass_filter_cutoff])
        return newwavfile

    def getStats(self, wavfile):
        return subprocess.check_output(['sox', wavfile, '-n', 'stats'], stderr=subprocess.STDOUT).decode("utf-8").strip()
    
    def getProperty(self, wavfile, property):
        for prop in self.getStats(wavfile).split("\n"):
            if property in prop:
                return float(prop.split(" ")[-1])
        return None