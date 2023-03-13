# credits: https://pythonbasics.org/convert-mp3-to-wav/
from os import path
from pydub import AudioSegment
import argparse

# create an ArgumentParser object
parser = argparse.ArgumentParser(description='convert mp3 to wav using ffmpeg (linux) and pydub library')
parser.add_argument('required_string', type=str, help='src file (include the .mp3 extension)')
parser.add_argument('required_string', type=str, help='output file (include the .wav extension)')

# parse the arguments from the command line
args = parser.parse_args()

# files                                                                         
src = args.src
dst = args.out

# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")
