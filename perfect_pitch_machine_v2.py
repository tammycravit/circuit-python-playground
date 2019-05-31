# The Perfect Pitch Machine
# By Isaac Wellish
# <https://learn.adafruit.com/perfect-pitch-machine/>
# Creative Commons Licence (Anyone can use and hack the code, just give attributions please!)
#
# Modified by Tammy Cravit, 05/29/2019:
#   - Pitches stored in an array
#   - Slide switch toggles octave
#   - Code cleanup for more idiomatic Python
#
# Big thanks to Adafruit!
# Much of this code was adapted from Adafruit's Circuit Playground
# Sound Meter tutorial found here:
# <https://learn.adafruit.com/adafruit-circuit-playground-express/playground-sound-meter>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

##############################################################################
#import neccesarry libraries
##############################################################################

import array
import math
import time

import board
import audiobusio
from   digitalio import DigitalInOut, Direction, Pull
import digitalio
import audioio
import neopixel

##############################################################################
# Global Variables
##############################################################################

# Threshhold for loudness of sound needed to trigger current pitch
blowThresshold = 5000

# debounce time, how long the debounce time should be to prevent multiple button triggers in one press
debounceTime = 0.2

# pitch length, how many seconds we want the note to sound when triggered
pitchLength = 1

# neopixel brightness
pixelBrightness = 0.1

# the number of samples taken per second in Hertz
SAMPLERATE = 8000

# how many samples we're collecting
NUM_SAMPLES = 160

# the frequency of the note being played
FREQUENCY = 0

##############################################################################
# set up note values in Hz. Find frequency values at
# <https://pages.mtu.edu/~suits/notefreqs.html>.
#
# Unexpected results may occurif pitch_frequencies_low, pitch_frequencies_high,
# and led_color_data are not all the same length.
##############################################################################

# Ab3, A3, As3, BB3, B3, C4. C4. Db4, D4, Ds4. Eb4. E4. F4. Fs4. Gb4, G4, Gs4
pitch_frequencies_low  = [208, 223, 233, 233, 247, 262, 277, 277, 294,
                          311, 311, 330, 349, 370, 370, 392, 415]

# Ab4, A4, As4, BB4, B4, C5. C5. Db5, D5, Ds5. Eb5. E5. F5. Fs5. Gb5, G5, Gs5
pitch_frequencies_high = [415, 440, 466, 466, 494, 523, 554, 554, 587,
                          622, 622, 659, 698, 739, 739, 783, 830]

# Define constants for the LED colors we want to use
COLOR_SHARP   = (255, 0, 0)
COLOR_NATURAL = (0, 255, 0)
COLOR_FLAT    = (0, 0, 255)

# Which NeoPixel and color to light up for each note. The length of led_color_data
# should match the length of pitch_frequencies_low and pitch_frequencies_high
led_color_data = [
    {"pixel": 9, "color": COLOR_FLAT},
    {"pixel": 9, "color": COLOR_NATURAL},
    {"pixel": 9, "color": COLOR_SHARP},
    {"pixel": 0, "color": COLOR_FLAT},
    {"pixel": 0, "color": COLOR_NATURAL},
    {"pixel": 1, "color": COLOR_NATURAL},
    {"pixel": 1, "color": COLOR_SHARP},
    {"pixel": 2, "color": COLOR_FLAT},
    {"pixel": 2, "color": COLOR_NATURAL},
    {"pixel": 2, "color": COLOR_SHARP},
    {"pixel": 3, "color": COLOR_FLAT},
    {"pixel": 3, "color": COLOR_NATURAL},
    {"pixel": 4, "color": COLOR_NATURAL},
    {"pixel": 4, "color": COLOR_SHARP},
    {"pixel": 5, "color": COLOR_FLAT},
    {"pixel": 5, "color": COLOR_NATURAL},
    {"pixel": 5, "color": COLOR_SHARP},
]

# The currently selected note range
note_range = 0  # 0 = low, 1 = high

# Prepare an array to record the mic samples into
samples = array.array('H', [0] * NUM_SAMPLES)

# Create a counter for tracking button presses
# Declared outside scope of while loop so it doesn't get reset to 0 at the beginnning of every loop!
counter = 0

##############################################################################
# Set up board IO
##############################################################################

# Set up the NeoPixels (brightness can be between 0 and 1)
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness= pixelBrightness)

# Program the two buttons on the board to be able to move up and down pitches
buttonD = DigitalInOut(board.BUTTON_A) # button A is the down button
buttonD.direction = Direction.INPUT
buttonD.pull = Pull.DOWN

buttonU = DigitalInOut(board.BUTTON_B) # button B is the up button
buttonU.direction = Direction.INPUT
buttonU.pull = Pull.DOWN

# Enable the speaker for audio output
spkrenable = DigitalInOut(board.SPEAKER_ENABLE)
spkrenable.direction = Direction.OUTPUT
spkrenable.value = True

# Enable the slide switch to select which note range to use
range_switch = DigitalInOut(board.D7)
range_switch.direction = Direction.INPUT
range_switch.pull = Pull.UP

# Set up a PWM imput for sampling the microphone
mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA, sample_rate=16000, bit_depth=16)

##############################################################################
# Helper math functions for working with the microphone
##############################################################################

# Remove DC bias before computing RMS.
def normalized_rms(values):
    minbuf = int(mean(values))
    return math.sqrt(sum(float((sample - minbuf) * (sample - minbuf)) for sample in values) / len(values))

def mean(values):
    return (sum(values) / len(values))

##############################################################################
#Taking and analyzing input from the microphone (The hard part...)
#This block of code will essentially allow us to find the magnitude or loudness of the mic input (Your breath!)
##############################################################################

while True:
    if range_switch.value == True:
        note_range = 1
    else:
        note_range = 0

    #We begin regcording samples from the board's mic
    mic.record(samples, len(samples))
    magnitude = normalized_rms(samples)

    if buttonU.value == True:  # If Up button is pushed then move up a pitch
        pixels.fill((0, 0, 0)) #turn all neopixels off
        counter += 1 #increase the counter by 1
        time.sleep(debounceTime) #to ensure button isn't triggered multiple times in one press we must "debounce" the button by creating a short delay after pressing it
    elif buttonD.value == True: #Do the same for the down button
        pixels.fill((0, 0, 0)) # If Down button is pushed then move down a pitch
        counter -= 1 #decrease counter by one
        time.sleep(debounceTime) #debounce button

    if counter > (len(pitch_frequencies_low) - 1):
        counter = 0
    elif counter < 0:
        counter = (len(pitch_frequencies_low) - 1)

    if note_range == 0:
        FREQUENCY = pitch_frequencies_low[counter]
    else:
        FREQUENCY = pitch_frequencies_high[counter]

    pixels[led_color_data[counter]["pixel"]] = led_color_data[counter]["color"]

    # Any time we get a sound with a magnitude greater than the value of blowThresshold, trigger the
    # current pitch (can be changed at top where it is defined)
    if magnitude > blowThresshold:
        length = SAMPLERATE // FREQUENCY #create length of sample
        sine_wave = array.array("H", [0] * length) # create an array for a sine wave
        for i in range(length):
            sine_wave[i] = int(math.sin(math.pi * 2 * i / 18) * (2 ** 15) + 2 ** 15) # fill the array with values

        audio = audioio.AudioOut(board.SPEAKER)
        sine_wave_sample = audioio.RawSample(sine_wave)
        audio.play(sine_wave_sample, loop=True)  # Play the sample
        time.sleep(pitchLength)  # Play for length of pitchLength
        audio.stop()  # we tell the board to stop
        audio.deinit()

    pixels.show() #show the desired neopixel light up on board