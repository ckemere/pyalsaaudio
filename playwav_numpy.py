#!/usr/bin/env python3

# Simple test script that plays (some) wav files

from __future__ import print_function

import sys
import scipy.io.wavfile
import getopt
import alsaaudio
import numpy as np
from itertools import cycle

def play(device, song, fs, mod=None, 
        audio_format=alsaaudio.PCM_FORMAT_S16_LE, buffer_size=256):    

    if song.ndim > 1:
        print('%d channels, %d sampling rate\n' % (song.shape[1],fs))
        nchan = song.shape[1]
    else:
        print('%d channels, %d sampling rate\n' % (1,fs))
        nchan = 1

    # Set attributes
    device.setchannels(nchan)
    device.setrate(fs)
    device.setformat(audio_format)
    device.setperiodsize(buffer_size)

    song_len = song.shape[0]

    if buffer_size > song_len:
        raise(ValueError('Buffer size must be smaller than or equal to length of song.'))

    data = np.zeros(buffer_size, dtype=song.dtype)
    
    data[:] = song[:buffer_size]
    print(data.dtype)

    curpos = buffer_size
    while True:
        # Read data from stdin
        if mod is not None:
            res, xruns = device.write(data * next(mod))

        if xruns != 0:
            print('Xruns: {}'.format(xruns))
        remainder = curpos + buffer_size - song_len
        if remainder > 0:
            first = song_len - curpos
            data[:first] = song[curpos:(curpos+first)]
            data[first:] = song[:remainder]
            curpos = remainder
        else:
            data[:] = song[curpos:(curpos+buffer_size)]
            curpos += buffer_size



def usage():
    print('usage: playwav.py [-d <device>] <file>', file=sys.stderr)
    sys.exit(2)

if __name__ == '__main__':

    device = 'default'

    opts, args = getopt.getopt(sys.argv[1:], 'd:')
    for o, a in opts:
        if o == '-d':
            device = a

    if not args:
        usage()
        
    fs, song = scipy.io.wavfile.read(args[0])

    buf_size = 8

    mod1 = np.ones(buf_size)
    mod2 = np.ones(buf_size) * 0.8
    mod = cycle([mod1, mod2])

    device = alsaaudio.PCM(device=device)

    play(device, song, fs, mod=mod, buffer_size=buf_size)

