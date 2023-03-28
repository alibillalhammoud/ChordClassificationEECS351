import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.interpolate import CubicSpline
import argparse
from util import *
from notes import *

# input parse
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('-s','--src', type=str, help='src file (wav format)')
args = parser.parse_args()

# load audio file
# caution: WAV files can be 1-channel (mono) or 2-channel (stereo)
sample_rate, samples = wavfile.read(args.src)
num_samples = samples.shape[0]
print("Num Samples:", num_samples)
print("Sample Rate:", sample_rate)

# do spectrogram
window_length = 10000
window = np.hamming(window_length)
frequencies, times, spectrogram = signal.spectrogram(samples[:,0], sample_rate, window)
spectrogram /= spectrogram.max()
spectrogram_rows = range(len(spectrogram))  # rows represent frequencies
spectrogram_columns = range(len(spectrogram[0]))    # columns represent time-divisions


# perform basic thresholding
magn_threshold = 0.04
thresh_spectrogram = 0*spectrogram
detected_notes_list = []
for j in spectrogram_columns:
    for i in spectrogram_rows:
        if spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1
            if not [times[j], freq2note(frequencies[i],piano_frequencies)] in detected_notes_list:
                detected_notes_list.append([times[j], freq2note(frequencies[i],piano_frequencies)])
#

# List detected notes 'cells'
"""
for (t, n) in detected_notes_list:
    print("Time: ", t, "Note: ", n)
#
"""

"""
# plot spectrogram
plt.pcolormesh(times, frequencies, spectrogram)
plt.ylim(0, 1000)
#plt.xlim(0, 12)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()
plt.show()
"""

# plot frequency spectrum at some times
#data = spectrogram[:, t2ind(52.3, times)]
fnew = np.linspace(1, 1000, 1000)
data = CubicSpline(frequencies, spectrogram[:, t2ind(52.3, times)])
plt.plot(fnew, data(fnew))
plt.xlim(0, 1000)
plt.show()
