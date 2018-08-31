import board
import time
from digitalio import DigitalInOut, Direction
import neopixel

######################################################################
#  CONFIGURATION - EDIT THESE AS APPROPRIATE TO CHANGE THE BEHAVIOR  # 
######################################################################

# What message(s) should we send?
messages = []
messages.append("My cuddle dungeon is the best cuddle dungeon!")
messages.append("And then suddenly, Pip!")
messages.append("I volunteer as tribute!")
messages.append("No, that's definitely not an alpaca in my bag.")
messages.append("I am worthy of love and belonging.")
messages.append("Feed and water your meatsuits!")
messages.append("Spoiler alert: Your brain weasels are definitely lying.")

# How fast should we send it (words per minute)?
morse_wpm = 20

######################################################################
#              No user-servicable parts below this line              #
######################################################################

# Morse code alphabet
CODE = {'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
        'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.',  

        '&': '.-...',  ':': '---...', ',': '--..--',
        '!': '-.-.--', '=': '-...-',  '.': '.-.-.-',
        '-': '-....-', '+': '.-.-.',  '?': '..--.-',
        '/': '-..-.',  '\'': '.----.', ':': '---...',
        }

dot_length = 1000 / (morse_wpm)   # In milliseconds
dash_length = dot_length * 3
char_space_length = dot_length
word_space_length = dot_length * 5

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)

whichMessage = 0

print("**********************************************************************")
print("* Transmitting", len(messages), "messages at", morse_wpm, "wpm")
print("**********************************************************************")
print("")

time.sleep(1)

while True:
    pixel[0] = (0, 0, 0)
    pixel.show()

    message = messages[whichMessage]
    print("Transmitting message", (whichMessage + 1), ":", message)
    
    for c in message.upper():
        if c == ' ':
            time.sleep(word_space_length/1000)
        else:
            if c in CODE:
                for mc in CODE[c]:
                    if mc == '.':
                        led.value = True
                        time.sleep(dot_length/1000)
                    elif mc == '-':
                        led.value = True
                        time.sleep(dash_length/1000)
                    # Send an inter-character break
                    led.value = False
                    time.sleep(char_space_length/1000)
            else:
                print("Note: Undefined morse character", "'" + c + "'", "skipped")
    
    # Send inter-message break
    print("End of message")
    led.value = False
    time.sleep(2)
    
    # Select the next message
    whichMessage = whichMessage + 1
    if whichMessage > (len(messages) - 1):
        whichMessage = 0
        time.sleep(2)
