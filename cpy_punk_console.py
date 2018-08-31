##############################################################################
#                    Atari Punk Console in CircuitPython                     #
#               By Tammy Cravit, <tammymakesthings@gmail.com>                #
##############################################################################
# The sound generation code is based on the Arduino Punk Console by beavis   #
# audio research (https://bit.ly/2omfoJH). As written, this code should run  #
# without modification on an Adafruit Circuit Playground Express with the    #
# following additional components:                                           #
#                                                                            #
# A1 - 50K potentiometer - frequency                                         #
# A2 - 50K potentiometer - pulse width                                       #
# A3 - 50K potentiometer - tempo                                             #
# A6 - 50K potentiometer - volume                                            #
#                                                                            #
# We skip pins A4 and A5 in this version so we can use them for an I2C LCD   #
# display later.                                                             #
##############################################################################

import board
import time
import neopixel
import digitalio
import analogio
import array
import math
import audioio

class CPPunkConsole:
    # Set up the hardware and get everything ready
    def __init__(self):
        # Set up hardware linkages
        self.pixels = neopixel.NeoPixel(board.D8, 8)
        self.speaker_output  = analogio.AudioOut(board.A0)
        self.frequency_input = analogio.AnalogIn(board.A1)
        self.pulse_width_input = analogio.AnalogIn(board.A2)
        self.pixelStatus(255, 0, 255)
        self.speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
        self.speaker_enable.direction = digitalio.Direction.OUTPUT
        self.speaker_enable.value = True

    # Display a graduated color on the NeoPixels - used as a status indicator
    def pixelStatus(red=255, green=255, blue=255, delay_ms=1000):
        for i in range(8):
            self.pixels[i] = (((red/25) * i), ((green/25) * i), ((blue / 25) * i))
        self.pixels.show()
        sleep(delay_ms/1000)
        for i in range(8):
            self.pixels[i] =(0, 0, 0)
        self.pixels.show()

    # Read the analog inputs
    def readAnalogInputs():
        # Scale frequency from 50-650 Hz
        frequency = (self.frequency_input.value / 109) + 50
        # Scale duration from 50-150 ms
        pulse_width = (self.duration_input.value / 6553) + 50

        return(frequency, pulse_width)

    def playSound(sample_size=8000):
        (frequency, pulse_width) = readAnalogInputs()
        length = sample_size // frequency
        waveform = array.array("H", [0] * length)
        for t in range(length):
            v = (1.3 * math.sin(math.pi/length)*t)
            v = v + ((1.1 * math.sin(math.pi/length)*(t*3)))
            v = v + ((1.4 * math.sin(math.pi/length)*(t*5)))
            waveform[t] = int(v)

        # Play that wave, baby!
        self.speaker_enable.value = True
        wave_sample = audioio.RawSample(waveform)

        audio.play(wave_sample, loop=True)  # keep playing the sample over and over
        time.sleep(pulse_width/1000)  # until...
        audio.stop()  # we tell the board to stop

