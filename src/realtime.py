import pyaudio
import time
import wave
import numpy as np

from util import *
from spectrogram import *

# set global audio information / parameters and test an input stream
class AudioDeviceInfo:
	def __init__(self):
		testinst = pyaudio.PyAudio()
		device_info = testinst.get_default_output_device_info()
		device_sample_rate = int(device_info["defaultSampleRate"])
		# for now only use int16 format
		audioformat = pyaudio.paInt16
		# use only 1 channel for now
		numchannels = 1
		# test stream
		teststream = testinst.open(format=audioformat, channels=numchannels, rate=device_sample_rate, input=True, frames_per_buffer=100000)
		teststream.close()
		testinst.terminate()
		self.device_sample_rate = device_sample_rate
		self.format = audioformat
		self.channels = numchannels

entirerecording = None # global var that will contain data if not none
tstart = 0 # global var holding the start time of the processing
srate = None
def processing_callback(input_data, frame_count, time_info, status):
	"""Includes get_notes function and custom printing. Processes audio data while pyaudio collects from the buffer."""
	npinput_data = np.frombuffer(input_data, dtype=np.int16)
	if entirerecording is not None:
		entirerecording.append(npinput_data)
	try:
		detected_notes, thresh_spectrogram = get_notes(AudioSignal(npinput_data,srate),False)
		print_detected_notes(detected_notes, toffset=time.time()-tstart)
		# Return the audio data and continue streaming
		return (input_data, pyaudio.paContinue)
	# catch overflow
	except IOError:
		return (input_data, pyaudio.paAbort)


def listenANDprocess(deviceInfo: AudioDeviceInfo, buffersize: float, listentime: float, record=False):
	if not isinstance(deviceInfo, AudioDeviceInfo): raise TypeError("bad arg deviceInfo listenANDprocess func")
	if not isinstance(float(buffersize), float): raise TypeError("bad arg buffersize listenANDprocess func")
	if not isinstance(float(listentime), float): raise TypeError("bad arg listentime listenANDprocess func")
	if not isinstance(record, bool): raise TypeError("bad arg record listenANDprocess func")
	# set global vars
	global entirerecording, tstart, srate
	entirerecording = list() if record else None
	tstart = time.time()
	srate = deviceInfo.device_sample_rate
	# create audio stream and begin processing
	micinst = pyaudio.PyAudio()
	buffersamps = int(buffersize * deviceInfo.device_sample_rate)
	micstream = micinst.open(format=deviceInfo.format, channels=deviceInfo.channels, rate=deviceInfo.device_sample_rate, input=True, output=False, frames_per_buffer=buffersamps, stream_callback=processing_callback)
	# process until interrupt or finish time as set by command line
	micstream.start_stream()
	tstart = time.time()
	try:
		if listentime != 0:
			while (time.time()-tstart) < listentime:
				pass
		else:
			while True:
				pass
	except KeyboardInterrupt:
		micstream.stop_stream()
		micstream.close()
		if record:
			wavfilename = time.ctime().replace(' ','_').replace(':','_') + ".wav"
			wf = wave.open(wavfilename, 'wb')
			wf.setnchannels(deviceInfo.channels)
			wf.setsampwidth(micinst.get_sample_size(deviceInfo.format))
			wf.setframerate(deviceInfo.device_sample_rate)
			wf.writeframes(b''.join(entirerecording))
			wf.close()
		micinst.terminate()
	finally:
		micstream.stop_stream()
		micstream.close()
		micinst.terminate()


