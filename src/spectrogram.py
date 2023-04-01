import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse
import math
from util import *
from notes import *

# parse input
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('-s','--src', type=str, help='src file (wav format)')
args = parser.parse_args()

# load audio file (caution: WAV files can be 1- or 2-channel)
sample_rate, samples = wavfile.read(args.src)
num_samples = samples.shape[0]
print("Num Samples:", num_samples)
print("Sample Rate:", sample_rate)

# do spectrogram
window_length_samples = 5000    # window too short -> note getting too 'spread out' in frequency
zero_pad_samples = 2.0*window_length_samples
Wtot = window_length_samples + zero_pad_samples
window = np.hamming(window_length_samples)
frequencies, times, spectrogram = signal.spectrogram(samples[:,0], sample_rate, window, nfft=Wtot)
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

"""
# List detected notes
for (t, n) in detected_notes_list:
    print("Time: ", t, "Note: ", n)
"""

#"""
# plot spectrogram
plt.pcolormesh(times, frequencies, thresh_spectrogram)
plt.ylim(0, 1000)
plt.xlim(0, 14)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()
plt.show()
#"""

"""
# plot frequency spectrum at some time
data = spectrogram[:, t2ind(52.3, times)]
plt.plot(frequencies, data)
plt.xlim(0, 1000)
plt.show()
"""

"""
# plot volume over time
plt.plot(times, volume)
plt.xlim(0, 15)
plt.show()
"""

"""
# plot volume histogram
plt.hist(volume, bins=500)
plt.xlim(0, 0.1)
plt.show()
"""

##################### OLD STUFF ##########################
"""
# perform basic thresholding (original spectrogram)
magn_threshold = 0.9
thresh_spectrogram = 0*spectrogram
detected_notes_list = []
for j in range(spect_cols):
    for i in range(spect_rows):
        if spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1
            if not [times[j], freq2note(frequencies[i],piano_frequencies)] in detected_notes_list:
                detected_notes_list.append([times[j], freq2note(frequencies[i],piano_frequencies)])
"""

"""
# interpolate spectrogram in frequency axis
df = 0.1
min_f = 0
max_f = 1000
fnew_arr = np.arange(min_f, max_f, df)
interp_spect_rows = len(fnew_arr)
interp_spectrogram = np.zeros((interp_spect_rows, spect_cols))
for j in range(spect_cols):
    interp_spectrogram[:, j] = np.interp(fnew_arr, frequencies, spectrogram[:, j])

# perform basic thresholding (interpolated spectrogram)
magn_threshold = 0.4
thresh_spectrogram = 0*interp_spectrogram
detected_notes_list = []
for j in range(spect_cols):
    for i in range(interp_spect_rows):
        if interp_spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1
            if not [times[j], freq2note(fnew_arr[i],piano_frequencies)] in detected_notes_list:
                detected_notes_list.append([times[j], freq2note(fnew_arr[i],piano_frequencies)])

# plot spectrogram
#plt.pcolormesh(times, fnew_arr, interp_spectrogram)
plt.ylim(0, 1000)
#plt.xlim(0, 12)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()
plt.show()
"""