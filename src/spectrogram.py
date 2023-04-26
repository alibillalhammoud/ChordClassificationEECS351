from statistics import harmonic_mean
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import argparse
import math
from collections.abc import Iterable

from util import *
from notes import *

# store audio signal using this file type to unify the mic and scr file input methods
class AudioSignal:
    def __init__(self, samples: Iterable, sample_rate):
        if not isinstance(samples, Iterable):
            raise TypeError("Data must be list like")
        if not isinstance(int(sample_rate), int):
            raise TypeError("sample_rate must be a number")
        if len(samples.shape) > 1:
            samples = samples.sum(axis=1)
        self.samples = np.array(samples)
        self.num_samples = len(samples)
        self.sample_rate = int(sample_rate)

    @staticmethod
    def fromWAV(audio_file: str):
        # If the audio data has multiple channels combine them by summing
        if not isinstance(audio_file, str):
            raise TypeError("Argument must be a string")
        sample_rate, samples = wavfile.read(audio_file)
        # only take first audio channel and write to a new WAV file
        if len(samples.shape) > 1:
            # samples = samples[:,0]
            samples = samples.sum(axis=1)  # we may do something more advanced in the future
            # samples = samples / np.max(np.abs(samples)) #normalize audio data [-1, 1]
            merged_wavfile = (
                os.path.dirname(os.path.abspath(audio_file))
                + "/merged_"
                + os.path.basename(audio_file)
            )
            wavfile.write(merged_wavfile, sample_rate, samples)
        return AudioSignal(samples, sample_rate)


def test_realtime_notes(data: AudioSignal):
    """Returns straight notes quickly just to test functionality"""
    if not isinstance(data, AudioSignal):
        raise TypeError("Argument must be of the AudioSignal type")
    # do spectrogram
    window_length = 5000
    padding_factor = 2
    frequencies, times, spectrogram = do_spectrogram(
        data.samples, data.sample_rate, window_length, padding_factor, "end"
    )
    test_notes = list()
    for time in times:
        test_notes.append((time, "C3"))
    return test_notes


def get_notes(data: AudioSignal, print_metrics=True, volmem=None):
    # twinkle: volume_threshold = 0.1, magn_threshold = 0.7, harmonic_threshold = 0.01
    # bach_midi: volume_threshold = 0.01, magn_threshold = 0.1, bass boosting ON, harmonic_cut_amount = 0.7, harmonic_threshold = 0.01, harmonic_orders = [2]
    # bach_rousseau: volume_threshold = 0.000001, magn_threshold = 0.3, bass boosting ON, harmonic_cut_amount = 0.5, harmonic_threshold = 0.01, harmonic_orders = [2]
    # carillon_hedwig:
    """Returns a list of pairs (times, note detected) in an AudioSignal, along with a graph threshold for plotting"""
    if not isinstance(data, AudioSignal):
        raise TypeError("Argument must be of the AudioSignal type")
    if volmem and not isinstance(float(volmem), float):
        raise TypeError("Argument must be number like")
    # do spectrogram
    window_length = 5000
    padding_factor = 2
    frequencies, times, spectrogram = do_spectrogram(
        data.samples, data.sample_rate, window_length, padding_factor, "end"
    )
    if print_metrics:
        compute_metrics(spectrogram, data.sample_rate, window_length, padding_factor)
    # measure volume over time
    volume, loudest_window_energy = get_volume_array(spectrogram)
    if volmem:
        if 1024 * loudest_window_energy < volmem:
            return None, None, loudest_window_energy
    # normalize individual columns
    volume_threshold = 0.0000000000001
    col_norm_spectrogram = do_col_normalization(spectrogram, volume, volume_threshold)
    # boost magnitude of low-frequency notes
    bass_boosted_spectrogram = do_bass_boost(col_norm_spectrogram, frequencies, 350, 3)
    bass_boosted_spectrogram = do_col_normalization(
        bass_boosted_spectrogram, volume, volume_threshold
    )
    # 'cut' notes which are loud enough and have a signficant note 1 octave below
    # harmonic_threshold: how loud does note and octave need to be before being cut
    # harmonic_cut_amount: decimal representing amount of harmonic note that is removed
    # harmonic_orders: list of harmonic orders that should be cut ("1" = original note)
    harmonic_cut_amount = 1
    harmonic_threshold = 0.01
    harmonic_orders = [2, 3, 4, 5]
    harmonic_corrected_spectrogram = do_harmonic_correction(
        bass_boosted_spectrogram, harmonic_threshold, harmonic_cut_amount, harmonic_orders,
    )
    # do thresholding and note detection
    magn_threshold = 0.1
    thresh_spectrogram, detected_notes = do_thresholding(
        harmonic_corrected_spectrogram, times, frequencies, note_frequencies, magn_threshold,
    )
    return times, frequencies, detected_notes, thresh_spectrogram, loudest_window_energy
