# DFT Music Interpreter

## Project Description

Our project attempts to detect notes and chords in audio samples by performing a spectrogram on the audio data and running a post-processing algorithm to perform frequency-domain analysis. We developed this entirely in Python using our own algorithms and open-source python signal processing APIs.

## Installation

Download the zip file and change the directory to ChordClassificationEECS351\src in the terminal

## Usage
These are the helper outputs for our program

**py run.py -h**
``` console
PS C:\Users\samsa\VSCode\351project\ChordClassificationEECS351\src> py run.py -h
usage: run.py [-h] {mic,file} ...

Perform note detection on input src file

positional arguments:
  {mic,file}  Choose to input data in real time from the mic OR from a WAV file
    mic       sets the input method to real time input from the microphone
    file      sets the input method to a wav file

options:
  -h, --help  show this help message and exit
```
**py run.py mic -h**
``` console
PS C:\Users\samsa\VSCode\351project\ChordClassificationEECS351\src> py run.py mic -h
usage: run.py mic [-h] [-b BUFFER] [-t TIME] [-w] [-n {dynamic,linear,attenuated,none}]

options:
  -h, --help            show this help message and exit
  -b BUFFER, --buffer BUFFER
                        set the audio buffer length in seconds
  -t TIME, --time TIME  set how long in seconds you want the program to run. 0 results in looping forever until ctrl-c is pressed
  -w, --writewav        writes all input data collected from the mic to a wav file.
  -n {dynamic,linear,attenuated,none}, --noisefilter {dynamic,linear,attenuated,none}
                        Choose the noise filter mode. Dynamic mode readjusts the noise threshold in real time if the audio gets louder or quieter. 
                        Linear mode will place a linear place a linear threshold for noise based on the loudest audio from the entire session
```
**py run.py file -h**
``` console
PS C:\Users\samsa\VSCode\351project\ChordClassificationEECS351\src> py run.py file -h
usage: run.py file [-h] -s SRC

options:
  -h, --help         show this help message and exit
  -s SRC, --src SRC  src file (wav format)
  ```
## Contributors
**Ali Hammoud, Thomas Kennings, Joshua Lian, Sehyun Park**

## Copyright and License

