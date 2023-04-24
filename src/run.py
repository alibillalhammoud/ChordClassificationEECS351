import argparse

from spectrogram import *
from realtime import *

# parse input
parser = argparse.ArgumentParser(description='Perform note detection on input src file')
subparsers = parser.add_subparsers(required=True, help='Choose to input data in real time from the mic OR from a WAV file', dest='inputmode')

parser_realtime = subparsers.add_parser('mic', help='sets the input method to real time input from the microphone')
parser_realtime.add_argument('-b','--buffer', type=float, default=2, help='set the audio buffer length in seconds', required=False)
parser_realtime.add_argument('-t','--time', type=float, default=0, help='set how long in seconds you want the program to run. 0 results in looping forever until ctrl-c is pressed', required=False)
parser_realtime.add_argument('-w','--writewav', action='store_true', default=False, help='writes all input data collected from the mic to a wav file.')
parser_realtime.add_argument('-n','--noisefilter',choices=['dynamic', 'linear','attenuated','none'],help='Choose the noise filter mode. Dynamic mode readjusts the noise threshold in real time if the audio gets louder or quieter. Linear mode will place a linear place a linear threshold for noise based on the loudest audio from the entire session', default='dynamic')

parser_file = subparsers.add_parser('file', help='sets the input method to a wav file')
parser_file.add_argument('-s','--src', type=argparse.FileType('r'), help='src file (wav format)', required=True)

args = parser.parse_args()




if args.inputmode == 'file':
	data = AudioSignal.fromWAV(args.src.name)
	print("Num Samples:", data.num_samples)
	print("Sample Rate:", data.sample_rate)
	detected_notes, thresh_spectrogram = get_notes(data)[0:1]
elif args.inputmode == 'mic':
	deviceInfo = AudioDeviceInfo()
	listenANDprocess(deviceInfo,args.buffer,args.time,args.noisefilter,args.writewav)

#print_detected_notes(detected_notes)

## listen for exit signal and exit gracefully
#def exit_handler(sig, frame):
#    print('\n\nExit keys pressed, ending program execution now.\n\n')
#    sys.exit(0)
#signal.signal(signal.SIGINT, exit_handler)

