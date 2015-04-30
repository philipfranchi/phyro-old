import serial
import string 
import time 


PACKET_LENGTH = 9
GET_NAME = 78
GET_VER = 142


toWrite = 224


def readByte(bytes):
	c = ser.read(1)
	d = ser.read(1)
	return ord(d) | (ord(d)<<8)

def readMe(bytes):
	c = ser.read(1)
	return ord(c)
print("Opening port to write char: " + str(toWrite));

ser = serial.Serial("/dev/tty.Fluke2-0640-Fluke2-1",57600)

wrote = str(ser.write(chr(toWrite)))

print("Wrote " + wrote + " bytes");

time.sleep(0.01);
#bytes = ser.inWaiting()

print("Reading")

bit = readMe(PACKET_LENGTH)

print(bit)

print("Close")

ser.close()


