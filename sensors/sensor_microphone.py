import wave
import struct
import math
import os
import config
import subprocess
import time

# Remider: Do not use pyAudio because hangs the program when it fails to access the microphone
# Use external utility instead

class SensorMicrophone:

    def __init__(self, logger):
        self.logger = logger
        self.wavfile = f'{config.data_directory}/record.wav'
    
    def getEvidenceFile(self, format="wav"):
        """ Returns the original wav file or converts it into opus codec (e.g. to send it on telegram) """
        evidence = self.wavfile
        if format == "opus":
            evidence = self.wavfile + ".ogg"
            os.system(f"ffmpeg -i {self.wavfile} -y -c:a libopus {evidence}")
        return evidence

    def record(self, seconds):
        if os.path.exists(self.wavfile):
            os.remove(self.wavfile)

        attempts = 3

        while (attempts > 0):
            # Record audio Signed 16 bit Little Endian, Rate 48000 Hz, Mono
            subprocess.run(['arecord', "--duration", str(seconds), "--format", "dat", "--channels", "1", self.wavfile])

            # Check if output file exists and contains data
            if not os.path.exists(self.wavfile) or (os.path.getsize(self.wavfile) < 10):
                self.logger.error("Audio recording failed")
            else:
                return True

            attempts -= 1
            time.sleep(1)

        self.logger.error("Failed all attempts to record audio")

        # Remove noise with sox
        #if os.path.exists(self.wavfile):
        #    os.system(f"sox {self.wavfile} -n trim 0 0.5 noiseprof {config.data_directory}/noise.prof")
        #    os.system(f"sox {self.wavfile} {self.wavfile} noisered {config.data_directory}/noise.prof 0.21")

        return False



