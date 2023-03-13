import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse

# ArgumentParser for input parse
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('-s','--src', type=str, help='src file (wav format)')
args = parser.parse_args()

# Load audio file
sample_rate, samples = wavfile.read(args.src)

# Define spectrogram parameters
nfft = 1 # length of the FFT window
window = signal.windows.hann(nfft)

# Calculate spectrogram
frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, window=window)

# Plot spectrogram
plt.pcolormesh(times, frequencies, spectrogram, shading='gouraud')
#plt.xlabel('Time (s)')
#plt.ylabel('Frequency (Hz)')
#plt.title('Spectrogram of Example Song')
#plt.colorbar()
#plt.savefig('spectrogram.png')
plt.show()
