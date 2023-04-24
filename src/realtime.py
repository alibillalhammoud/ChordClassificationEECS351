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
	# noise filter class is nested within ProcessingCallback
	class NoiseFilter:
		dynamic_memory_length = 3# how many time collection buffers to remeber in dynamic mode
		
		def __init__(self, mode: str):
			if not isinstance(mode,str): raise TypeError("NoiseFilter mode must be specified as a string")
			if mode not in ['dynamic', 'linear','attenuated']: raise NotImplementedError("NoiseFilter only support dynamic or linear modes")
			self.__memory_type = mode
			self.__current_volume_benchmark = []
		
		def update_volume_benchmark(self, most_recent_volume: float):
			if not isinstance(float(most_recent_volume), float): raise TypeError("most_recent_volume must be number like")
			if not self.__current_volume_benchmark: self.__current_volume_benchmark.append(most_recent_volume)
			elif self.__memory_type == 'dynamic':
				self.__current_volume_benchmark.append(most_recent_volume)
				if len(self.__current_volume_benchmark) > ProcessingCallback.NoiseFilter.dynamic_memory_length:
					self.__current_volume_benchmark.pop(0)
			elif self.__memory_type == 'linear' and self.__current_volume_benchmark[0] < most_recent_volume:
				self.__current_volume_benchmark[0] = most_recent_volume
			elif self.__memory_type == 'attenuated':
				if self.__current_volume_benchmark[0] < most_recent_volume:
					self.__current_volume_benchmark[0] = most_recent_volume
				else:
					self.__current_volume_benchmark[0] *= 0.5
		
		def get_volume_benchmark(self):
			if self.__current_volume_benchmark:
				if self.__memory_type == 'dynamic':
					return max(self.__current_volume_benchmark)
				elif self.__memory_type == 'linear' or self.__memory_type == 'attenuated':
					return self.__current_volume_benchmark[0]
			else:
				return 0.0
	
	
	def __init__(self, device_sample_rate, record=False, memtype='dynamic'):
		if not isinstance(record, bool): raise TypeError("bad arg ProcessingCallback constructor, record must be bool")
		if not isinstance(int(device_sample_rate), int): raise TypeError("bad arg ProcessingCallback constructor, sample rate must be number")
		self.__entirerecording = list() if record else None
		self.__tstart = None # allows setting start based on first buffer time
		self.__srate = device_sample_rate
		self.noisefilter = ProcessingCallback.NoiseFilter(memtype)
	
	def __call__(self, input_data, frame_count, time_info, status):
		"""Includes get_notes function and custom printing. Processes audio data while pyaudio collects from the buffer."""
		if self.__tstart is None: self.__tstart = time.time() - self.__srate*frame_count # estimate time instead of use pyaudio time
		if status: return (input_data, pyaudio.paAbort)
		npinput_data = np.frombuffer(input_data, dtype=np.int16)
		if self.__entirerecording is not None: self.__entirerecording.append(npinput_data)
		try:
			detected_notes, thresh_spectrogram, max_window_energy = get_notes(AudioSignal(npinput_data,self.__srate),print_metrics=False,volmem=self.noisefilter.get_volume_benchmark())
			self.noisefilter.update_volume_benchmark(max_window_energy)
			if detected_notes is None: return (input_data, pyaudio.paContinue)
			#detected_notes = test_realtime_notes(AudioSignal(npinput_data,self.__srate))
			#print_detected_notes(detected_notes, toffset=time.time()-self.__tstart)
			print_chord(detected_notes, toffset=time.time()-self.__srate*frame_count-self.__tstart)
			# Return the audio data and continue streaming
			return (input_data, pyaudio.paContinue)
		# catch overflow
		except IOError:
			return (input_data, pyaudio.paAbort)


def listenANDprocess(deviceInfo: AudioDeviceInfo, buffersize: float, listentime: float, noisefilter: str, record=False):
	if not isinstance(deviceInfo, AudioDeviceInfo): raise TypeError("bad arg deviceInfo listenANDprocess func")
	if not isinstance(float(buffersize), float): raise TypeError("bad arg buffersize listenANDprocess func")
	if not isinstance(float(listentime), float): raise TypeError("bad arg listentime listenANDprocess func")
	if not isinstance(record, bool): raise TypeError("bad arg record listenANDprocess func")
	if not isinstance(noisefilter,str): raise TypeError("bad arg noisefilter mode must be specified as a string listenANDprocess func")
	# create audio stream
	micinst = pyaudio.PyAudio()
	buffersamps = int(buffersize * deviceInfo.device_sample_rate)
	# create the callback functor
	callback = ProcessingCallback(deviceInfo.device_sample_rate, record, noisefilter)
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


