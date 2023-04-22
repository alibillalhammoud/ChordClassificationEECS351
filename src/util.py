import os
import math
import numpy as np
from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
from pychord import find_chords_from_notes 
from pychord import Chord

from notes import *

def get_volume_array(spectrogram):
	spect_rows = len(spectrogram)		# rows represent frequencies
	spect_cols = len(spectrogram[0])    # columns represent time-divisions
	volume = [0] * spect_cols
	for j in range(spect_cols):
		for i in range(spect_rows):
			volume[j] = volume[j] + spectrogram[i, j]**2	# parseval's thereom

	volume /= max(volume)
	return volume


def do_spectrogram(samples, sample_rate, window_length, padding_factor, padtype):
	dft_length = window_length + padding_factor*window_length
	hamming_window = np.hamming(window_length)
	frequencies, times, spectrogram = signal.spectrogram(samples, window=hamming_window, fs=sample_rate, nfft=dft_length, noverlap=0)
	spectrogram /= spectrogram.max()
	return frequencies, times, spectrogram


def do_col_normalization(spectrogram, volume, volume_threshold):
	# normalize each column if the volume is big enough
	# volume condition avoids division by zero
	spect_cols = len(spectrogram[0])    # columns represent time-divisions
	col_norm_spectrogram = 0*spectrogram
	for j in range(spect_cols):
		if volume[j] > volume_threshold:
			#print("Volume threshold met")
			col_norm_spectrogram[:, j] = spectrogram[:, j] / spectrogram[:, j].max()
	return col_norm_spectrogram


def do_bass_boost(input_spectrogram, frequencies, f_thresh, boost_mag):
	bb_spectrogram = input_spectrogram
	spect_rows = len(input_spectrogram)			# rows represent frequencies
	spect_cols = len(input_spectrogram[0])		# columns represent time-divisions
	for j in range(spect_cols):
		for i in range(spect_rows):
			if frequencies[i] < f_thresh and input_spectrogram[i, j] > 0.01:
				bb_spectrogram[i, j] = np.clip(bb_spectrogram[i, j] * boost_mag, 0, 1)
	return bb_spectrogram


# returns spectrogram of just the identified harmonics
def get_harmonic_spectrogram(input_spectrogram, magn_threshold, harmonic_orders):
	harmonic_spectrogram = 0*input_spectrogram
	spect_rows = len(input_spectrogram)			# rows represent frequencies
	spect_cols = len(input_spectrogram[0])		# columns represent time-divisions
	for j in range(spect_cols):
		for i in range(spect_rows):
			for h in harmonic_orders:
				if (input_spectrogram[i, j] > magn_threshold) and (input_spectrogram[math.floor(1.0*i/h), j] > magn_threshold):
					harmonic_spectrogram[i, j] = input_spectrogram[i, j]
	return harmonic_spectrogram


# attenuates identified harmonics by 0-100%
def do_harmonic_correction(input_spectrogram, harmonic_threshold, cut_amount, harmonic_order):
	return np.clip(input_spectrogram - cut_amount*get_harmonic_spectrogram(input_spectrogram, harmonic_threshold, harmonic_order), 0, 1)


def do_thresholding(spectrogram, times, frequencies, note_frequencies, magn_threshold):
	thresh_spectrogram = 0*spectrogram
	spect_rows = len(spectrogram)		# rows represent frequencies
	spect_cols = len(spectrogram[0])    # columns represent time-divisions
	detected_notes_list = []
	for j in range(spect_cols):
		for i in range(spect_rows):
			if spectrogram[i, j] > magn_threshold:
				thresh_spectrogram[i, j] = 1
				if not [times[j], freq2note(frequencies[i],note_frequencies)] in detected_notes_list:
					detected_notes_list.append([times[j], freq2note(frequencies[i],note_frequencies)])
	return thresh_spectrogram, detected_notes_list


def print_detected_notes(detected_notes_list, toffset=0):
	for (t, n) in detected_notes_list:
		print(f"Time {t + toffset} : Note {n}")


def compute_metrics(spectrogram, sample_rate, window_length, padding_factor):
	dft_length = window_length + padding_factor*window_length
	spect_rows = len(spectrogram)           # rows represent frequencies
	spect_cols = len(spectrogram[0])        # columns represent time-divisions
	spect_dt = window_length/sample_rate
	spect_df = sample_rate/dft_length

	print("Spectrogram dt: ", spect_dt)
	print("Spectrogram df: ", spect_df)
	print("Spectrogram Rows: ", spect_rows)
	print("Spectrogram Columns: ", spect_cols)
	return


# takes in a time and returns the corresponding index in the spectrogram matrix
def t2ind(t, times):
    return next(x for x, val in enumerate(times) if val > t)


def freq2note(freq, piano_frequencies):
    smallest_diff = 1e6
    for (n, f) in piano_frequencies:
        diff = abs(f - freq)
        if diff < smallest_diff:
            smallest_diff = diff
            note = n
    return note


def plotSpectrogram(frequencies,times,spectrogram):
	#plt.pcolormesh(times, frequencies, np.log10(spectrogram))	# log10?
	plt.pcolormesh(times, frequencies, spectrogram)
	plt.ylim(0, 1000)
	plt.yscale("log", 10, [2, 5])
	plt.xlabel('Time (s)')
	plt.ylabel('Frequency (Hz)')
	plt.colorbar()
	plt.show()

def addNoteScale(fig) :
	ax = fig.get_axes()[0]

	ax.set_yscale("log")

	def noteLabeler(x, y) :
		return freq2note(x, note_frequencies)

	majtickfreq = []
	mintickfreq = []
	n = 0
	for i in note_frequencies :
		if n%4 == 0 :
			majtickfreq.append(i[1])
		else :
			mintickfreq.append(i[1])
		n += 1

	ax.yaxis.set_major_locator(tick.FixedLocator(majtickfreq))
	ax.yaxis.set_minor_locator(tick.FixedLocator(mintickfreq))
	ax.yaxis.set_major_formatter(tick.FuncFormatter(noteLabeler))

	# uncomment for no labels for in-between notes (nptes that are not C, E, G#):
	ax.yaxis.set_minor_formatter(tick.NullFormatter())

	# uncomment for labels for in-between notes (nptes that are not C, E, G#):
	# ax.yaxis.set_minor_formatter(FuncFormatter(noteLabeler))


def print_chord(detected_notes_list, toffset=0):
	notes_list = []
	for i in range(len(detected_notes_list)):
		notes_list.append(detected_notes_list[i][1][0:-1])

	notes_list_nodup = []
	for i in range(len(notes_list)):
		if not notes_list[i] in notes_list_nodup:
			notes_list_nodup.append(notes_list[i])

	print(notes_list_nodup)
	if len(notes_list_nodup) > 0:
		print(find_chords_from_notes(notes_list_nodup))
		
	return
