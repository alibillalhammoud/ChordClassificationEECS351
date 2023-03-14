import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.io import wavfile
import argparse

# input parse
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('-s','--src', type=str, help='src file (wav format)')
args = parser.parse_args()

# load audio file
# caution: WAV files can be 1-channel (mono) or 2-channel (stereo)
sample_rate, samples = wavfile.read(args.src)
print("Num Samples:", samples.shape[0])
print("Sample Rate:", sample_rate)

# do spectrogram
window_length = 10000
window = np.hamming(window_length)
frequencies, times, spectrogram = signal.spectrogram(samples[:,0], sample_rate, window)

# plot
plt.pcolormesh(times, frequencies, spectrogram)
#plt.xlim(0, 60)
#plt.ylim(0, 1000)
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.title('Spectrogram of Example Song')
plt.colorbar()
plt.savefig('spectrogram.png')
plt.show()
