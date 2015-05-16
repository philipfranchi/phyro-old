import serial
import string 

PACKET_LENGTH = 9;

_lastTranslate = 0
_lastRotate = 0


#Constants, used for passasing meesages 
SET_MOTORS = 109;
SET_MOTORS_OFF = 108;
BATTERY_VOLTAGE = 89;

#A few commands already loaded 
msg_move = (SET_MOTORS,0,0,0,0)
msg_stop = [SET_MOTORS_OFF,0,0,0,0]
msg_read_bat = (BATTERY_VOLTAGE)


def translate(val):
	_lastTranslate = val
def rotate(val):
	_lastRoate = val;

def _adjustSpeed():
    left  = min(max(_lastTranslate - _lastRotate, -1), 1)
    right  = min(max(_lastTranslate + _lastRotate, -1), 1)

    leftPower = (left + 1.0) * 100.0
    rightPower = (right + 1.0) * 100.0
    #leftPower = 0
	
    _set([SET_MOTORS, rightPower, leftPower])

def moveTR(translate,rotate):
	_lastTranslate = translate;
	_lastRotate = rotate;
	_adjustSpeed();

def move(left,right):
	leftPower = (left + 1.0) * 100
	rightPower = (right + 1.0) * 100
	print( "" + str(int(rightPower)) + " : " + str(int(leftPower)) )

	_set( [SET_MOTORS, leftPower, rightPower] )

def _set(*values):

	v = values 
	t = map(lambda x: chr(int(x)), *v)
	data = string.join(t, '') + (chr(0) * (PACKET_LENGTH - len(t)))[:9]
	#Make sure to print how many bytes we sent over to the fluke
	print("Write to Fluke")
	print("Bytes written: " + str(ser.write(data)))
	

print("Open port")
ser = serial.Serial("/dev/tty.Fluke2-0640-Fluke2",115200,timeout=5)
usrin = 't'

while(usrin!='q'):
	usrin = str(raw_input("command please\n"))
	if(usrin is 'm'):

		#ser.write(chr(245))
		move(1,1)
		bytes = ser.inWaiting()
		print(bytes)
		print(str(ser.read(bytes)))
	if(usrin is 's'):
		_set(msg_stop)
	if(usrin is'l'):
		move(0,1)

print("Read Response")
print(ser.read(11))
print("Close")
ser.close()


