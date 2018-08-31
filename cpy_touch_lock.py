##############################################################################
#                CircuitPython Touch-Sensitive Combination Lock              #
#        Tammy Cravit, <tammymakesthings@gmail.com>, v1.00, 2018-08-31       #
##############################################################################
# This code is designed for the Circuit Playground Express hardware, but all #
# of the hardware specific stuff is wrapped up in the __init__ method, so    #
# adapting this to other board configurations should be fairly               #
# straightforward.                                                           #
#                                                                            #
# Code to actually activate the servo/magnet/etc. to unlock the lock should  #
# be added to do_unlock_hardware(). Right now, this function simply prints a #
# message on the Serial console.                                             #
##############################################################################
# Copyright (c) 2018, Tammy Cravit.                                          #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the “Software”), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS    #
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,#
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE#
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER     #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
##############################################################################

import board
import touchio
import time
import neopixel

class CPYTouchLock:
    #------------------------------------------------------------------------
    # Set up the hardware and internal state.
    #
    # NOTE: No checking is done on the combination to ensure that the digits
    # it contains match the button configuration of the device.
    #------------------------------------------------------------------------
    def __init__(self, combination="1234"):
        # Set up our internal state
        self.combination = combination
        self.current_pos = 0
        self.num_pixels = 10

        # Set up the NeoPixels. We use colored blink codes to display status.
        self.pixels = neopixel.NeoPixel(board.D8, self.num_pixels)

        # Set up the capacitive touch inputs. We save the touchio objects in an
        # array to simplify scanning them.
        touch_inputs = [board.A1, board.A2, board.A3, board.A4, board.A5,
                board.A6, board.A7]
        self.inputs = [None]
        for i in touch_inputs:
            self.inputs = self.inputs + touchio.TouchIn(i)

        # Blink the neopixels to indicate that initialization is done.
        blink_status(255,0,0, num_blinks=1, blink_duration=0.25)
        blink_status(255,255,0, num_blinks=1, blink_duration=0.25)
        blink_status(0,255,0, num_blinks=1, blink_duration=0.25)
        blink_status(0,255,255, num_blinks=1, blink_duration=0.25)
        blink_status(0,0,255, num_blinks=1, blink_duration=0.25)
        blink_status(255,0,255, num_blinks=1, blink_duration=0.25)

        print("CPYTouchLock initialized with", len(touch_inputs)+1, "inputs")

    #------------------------------------------------------------------------
    # Scan the touch inputs and look for touches.
    #
    # The result is a list of all the touch inputs being touched. This version of
    # the lock treats multiple inputs as an error condition which resets the input
    # state.
    #
    # Implementing "chorded" combinations is left as an exercise to the reader. :-)
    #------------------------------------------------------------------------
    def scan_inputs():
        result_set = []
        for index, input_ob in enumerate(self.inputs):
            if input_ob is not None and input_ob.value:
                result_set = result_set + str(index)
        if len(result_set) > 0:
            print("scan_inputs(): active input set is", result_set)
        return result_set

    #------------------------------------------------------------------------
    # Blink the NeoPixels to indicate status.
    #------------------------------------------------------------------------
    def blink_status(red_val, grn_val, blu_val, num_blinks=5, blink_duration=0.25):
        for i in range(num_blinks):
            for i in range(self.num_pixels):
                self.pixels[i] = (red_val, grn_val, blu_val)
            time.sleep(blink_duration)
            for i in range(self.num_pixels):
                self.pixels[i] = (0, 0, 0)
            time.sleep(blink_duration)

    #------------------------------------------------------------------------
    # Reset the input state after a successful unlock or an incorrect digit.
    #------------------------------------------------------------------------
    def reset_input_state():
        print("reset_input_state(): resetting")
        self.current_pos = 0
        blink_status(255, 0, 0, 3)

    #------------------------------------------------------------------------
    # Activate whatever hardware is requ9ired to unlock the device.
    #------------------------------------------------------------------------
    def do_unlock_hardware():
        print("do_unlock_hardware(): no hardware configured")

    #------------------------------------------------------------------------
    # Handle a successful unlock (and then call do_unlock_hardware() to actually
    # unlock the device.
    #------------------------------------------------------------------------
    def do_unlock():
        print("do_unlock(): successful unlock")
        blink_status(0, 0, 255, num_blinks=5, blink_duration=0.3)
        self.do_unlock_hardware()
        self.current_pos = 0

    #------------------------------------------------------------------------
    # Check the result set returned from scan_inputs() and handle the digit(s)
    # pressed.
    #------------------------------------------------------------------------
    def check_and_process_input(result_set):
        print("check_and_process_input()", "result_set length=", len(result_set))
        if len(result_set) > 1:
            print("check_and_process_input()", "multiple buttons pressed; resetting input state")
            reset_input_state()
        if result_set[0] == self.combination[self.current_pos]:
            print("check_and_process_input()", "Digit", self.current_pos, "matched combination")
            current_pos = current_pos + 1
            print("check_and_process_input()", "current_pos is now", current_pos)
            blink_status(0, 255, 0, num_blinks=1)
            if current_pos > (len(combination)-1):
                do_unlock()
        else:
            print("check_and_process_input()", "")
            reset_input_state()

    #------------------------------------------------------------------------
    # App event loop.
    #------------------------------------------------------------------------
    def run():
        print("run(): starting event loop")
        while True:
            input_set = scan_inputs()
            check_and_process_input(input_set)
            time.sleep(0.01)

#============================================================================
# Kick off the app
#============================================================================
CPyTouchLock.new("3472").run()
