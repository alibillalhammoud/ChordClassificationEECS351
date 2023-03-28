import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse
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
window_length_samples = 10000
zero_pad_samples = 10000
Wtot = window_length_samples + zero_pad_samples
window = np.hamming(window_length_samples)
frequencies, times, spectrogram = signal.spectrogram(samples[:,0], sample_rate, window, nfft=Wtot)
spectrogram /= spectrogram.max()
spect_rows = len(spectrogram)           # rows represent frequencies
spect_cols = len(spectrogram[0])        # columns represent time-divisions

print("Spectrogram Rows: ", spect_rows)
print("Spectrogram Columns: ", spect_cols)

#"""
# interpolate spectrogram in frequency axis
df = 0.1
min_f = 0
max_f = 1000
fnew_arr = np.arange(min_f, max_f, df)
interp_spect_rows = len(fnew_arr)
interp_spectrogram = np.zeros((interp_spect_rows, spect_cols))
for j in range(spect_cols):
    interp_spectrogram[:, j] = np.interp(fnew_arr, frequencies, spectrogram[:, j])
#"""

#"""
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
#"""

"""
# List detected notes
for (t, n) in detected_notes_list:
    print("Time: ", t, "Note: ", n)
"""

#"""
# plot spectrogram
plt.pcolormesh(times, frequencies, spectrogram)
#plt.pcolormesh(times, fnew_arr, interp_spectrogram)
plt.ylim(0, 1000)
#plt.xlim(0, 12)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()
plt.show()
#"""

# plot frequency spectrum at some times
"""
data = spectrogram[:, t2ind(52.3, times)]
plt.plot(frequencies, data)
plt.xlim(0, 1000)
plt.show()
"""

##################### OLD STUFF ##########################

# perform basic thresholding (original spectrogram)
"""
magn_threshold = 0.5
thresh_spectrogram = 0*spectrogram
detected_notes_list = []
for j in range(spect_columns):
    for i in range(spect_rows):
        if spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1
            if not [times[j], freq2note(frequencies[i],piano_frequencies)] in detected_notes_list:
                detected_notes_list.append([times[j], freq2note(frequencies[i],piano_frequencies)])
#
"""