import wave
import struct
import math
import pyaudio
import os

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
        self.wavfile = '/opt/pyalarmguard/record.wav'
        self.last_peak_dB = 0
    
    def getEvidenceFile(self):
        return self.wavfile

    #def getPeakdB(self, wavfile):
    #    """ Simple function to get peak dB in the wav file """
    #    # Open the audio file
    #    with wave.open(wavfile, 'r') as audio:
    #        # Extract the raw audio data
    #        raw_data = audio.readframes(audio.getnframes())
#
    #    # Convert the raw audio data to a list of integers
    #    samples = struct.unpack('<{n}i'.format(n=audio.getnframes()), raw_data)
#
    #    # Find the peak sample
    #    peak = max(samples)
#
    #    # Calculate the reference value based on the bit depth of the audio file
    #    reference_value = 2**(audio.getsampwidth() * 8 - 1)
#
    #    # Calculate the peak value in dBFS, using the maximum possible sample value as the reference value
    #    peak_dB = 20 * math.log10(peak / reference_value)
#
    #    return peak_dB
#
#
    #def alarm(self):
    #    """ Detect if audio from mic contains alarm sound """
    #    #peak_dB = self.getPeakdB(self.wavfile)
    #    #self.last_peak_dB = peak_dB
    #    #if (peak_dB > self.threshold):
    #    #    self.logger.info(f"Registered peak with dB {peak_dB} exceeding threshold ({self.threshold})")
    #    #    return True
    #    #return False
#
    #    
    #    return self.wavfile

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



