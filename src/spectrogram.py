import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse

# define frequencies as in https://en.wikipedia.org/wiki/Piano_key_frequencies
piano_frequencies = [("C3", 130.8),
                     ("C#3", 138.6),
                     ("D3", 146.8),
                     ("D#3", 155.6),
                     ("E3", 164.8),
                     ("F3", 174.6),
                     ("F#3", 185),
                     ("G3", 196),
                     ("G#3", 207.7),
                     ("A3", 220),
                     ("Bb3", 233.1),
                     ("B3", 246.9),
                     ("C4", 261.6),
                     ("C#4", 277.2),
                     ("D4", 293.7),
                     ("D#4", 311.1),
                     ("E4", 329.6),
                     ("F4", 349.2),
                     ("F#4", 370),
                     ("G4", 392),
                     ("G#4", 415.3),
                     ("A4", 440),
                     ("Bb4", 466.16),
                     ("B4", 493.9),
                     ("C5", 523.3),
                     ("C#5", 554.4),
                     ("D5", 587.3),
                     ("D#5", 622.3),
                     ("E5", 659.3),
                     ("F5", 698.5),
                     ("F#5", 740),
                     ("G5", 784),
                     ("G#5", 830.6),
                     ("A5", 880),
                     ("Bb5", 932.3),
                     ("B5", 987.8),
                     ("C6", 1046.5),
                     ("C#6", 1108.7),
                     ("D6", 1174.7),
                     ("D#6", 1244.5),
                     ("E6", 1318.5),
                     ("F6", 1396.9),
                     ("F#6", 1480),
                     ("G6", 1568),
                     ("G#6", 1661.2),
                     ("A6", 1760),
                     ("Bb6", 1864.7),
                     ("B6", 1975.5),
                     ("C7", 2093)
                     ]

# takes in a time and returns the corresponding index in the spectrogram matrix
def t2ind(t):
    return next(x for x, val in enumerate(times) if val > t)

def freq2note(freq):
    smallest_diff = 1e6
    for (n, f) in piano_frequencies:
        diff = abs(f - freq)
        if diff < smallest_diff:
            smallest_diff = diff
            note = n
    return note

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
magn_threshold = 0.04
thresh_spectrogram = 0*spectrogram
detected_notes_list = []
for j in spectrogram_columns:
    for i in spectrogram_rows:
        if spectrogram[i, j] > magn_threshold:
            thresh_spectrogram[i, j] = 1
            detected_notes_list.append([times[j], freq2note(frequencies[i])])

# List detected notes 'cells'
for (t, n) in detected_notes_list:
    print("Time: ", t, "Note: ", n)

# plot spectrograms
#plt.subplot(1, 2, 1)
plt.pcolormesh(times, frequencies, thresh_spectrogram)
plt.ylim(0, 1000)
plt.xlim(0, 20)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.colorbar()

"""
plt.subplot(1, 2, 2)
plt.pcolormesh(times, frequencies, thresh_spectrogram)
#plt.ylim(0, 1000)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
"""
plt.show()
# plot frequency spectrum at some time
'''
data = spectrogram[:, t2ind(52.3)]
plt.plot(frequencies, data)
plt.xlim(0, 1000)
plt.show()
'''