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

# load audio
sample_rate, samples, num_samples = readWAV(args.src.name)
print("Num Samples:", num_samples)
print("Sample Rate:", sample_rate)

# do spectrogram
window_length = 5000
padding_factor = 5
frequencies, times, spectrogram = do_spectrogram(samples, sample_rate, window_length, padding_factor, "end")

# compute and print some metrics
compute_metrics(spectrogram, sample_rate, window_length, padding_factor)

# measure volume over time
volume = get_volume_array(spectrogram)

# normalize individual columns
volume_threshold = 0.01
col_norm_spectrogram = do_col_normalization(spectrogram, volume, volume_threshold)

# do thresholding and note detection
magn_threshold = 0.8
thresh_spectrogram, detected_notes_list = do_thresholding(col_norm_spectrogram, times, frequencies, note_frequencies, magn_threshold)

#print_detected_notes(detected_notes_list)

######## Plotting ##########

#"""
# plot spectrogram

# set our ylimits here
# Current lowest freq labeled, C3: 130.8Hz
# Current highest freq labeled, C7: 2093Hz

ybot = 100
ytop = 2000

fig = plt.pcolormesh(times, frequencies, col_norm_spectrogram).get_figure()

# uncomment for the fancy note scale
addNoteScale(fig)

plt.ylim(ybot, ytop)

# uncomment if log scale is needed - log scale is already set in addNoteScale
# plt.yscale("log", base = 2, subs = [1.059, 1.122, 1.189, 1.260, 1.335, 1.414, 1.498, 1.587, 1.682, 1.782, 1.888])

plt.xlim(0, 15)
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
plt.xlabel('Time (s)')
plt.ylabel('Volume (norm)')
plt.show()
"""

"""
# plot volume histogram
plt.hist(volume, bins=500)
plt.xlim(0, 0.1)
plt.xlabel('Volume (norm)')
plt.show()
"""
