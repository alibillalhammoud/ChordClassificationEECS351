import os
import math
import numpy as np
from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

from notes import *

def readWAV(audio_file: str):
	#If the audio data has multiple channels combine them by summing
	if not isinstance(audio_file, str):
		raise TypeError("Argument must be a string")
	sample_rate, samples = wavfile.read(audio_file)
	# only take first audio channel and write to a new WAV file
	if len(samples.shape) > 1:
		#samples = samples[:,0]
		samples = samples.sum(axis=1) # we may do something more advanced in the future
		# samples = samples / np.max(np.abs(samples)) #normalize audio data [-1, 1]
		merged_wavfile = os.path.dirname(os.path.abspath(audio_file)) + "/merged_" + os.path.basename(audio_file)
		wavfile.write(merged_wavfile, sample_rate, samples)
	return sample_rate, samples, len(samples)


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
	if padtype == "end":
		frequencies, times, spectrogram = signal.spectrogram(samples, window=hamming_window, fs=sample_rate, nfft=dft_length, noverlap=0)
	"""
	elif padtype== "beginend":
		hamming_window = signal.windows.hann(window_length)
		pad_width = 100 # begin and end with zeros
		hamming_window = np.pad(hamming_window, pad_width=((pad_width, pad_width)), mode='constant')
		frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, window=hamming_window, nperseg=window_length+2*pad_width, noverlap=0)
	"""
	spectrogram /= spectrogram.max()
	return frequencies, times, spectrogram


def do_col_normalization(spectrogram, volume, volume_threshold):
	# normalize each column if the volume is big enough
	# volume condition avoids division by zero
	spect_cols = len(spectrogram[0])    # columns represent time-divisions
	col_norm_spectrogram = 0*spectrogram
	for j in range(spect_cols):
		if volume[j] > volume_threshold:
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


def get_harmonic_spectrogram(input_spectrogram, magn_threshold):
	harmonic_spectrogram = 0*input_spectrogram
	spect_rows = len(input_spectrogram)			# rows represent frequencies
	spect_cols = len(input_spectrogram[0])		# columns represent time-divisions
	for j in range(spect_cols):
		for i in range(spect_rows):
			if (input_spectrogram[i, j] > magn_threshold) and (input_spectrogram[math.floor(1.0*i/2), j] > magn_threshold):
				harmonic_spectrogram[i, j] = input_spectrogram[i, j]
			else:
				harmonic_spectrogram[i, j] = 0
	return harmonic_spectrogram


def do_harmonic_correction(input_spectrogram, harmonic_threshold, cut_amount):
	return np.clip(input_spectrogram - cut_amount*get_harmonic_spectrogram(input_spectrogram, harmonic_threshold), 0, 1)


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


def print_detected_notes(detected_notes_list):
	for (t, n) in detected_notes_list:
		print("Time: ", t, "Note: ", n)


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

# subdivisions within an octave - may be useful
# [1.059, 1.122, 1.189, 1.260, 1.335, 1.414, 1.498, 1.587, 1.682, 1.782, 1.888]