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
length = samples.shape[0] / sample_rate
time = np.linspace(0., length, samples.shape[0])



# Define spectrogram parameters
nfft = 1 # length of the FFT window
window = signal.windows.hann(nfft)

# Calculate spectrogram
frequencies, times, spectrogram = signal.spectrogram(samples[:,0], sample_rate)

#print(frequencies)
#print(times)
# Plot spectrogram
#plt.pcolormesh(times, np.fft.fftshift(frequencies), np.fft.fftshift(spectrogram, axes=0))
plt.pcolormesh(times, frequencies, spectrogram)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram of Example Song')
plt.colorbar()
plt.savefig('spectrogram.png')
plt.show()
