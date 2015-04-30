import serial
import time
import string

#---------------#
# CODE CONSTANTS
#---------------#

NUM_TRIALS = 1 # Clearly its the number of times we're gonna run this for
tot = 0 # Keeps track of the total amount of time we've run for so far, used to calculate the average

#---------------#
# PREDEFINED SCRIBBLE COMMANDS
#---------------#

PACKET_LENGTH = 9 #Why the 9th bit? NOBODY KNOWS
SCRIBBLER_RETURN_BYTES = 240


def _write(rawdata):
	#Takes all the raw data and puts it into a chr format using the pesky "map" command 
	t = map(lambda x: chr(int(x)), rawdata)
	data = string.join(t, '') + (chr(0) * (PACKET_LENGTH - len(t)))[:9]

	#Wrapper function!
	#Make sure that we write the correct number of bytes to the fluke.
	count = 0
	i =0
	while(count<len(data)):
		count += ser.write(data.charAt(i))      # write packets
		i+=1
		
	time.sleep(0.01) # HACK! THIS SEEMS TO NEED TO BE HERE!


def _read(bytes = 1):
        c = ser.read(bytes)

        # .nah. bug fix
        while (bytes > 1 and len(c) < bytes):      
            c = c + ser.read(bytes-len(c))

        # .nah. end bug fix
        time.sleep(0.01) # HACK! THIS SEEMS TO NEED TO BE HERE!
        if bytes == 1:
            x = -1
            if (c != ""):
                x = ord(c)            
        else:
            return map(ord, c)

print("Open port")
ser = serial.Serial("/dev/tty.Fluke2-0640-Fluke2-1",57600,timeout=1)
print("Begin testing")

for i in range(NUM_TRIALS):

	pre = time.clock()
	ser.write(chr(89))
	bits = ser.inWaiting();
	print(ser.read(bits))
	pos = time.clock()

	tot+= pos-pre

print("Average time: " + str(tot/NUM_TRIALS))
print("Close")
ser.close()



