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


# functor
class ProcessingCallback:
	def __init__(self, device_sample_rate, record=False):
		self.entirerecording = list() if record else None
		self.tstart = None # allows setting start based on first buffer time
		self.srate = device_sample_rate
	
	def __call__(self, input_data, frame_count, time_info, status):
		"""Includes get_notes function and custom printing. Processes audio data while pyaudio collects from the buffer."""
		if self.tstart is None: self.tstart = time_info["input_buffer_adc_time"]
		if status: return (input_data, pyaudio.paAbort)
		npinput_data = np.frombuffer(input_data, dtype=np.int16)
		if self.entirerecording is not None: self.entirerecording.append(npinput_data)
		try:
			detected_notes, thresh_spectrogram = get_notes(AudioSignal(npinput_data,self.srate),False)
			#detected_notes = test_realtime_notes(AudioSignal(npinput_data,self.srate))
			print_detected_notes(detected_notes, toffset=time_info["input_buffer_adc_time"]-self.tstart)
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
	# create audio stream
	micinst = pyaudio.PyAudio()
	buffersamps = int(buffersize * deviceInfo.device_sample_rate)
	# create the callback functor
	callback = ProcessingCallback(deviceInfo.device_sample_rate, record)
	# begin processing
	micstream = micinst.open(format=deviceInfo.format, channels=deviceInfo.channels, rate=deviceInfo.device_sample_rate, input=True, output=False, frames_per_buffer=buffersamps, stream_callback=callback)
	# process until interrupt or finish time as set by command line
	micstream.start_stream()
	timeout_counter_start = time.time() # seperate timeout start time avoids potential errors
	try:
		if listentime != 0:
			while (time.time()-timeout_counter_start) < listentime: pass
		else:
			while True: pass
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


