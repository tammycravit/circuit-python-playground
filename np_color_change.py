# For Metro Express M0:
#   ------      -----------                     ---------------------
#   Pin(s)      Description                     Python board constant
#   ------      -----------                     ---------------------
#   #0/RX       GPIO #0, serial recieve         D0
#   #1/TX       GPIO #1, serial transmit        D1
#   #2 - #12    GPIO (3-6 and 8-12 can PWM)     D2 - D12
#   #13         GPIO #13, onboard red LED       D13
#   SDA         I2C Data                        SDA
#   SCL         I2C Clock                       SCL
#   A0          Analog in, analog out 0-3.3V    A0
#   A1-A5       Analog in, digital IO           A1 - A5
#   A6-A11      Analog in, multiplexed onto     A6 - A11
#               D0/D1/D4/D5/D8/D9
#   SCK         Hardware SPI - SCK              SCK
#   MOSI        Hardware SPI - MOSI             MOSI
#   MISO        Hardware SPI - MISO             MISO
#   NEOPIXEL    Onboard neopixel (pin 40)       NEOPIXEL

import board
import neopixel
import time

pixel_pin = board.NEOPIXEL
num_pixels = 1

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False)

while True:
    for pixel_red in range(255, 0, -10):
        for pixel_green in range(0, 255, 10):
            for pixel_blue in range(0, 255, 10):        
                pixels[0] = (pixel_red, pixel_green, pixel_blue)
                pixels.show()
                time.sleep(0.1)
    