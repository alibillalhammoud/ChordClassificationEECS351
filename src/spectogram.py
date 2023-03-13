import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse

# ArgumentParser for input parse
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('-s','--src', type=str, help='src file (wav format)')

# Load audio file
sample_rate, samples = wavfile.read("example_song.wav")

# Define spectrogram parameters
nfft = 1024 # length of the FFT window
hop_length = 512 # number of samples between successive frames
window = signal.windows.hann(nfft)

# Calculate spectrogram
frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, window=window, nfft=nfft, hop_length=hop_length)

# Plot spectrogram
plt.pcolormesh(times, frequencies, 10*np.log10(spectrogram), cmap='jet')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram of Example Song')
plt.colorbar()
plt.savefig('spectrogram.png')
plt.show()
