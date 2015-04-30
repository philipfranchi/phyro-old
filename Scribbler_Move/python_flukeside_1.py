#
# Philip Franchi 
# This program makes the scribbler move in response to the light
# Version 1.0 For meeting on 4/8
#

from cytpes import *

cdll.LoadLibrary("/home/fluke2/server/fluke2cmd.so")

libc = CDLL("/home/fluke2/server/fluke2cmd.so")
libc.scribbler_passthrough()

