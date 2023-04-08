from statistics import harmonic_mean
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
padding_factor = 2
frequencies, times, spectrogram = do_spectrogram(samples, sample_rate, window_length, padding_factor, "end")

# compute and print some metrics
compute_metrics(spectrogram, sample_rate, window_length, padding_factor)

# measure volume over time
volume = get_volume_array(spectrogram)

# normalize individual columns
volume_threshold = 0.01
col_norm_spectrogram = do_col_normalization(spectrogram, volume, volume_threshold)

# boost magnitude of low-frequency notes
#bass_boosted_spectrogram = do_bass_boost(col_norm_spectrogram, frequencies, 350, 2)
#bass_boosted_spectrogram = do_col_normalization(bass_boosted_spectrogram, volume, volume_threshold)

# 'cut' notes which are loud enough and have a signficant note 1 octave below
# harmonic_threshold: how loud does note and octave need to be before being cut
# harmonic_cut_amount: decimal representing amount of harmonic note that is removed
harmonic_cut_amount = 0.5
harmonic_threshold = 0.1
harmonic_corrected_spectrogram = do_harmonic_correction(col_norm_spectrogram, harmonic_threshold, harmonic_cut_amount)

# do thresholding and note detection
magn_threshold = 0.1
thresh_spectrogram, detected_notes_list = do_thresholding(harmonic_corrected_spectrogram, times, frequencies, note_frequencies, magn_threshold)

#print_detected_notes(detected_notes_list)

######## Plotting ##########

#"""
# plot spectrogram
plt.pcolormesh(times, frequencies, harmonic_corrected_spectrogram)
plt.ylim(0, 1000)
plt.xlim(3.5, 15)
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
