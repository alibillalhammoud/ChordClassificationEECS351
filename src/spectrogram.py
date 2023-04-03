import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import argparse
import math

from util import *
from notes import *

# parse input
parser = argparse.ArgumentParser(description='Perform note detection on input src file')
parser.add_argument('-s','--src', type=argparse.FileType('r'), help='src file (wav format)', required=True)
args = parser.parse_args()

# load audio into a 1D numpy array. Merges audio if more than 1 channel
sample_rate, samples, num_samples = readWAV(args.src.name)
print("Num Samples:", num_samples)
print("Sample Rate:", sample_rate)

# do spectrogram
window_length_samples = 5000    # window too short -> note getting too 'spread out' in frequency
Wtot = 2 * window_length_samples
window = np.hamming(window_length_samples)
padtype="beginend"
if padtype == "end":
	frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, nperseg=window_length_samples, nfft=Wtot, noverlap=0)
elif padtype== "beginend":
	window = signal.windows.hann(window_length_samples)
	pad_width = 100 # begin and end with zeros
	window = np.pad(window, pad_width=((pad_width, pad_width)), mode='constant')
	frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, window=window, nperseg=window_length_samples+2*pad_width, noverlap=0)
	#frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate, window, nfft=Wtot)
#elif padtype == "ends":
#	frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate, window, nfft=Wtot)

#plotSpectrogram(frequencies,times,spectrogram)

spectrogram /= spectrogram.max()
spect_rows = len(spectrogram)           # rows represent frequencies
spect_cols = len(spectrogram[0])        # columns represent time-divisions
spect_dt = window_length_samples/sample_rate
spect_df = sample_rate/Wtot

print("Spectrogram dt: ", spect_dt)
print("Spectrogram df: ", spect_df)
print("Spectrogram Rows: ", spect_rows)
print("Spectrogram Columns: ", spect_cols)

#"""
# calculate volume as function of time
volume = [0] * spect_cols
for j in range(spect_cols):
    # parseval's thereom
    for i in range(spect_rows):
        volume[j] = volume[j] + spectrogram[i, j]**2                # probably want to normalize volume
volume /= max(volume)
#"""

#"""
# normalize each column, if the volume is big enough
# volume condition avoids division by zero
volume_threshold = 0.01
col_norm_spectrogram = 0*spectrogram
for j in range(spect_cols):
    if volume[j] > volume_threshold:
        col_norm_spectrogram[:, j] = spectrogram[:, j] / spectrogram[:, j].max()
#"""

#"""
# threshold column-normalized, volume-filtered spectrogram
magn_threshold = 0.2
thresh_spectrogram = 0*spectrogram
detected_notes_list = []
for j in range(spect_cols):
    for i in range(spect_rows):
        if col_norm_spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1
            # keep track of notes that pass the threshold
            if not [times[j], freq2note(frequencies[i],piano_frequencies)] in detected_notes_list:
                detected_notes_list.append([times[j], freq2note(frequencies[i],piano_frequencies)])
#"""


# List detected notes
#for (t, n) in detected_notes_list:
#    print("Time: ", t, "Note: ", n)


#"""
# plot spectrogram
plt.pcolormesh(times, frequencies, thresh_spectrogram)
plt.ylim(0, 1000)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()
plt.show()
#"""


## plot frequency spectrum at some time
#data = spectrogram[:, t2ind(52.3, times)]
#plt.plot(frequencies, data)
#plt.xlim(0, 1000)
#plt.show()

## plot volume over time
#plt.plot(times, volume)
#plt.xlim(0, 15)
#plt.show()

## plot volume histogram
#plt.hist(volume, bins=500)
#plt.xlim(0, 0.1)
#plt.show()

# see git commit history for old stuff

