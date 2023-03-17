import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse

# takes in a time and returns the corresponding index in the spectrogram matrix
def t2ind(t):
    return next(x for x, val in enumerate(times) if val > t)

# input parse
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('-s','--src', type=str, help='src file (wav format)')
args = parser.parse_args()

# load audio file
# caution: WAV files can be 1-channel (mono) or 2-channel (stereo)
sample_rate, samples = wavfile.read(args.src)
num_samples = samples.shape[0]
#print("Num Samples:", num_samples)
#print("Sample Rate:", sample_rate)

# do spectrogram
window_length = 10000
window = np.hamming(window_length)
frequencies, times, spectrogram = signal.spectrogram(samples[:,0], sample_rate, window)
spectrogram /= spectrogram.max()
spectrogram_rows = range(len(spectrogram))  # rows represent frequencies
spectrogram_columns = range(len(spectrogram[0]))    # columns represent time-divisions

# perform basic thresholding
magn_threshold = 0.5
thresh_spectrogram = 0*spectrogram
for i in spectrogram_rows:
    for j in spectrogram_columns:
        if spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1

# plot spectrograms
plt.subplot(1, 2, 1)
plt.pcolormesh(times, frequencies, spectrogram)
plt.ylim(0, 1000)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()

plt.subplot(1, 2, 2)
plt.pcolormesh(times, frequencies, thresh_spectrogram)
plt.ylim(0, 1000)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.show()

# plot frequency spectrum at some time
'''
data = spectrogram[:, t2ind(52.3)]
plt.plot(frequencies, data)
plt.xlim(0, 1000)
plt.show()
'''