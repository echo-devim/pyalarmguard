import wave
import struct
import math
import pyaudio
import os
import config

class SensorMicrophone:

    def __init__(self, logger, threshold = 91):
        self.threshold = threshold
        self.logger = logger
        self.audio = pyaudio.PyAudio()
        # Find USB Microphone device index
        self.dev_index = -1
        for ii in range(self.audio.get_device_count()):
            if "USB PnP Sound Device" in self.audio.get_device_info_by_index(ii).get('name'):
                self.dev_index = ii
                break
        if self.dev_index == -1:
            logger.error("Cannot find USB microphone")
        self.wavfile = f'{config.data_directory}/record.wav'
        self.last_peak_dB = 0
    
    def getEvidenceFile(self, format="wav"):
        evidence = self.wavfile
        if format == "opus":
            evidence = self.wavfile + ".ogg"
            os.system(f"ffmpeg -i {self.wavfile} -ar 48000 -ac 2 -acodec libopus -ab 256k {evidence}")
            os.remove(self.wavfile)
        return evidence

    def record(self, seconds):
        if os.path.exists(self.wavfile):
            os.remove(self.wavfile)
        form_1 = pyaudio.paInt16 # 16-bit resolution
        chans = 1 # 1 channel
        samp_rate = 44100 # 44.1kHz sampling rate
        chunk = 4096 # 2^12 samples for buffer
        record_secs = seconds # seconds to record
        wav_output_filename = self.wavfile # name of .wav file
        # create pyaudio stream
        stream = self.audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = self.dev_index,input = True, \
                            frames_per_buffer=chunk)
        print("recording")
        frames = []

        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk, exception_on_overflow = False)
            frames.append(data)

        print("finished recording")

        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(self.audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()



