import wave
import numpy as np
import sys

class SignalProcessing:

    def __init__(self):
        self.processed_signals = {}

    def getSignalArray(self, wavname, plot=False):
        """ Read signal amplitude values from wav file """
        wav_obj = wave.open(wavname, 'rb')
        n_samples = wav_obj.getnframes()
        sample_freq = wav_obj.getframerate()
        t_audio = n_samples/sample_freq
        signal_wave = wav_obj.readframes(n_samples)
        signal_array = np.frombuffer(signal_wave, dtype=np.int16)
        if wav_obj.getnchannels() > 1:
            print("Attention: Only wav with mono channel are supported")
            l_channel = signal_array[0::2]
            r_channel = signal_array[1::2]
            # Consider only one channel
            signal_array = l_channel
        times = np.linspace(0, n_samples/sample_freq, num=n_samples)
        if plot:
            import matplotlib.pyplot as plt
            # Plot amplitude
            plt.figure(figsize=(15, 5))
            plt.plot(times, signal_array)
            plt.title('Channel')
            plt.ylabel('Signal Value')
            plt.xlabel('Time (s)')
            plt.xlim(0, t_audio)
            plt.show()
        return signal_array

    def normalize(self, signal_array):
        """ Normalize signal values """
        # Signal can have positive and negative values
        # Find the minimum value
        minval = np.abs(np.amin(signal_array))
        # Add the minimum value to all the elements of the array (signal translation)
        signal_array = signal_array + minval
        # Sort the values using descending order
        # this implies ignoring time information
        signal_array = np.sort(signal_array)[::-1]
        return signal_array

    def compare(self, srcsig, dstsig):
        """ compare two signals returning how much similar they are """
        srcsig = self.normalize(srcsig)
        dstsig = self.normalize(dstsig)
        g = 0.
        m = 0
        for i in range(0, np.amin([len(srcsig), len(dstsig)])):
            # Calculate the difference between signal values with some tollerance
            if np.abs(srcsig[i] - dstsig[i]) < 15:
                m += 1
            g += 1
        ratio = m/g
        #print(f"Found {m} matches , ratio {ratio}")
        return ratio
    
    def calculateSimilarity(self, wav1, wav2, store1=False, store2=False):
        if store1 and (wav1 in self.processed_signals):
            s1 = self.processed_signals[wav1]
        else:
            s1 = self.getSignalArray(wav1)
            self.processed_signals[wav1] = s1
        
        if store2 and (wav2 in self.processed_signals):
            s2 = self.processed_signals[wav2]
        else:
            s2 = self.getSignalArray(wav2)
            self.processed_signals[wav2] = s2
        
        return self.compare(s1, s2)


## Plot frequency
#plt.figure(figsize=(15, 5))
#plt.specgram(signal_array, Fs=sample_freq, vmin=-20, vmax=50)
#plt.title('Left Channel')
#plt.ylabel('Frequency (Hz)')
#plt.xlabel('Time (s)')
#plt.xlim(0, t_audio)
#plt.colorbar()
#plt.show()