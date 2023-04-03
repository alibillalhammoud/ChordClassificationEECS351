import os
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

def readWAV(audio_file: str):
	"""If the audio data has multiple channels combine them by summing"""
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
	plt.pcolormesh(times, frequencies, np.log10(spectrogram))
	plt.ylim(0, 1000)
	plt.xlabel('Time (s)')
	plt.ylabel('Frequency (Hz)')
	plt.colorbar()
	plt.show()
