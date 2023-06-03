#!/usr/bin/python3

import subprocess
import numpy
import os


class AudioCorrelation:
    """ Correlate audio files """

    def __init__(self):
        # seconds to sample audio file for
        self.sample_time = 3
        # number of points to scan cross correlation over
        self.span = 1
        # step size (in points) of cross correlation
        self.step = 1
        # minimum number of points that must overlap in cross correlation
        # exception is raised if this cannot be met
        self.min_overlap = 1
        # report match when cross correlation has a peak exceeding threshold
        self.threshold = 0.5

    # calculate fingerprint
    # Generate file.mp3.fpcalc by "fpcalc -raw -length 500 file.mp3"
    def calculate_fingerprints(self, filename):
        if os.path.exists(filename + '.fpcalc'):
            print("Found precalculated fingerprint for %s" % (filename))
            f = open(filename + '.fpcalc', "r")
            fpcalc_out = ''.join(f.readlines())
            f.close()
        else:
            print("Calculating fingerprint by fpcalc for %s" % (filename))
            fpcalc_out = str(subprocess.check_output(['fpcalc', '-raw', '-length', str(self.sample_time), filename])).strip().replace('\\n', '').replace("'", "")
        fingerprint_index = fpcalc_out.find('FINGERPRINT=') + 12
        # convert fingerprint to list of integers
        fingerprints = list(map(int, fpcalc_out[fingerprint_index:].split(',')))
        
        return fingerprints

    # returns correlation between lists
    def correlation(self, listx, listy):
        if len(listx) == 0 or len(listy) == 0:
            # Error checking in main program should prevent us from ever being
            # able to get here.
            raise Exception('Empty lists cannot be correlated.')
        if len(listx) > len(listy):
            listx = listx[:len(listy)]
        elif len(listx) < len(listy):
            listy = listy[:len(listx)]
        
        covariance = 0
        for i in range(len(listx)):
            covariance += 32 - bin(listx[i] ^ listy[i]).count("1")
        covariance = covariance / float(len(listx))
        
        return covariance/32

    # return cross correlation, with listy offset from listx
    def cross_correlation(self, listx, listy, offset):
        if offset > 0:
            listx = listx[offset:]
            listy = listy[:len(listx)]
        elif offset < 0:
            offset = -offset
            listy = listy[offset:]
            listx = listx[:len(listy)]
        if min(len(listx), len(listy)) < self.min_overlap:
            # Error checking in main program should prevent us from ever being
            # able to get here.
            return 
        #raise Exception('Overlap too small: %i' % min(len(listx), len(listy)))
        return self.correlation(listx, listy)

    # cross correlate listx and listy with offsets from -span to span
    def compare(self, listx, listy, span, step):
        if span > min(len(listx), len(listy)):
            # Error checking in main program should prevent us from ever being
            # able to get here.
            raise Exception('span >= sample size: %i >= %i\n'
                            % (span, min(len(listx), len(listy)))
                            + 'Reduce span, reduce crop or increase sample_time.')
        corr_xy = []
        for offset in numpy.arange(-span, span + 1, step):
            corr_xy.append(self.cross_correlation(listx, listy, offset))
        return corr_xy

    # return index of maximum value in list
    def max_index(self, listx):
        max_index = 0
        max_value = listx[0]
        for i, value in enumerate(listx):
            if value > max_value:
                max_value = value
                max_index = i
        return max_index

    def get_max_corr(self, corr, source, target):
        max_corr_index = self.max_index(corr)
        max_corr_offset = -self.span + max_corr_index * self.step
        #print("max_corr_index = ", max_corr_index, "max_corr_offset = ", max_corr_offset)
        # report matches
        if corr[max_corr_index] > self.threshold:
            print('Sound similarity of %.2f%% at offset %i' % (corr[max_corr_index] * 100.0, max_corr_offset))
            return corr[max_corr_index]
    
    def correlate(self, source, target):
        fingerprint_source = self.calculate_fingerprints(source)
        fingerprint_target = self.calculate_fingerprints(target)
        corr = self.compare(fingerprint_source, fingerprint_target, self.span, self.step)
        return self.get_max_corr(corr, source, target)