#Phyro, by Philip Franchi-Pereira. Embrace Eternity

from ctypes import *
import sys, time, random
#import serial

#Constants
PACKET_LENGTH = 9
SOFT_RESET=33
GET_ALL=65 
GET_ALL_BINARY=66  
GET_LIGHT_LEFT=67  
GET_LIGHT_CENTER=68  
GET_LIGHT_RIGHT=69  
GET_LIGHT_ALL=70  
GET_IR_LEFT=71  
GET_IR_RIGHT=72  
GET_IR_ALL=73  
GET_LINE_LEFT=74  
GET_LINE_RIGHT=75  
GET_LINE_ALL=76  
GET_STATE=77  
GET_NAME1=78
GET_NAME2=64
GET_STALL=79  
GET_INFO=80  
GET_DATA=81  

GET_PASS1=50
GET_PASS2=51

GET_RLE=82  # a segmented and run-length encoded image
GET_IMAGE=83  # the entire 256 x 192 image in YUYV format
GET_WINDOW=84  # the windowed image (followed by which window)
GET_DONGLE_L_IR=85  # number of returned pulses when left emitter is turned on
GET_DONGLE_C_IR=86  # number of returned pulses when center emitter is turned on
GET_DONGLE_R_IR=87  # number of returned pulses when right emitter is turned on
GET_WINDOW_LIGHT=88# average intensity in the user defined region
GET_BATTERY=89  # battery voltage
GET_SERIAL_MEM=90  # with the address returns the value in serial memory
GET_SCRIB_PROGRAM=91  # with offset, returns the scribbler program buffer
GET_CAM_PARAM=92 # with address, returns the camera parameter at that address

GET_BLOB=95

SET_PASS1=55
SET_PASS2=56
SET_SINGLE_DATA=96
SET_DATA=97
SET_ECHO_MODE=98
SET_LED_LEFT_ON=99 
SET_LED_LEFT_OFF=100
SET_LED_CENTER_ON=101
SET_LED_CENTER_OFF=102
SET_LED_RIGHT_ON=103
SET_LED_RIGHT_OFF=104
SET_LED_ALL_ON=105
SET_LED_ALL_OFF=106
SET_LED_ALL=107 
SET_MOTORS_OFF=108
SET_MOTORS=109 
SET_NAME1=110 
SET_NAME2=119   # set name2 byte
SET_LOUD=111
SET_QUIET=112
SET_SPEAKER=113
SET_SPEAKER_2=114

SET_DONGLE_LED_ON=116   # turn binary dongle led on
SET_DONGLE_LED_OFF=117  # turn binary dongle led off
SET_RLE=118 # set rle parameters 
SET_DONGLE_IR=120   # set dongle IR power
SET_SERIAL_MEM=121  # set serial memory byte
SET_SCRIB_PROGRAM=122   # set scribbler program memory byte
SET_START_PROGRAM=123   # initiate scribbler programming process
SET_RESET_SCRIBBLER=124 # hard reset scribbler
SET_SERIAL_ERASE=125# erase serial memory
SET_DIMMER_LED=126  # set dimmer led
SET_WINDOW=127  # set user defined window
SET_FORWARDNESS=128 # set direction of scribbler
SET_WHITE_BALANCE=129   # turn on white balance on camera 
SET_NO_WHITE_BALANCE=130 # diable white balance on camera (default)
SET_CAM_PARAM=131   # with address and value, sets the camera parameter at that address

GET_JPEG_GRAY_HEADER=135
GET_JPEG_GRAY_SCAN=136
GET_JPEG_COLOR_HEADER=137
GET_JPEG_COLOR_SCAN=138

SET_PASS_N_BYTES=139
GET_PASS_N_BYTES=140
GET_PASS_BYTES_UNTIL=141

GET_VERSION=142

GET_IR_MESSAGE = 150
SEND_IR_MESSAGE = 151
SET_IR_EMITTERS = 152

SET_START_PROGRAM2=153   # initiate scribbler2 programming process
SET_RESET_SCRIBBLER2=154 # hard reset scribbler2
SET_SCRIB_BATCH=155  # upload scribbler2 firmware
GET_ROBOT_ID=156



#library_path = "/home/phil/Work/Phyro/phyroC.so"
library_path = "/root/test/phyroC.so"
debug = True

class Scribbler:
	def __init__(self):	
		self._volume = 0
		self._lastTranslate = 0
		self._lastRotate = 0
		self._lastSensors = []
class Writer:
	'''
	The writer function will handle the nitty gritty details about where phyro is being called from. 
	Any Phyro function can just pass its arguments to this instead of doing a bunch of if statements
	'''

	def __init__(self,serial_port="0000"):
		#Were is the writer?
		
		self.serialPort = serial_port
		
		if(serial_port != "Blue"):
			#Looks like we're on the fluke
			self.onboard = True
			self.serialLib = self.initSerialC()
			self.flukeLib = self.initFlukeC()
			DEBUG("Conencted")
		else:

			try:
				#self.ser = serial.Serial(serial_port,115200)
				self.onboard = False	
			except:
				DEBUG(sys.exc_info()[0])
				sys.exit(1)
		DEBUG("Initialized onboard?: " + str(self.onboard))

	def initSerialC(self):
		serialLib = None
		try:
			serialLib = cdll.LoadLibrary(library_path)
			self.fd = serialLib.init()
			DEBUG("This is our fd: " + str(self.fd))
		except:
			DEBUG(sys.exc_info()[0])
			sys.exit(1)
					
		return serialLib

	def initFlukeC(self):
		flukeLib = None
		try:
			flukeLib = cdll.LoadLibrary(library_path)
			DEBUG("Fluke functions now online: " )
		except:
			DEBUG(sys.exc_info()[0])
			sys.exit(1)
					
		return flukeLib	

	def write(self,toWrite,nbytes = None):
		'''
		Parameters of the function will be sent to either one of the two 
		'''

		ret = -1
		comByte = toWrite[0]

		if (type(toWrite) == int):
			toWrite = [toWrite]

		DEBUG("		Write called with com " + str(comByte) + " and args: " + str(toWrite[1:]) )
		DEBUG("		write to scrib")
		ret = self.scribWrite(toWrite,None)

		return ret


	def scribWrite(self,com, nbytes=9):

		DEBUG("		Scrib Write called with arg com: " + str(com[0]) + " and bytes: "+ str(com[1:]))
		toWrite = ""
		for c in com:
			toWrite += chr(c)
		if(len(com) < 9):
			for i in range(9-len(com)):
				toWrite += chr(ord('0'))
		if(nbytes == None):
			nbytes = 9
			n = c_int(int(nbytes))
			writeRes = self.serialLib.write_to_port(toWrite,n,self.fd)

		return writeRes

	def read(self, nbytes = 9):
		DEBUG("Called read for this many bytes: " + str(nbytes))
		ret = self.scribRead(nbytes)
		DEBUG("Read these values: " + str(ret))
		return ret

	def scribRead(self, nbytes = 9):
		read_port = self.serialLib.read_port
		read_port.argtypes = [c_char_p,c_int,c_int]
		read_port.restpye = c_int
		
		buf = create_string_buffer(nbytes)
		ret = []
		readRet  = read_port(buf,c_int(nbytes),c_int(self.fd))
		for c in buf.raw:
			ret.append(ord(c))
		return ret 
	
	#
	#Fluke Functions!!
	#

	def setLEDFront(self,value):
		value = int(min(max(value, 0), 1))
		if(isTrue(value)):
			self.serialLib.fluke_set_led_on()
		else:
			self.serialLib.fluke_set_led_off()
	def setLEDBack(self, value):
		if value > 1:
			value = 1
		elif value <= 0:
			value = 0
		else:
			value = int(float(value) * (255 - 170) + 170) # scale
		self.serialLib.fluke_set_bright_led(c_char_p(str(value)))

	def getObstacle(self,value = None):
		buf = create_string_buffer(2)
		if value == None:
			return	get("obstacle")			
		if value in ["left", 0]:
			self.serialLib.fluke_get_ir_left(buf)
		elif value in ["middle", "center", 1]:
			self.serialLib.fluke_get_ir_center(buf)	
		elif value in ["right", 2]:
			self.serialLib.fluke_get_ir_right(buf)
		hbyte = ord(buf[0])
		lbyte = ord(buf[1])
		lbyte = (hbyte << 8) | lbyte
		return int(lbyte)

	def fluke_get_battery(self):
		return int(self.serialLib.fluke_get_battery())/ 20.9813

	def setWhiteBalance(self,pos):		
		if(isTrue(pos)):
			self.serialLib.fluke_white_balance_on()
		else:
			self.serialLib.fluke_white_balance_off()


def init(serial_port):

	global writer
	global scrib

	writer = Writer(serial_port)
	scrib = Scribbler()
	playIntroSongForMePls()

def playIntroSongForMePls():
	beep(.75,500)
	beep(.01,1)
	beep(.75,500)
	beep(.01,1)
	beep(.75,500)

	beep(.75,600)
	beep(.375,550)
	beep(.375,550)
	beep(.375,500)
	beep(.375,500)
	beep(.375,475)
	beep(1,500)
	flushBuffer()

def motors(leftValue, rightValue):
	"""
	Move function that takes desired motor values
	and converts to trans and rotate.
	"""
	trans = (rightValue + leftValue) / 2.0
	rotate = (rightValue - leftValue) / 2.0
	move(trans, rotate)
	#Returns None
def move(trans, rotate):
	DEBUG("		Move called with parameters " + str(trans) + " , " + str(rotate))
	scrib._lastTranslate = trans
	scrib._lastRotate = rotate
	adjustSpeed()
	#returns none

def stop():
	scrib._lastTranslate = 0
	scrib._lastRotate = 0
	writer.write([SET_MOTORS_OFF],PACKET_LENGTH)
	writer.read(PACKET_LENGTH)
def hardStop():
	scrib._lastTranslate = 0
	scrib._lastRotate = 0
	writer.write([SET_MOTORS_OFF])
	writer.read(PACKET_LENGTH)
	#return none
		#scrib._read(Scribbler.PACKET_LENGTH) # read echo
		#scrib._lastSensors = self._read(11) # single bit sensors


def translate(amount):
	scrib._lastTranslate = amount
	adjustSpeed()

def rotate(amount):
	scrib._lastRotate = amount
	adjustSpeed()

def adjustSpeed():
	left  = min(max(scrib._lastTranslate - scrib._lastRotate, -1), 1)
	right  = min(max(scrib._lastTranslate + scrib._lastRotate, -1), 1)
	leftPower = (left + 1.0) * 100.0
	rightPower = (right + 1.0) * 100.0

	DEBUG("		Adjust Speed called with values "+ str(left) + " , " + str(right))
	writer.write([SET_MOTORS, int(rightPower), int(leftPower)])
	writer.read(PACKET_LENGTH + 11)

def turnRight(speed, timeout = None):
	ret = move(0,-speed)
	if(timeout != None):
		time.sleep(timeout)

def turnLeft(spee, timeout = None):
	ret = move(0, speed)
	if(timeout != None):
		time.sleep(timeout)

def beep(duration, frequency1, frequency2=None):
	if type(duration) in [tuple, list]:
		frequency2 = frequency1
		frequency1 = duration
		duration =.5
	
	if(duration != None and frequency1 == None):
		frequency1 = duration
		duration = .5

	if frequency1 == None:
		frequency1 = random.randrange(200, 10000)
	if type(frequency1) in [tuple, list]:
		if frequency2 == None:
			frequency2 = [None for i in range(len(frequency1))]
		for (f1, f2) in zip(frequency1, frequency2):
			ret = writeBeep(duration, f1, f2)
	else:
		ret = writeBeep(duration, frequency1, frequency2)
	wait(duration)
	return ret
def writeBeep(dur, _freq1, _freq2):
	duration = int(dur*1000)
	freq1 = int(_freq1)
	if(_freq2 != None):
		freq2 = int(_freq2)
	if(_freq2 == None):
		wRet =	writer.write([SET_SPEAKER,duration >> 8,duration % 256,freq1 >> 8,freq1 % 256])
		writer.read(PACKET_LENGTH+11)
	else:
		wRet =	writer.write([SET_SPEAKER_2,duration >> 8,duration % 256,freq1 >> 8,freq1 % 256,freq2 >> 8,freq2 % 256])
		writer.read(PACKET_LENGTH + 11)
	return wRet

def get(sensor = "all", *position):
	sensor = sensor.lower()
	if(sensor == "config"):
		return {"ir": 2, "line": 2, "stall": 1, "light": 3,"battery": 1, "obstacle": 3, "bright": 3}
	elif(sensor ==  "stall"):
		ret = _getAll()
		scrib._lastSensors = ret[10:]
		return ret[10]
	elif(sensor == "name"):
		n1 = _get(GET_NAME1,8)
		n2 = _get(GET_NAME2,8)
		c = n1 + n2
		c = string.join([chr(x) for x in c if "0" <= chr(x) <= "z"], '').strip()
		return c
	elif(sensor == "password"):
		c = _get(GET_PASS1, 8)
		c += _get(GET_PASS2, 8)
		c = string.join([chr(x) for x in c if "0" <= chr(x) <= "z"], '').strip()
		return c
	elif(sensor == "volume"):
		return scrib.volume

	elif(sensor == "battery"):
		#returns a float
		return getBattery()

	elif(sensor == "blob"):
		#returns a 3 tuple 
		return "blob"
	else:
		if(len(position)==0):
			if(sensor == "light"):
				#returns a 3 tuple
				return (getBright("left"), getBright("middle"), getBright("right"))
			elif(sensor == "line"):
				#returns a 2 tuple
				return _get(GET_LINE_ALL, 2)
			elif(sensor == "ir"):
				#returns 2 tuple
				return _get(GET_IR,2)
			elif(sensor == "obstacle"):
				#returns a 3 tupple
				return [getObstacle("left"), getObstacle("center"), getObstacle("right")]
			elif(sensor == "bright"):
				#returns a three tuple 
				return [getBright("left"), getBright("middle"), getBright("right")]
			elif sensor == "all":
				retval = getAll() # returned as bytes
				scrib._lastSensors = retval # single bit sensors
				return {"light": [retval[2] << 8 | retval[3], retval[4] << 8 | retval[5], retval[6] << 8 | retval[7]],
				"ir": [retval[0], retval[1]], "line": [retval[8], retval[9]], "stall": retval[10],
				"obstacle": [getObstacle("left"), getObstacle("center"), getObstacle("right")],
				"bright": [getBright("left"), getBright("middle"), getBright("right")],
				"blob": getBlob(),"battery": getBattery(),}
			else:
				raise ("invalid sensor name: '%s'" % sensor)


def getAll():
	writer.write([GET_ALL])
	return writer.read(PACKET_LENGTH + 11)

def getBattery():
	return writer.fluke_get_battery()

def identifyRobot():
	writer.write([GET_ROBOT_ID])
	ret = writer.read(PACKET_LENGTH + 11)
	return ret

def getIR():
	writer.write([GET_IR_ALL])
	ret = writer.read(PACKET_LENGTH+2)
	return [ret[9],ret[10]]

def getObstacle(value=None):
	return writer.getObstacle(value)

def getBlob(*args):
	return 0

def getBright(window = None):
	if(window == None or window == "all"):
		return get("bright")
	if(type(window) == str):
		if(window in "left"):
			window = 0
		elif(window in ["middle","center"]):
			window = 1
		elif(window in "right"):
			window = 2
	writer.write([GET_WINDOW_LIGHT,2])
	writer.read(PACKET_LENGTH)
	hbyte = (writer.read(1)[0])
	mbyte = (writer.read(1)[0])
	lbyte = (writer.read(1)[0])
	lbyte = (hbyte << 16)| (mbyte << 8) | lbyte
	return lbyte

def set(item, position, value = None):
	item = item.lower()
	if item == "led":
		if type(position) in [int, float]:
			if position == 0:
				if isTrue(value):
					return _set(SET_LED_LEFT_ON)
				else:				 
					return _set(SET_LED_LEFT_OFF)
			elif position == 1:
				if isTrue(value):
					return _set(SET_LED_CENTER_ON)
				else:
					return _set(SET_LED_CENTER_OFF)	
			elif position == 2:
				if isTrue(value):
					return _set(SET_LED_RIGHT_ON)
				else:
					return _set(SET_LED_RIGHT_OFF)
			else:
				raise AttributeError("no such LED: '%s'" % position)
		else:
			position = position.lower()
			if position == "center":
				if isTrue(value):
					return _set(SET_LED_CENTER_ON)
				else:
					return _set(SET_LED_CENTER_OFF)
			elif position == "left":
				if isTrue(value):
					return _set(SET_LED_LEFT_ON)
				else:
					return _set(SET_LED_LEFT_OFF)
			elif position == "right":
				if isTrue(value):
					return _set(SET_LED_RIGHT_ON)
				else:
					return _set(SET_LED_RIGHT_OFF)
			elif position == "front":
				return setLEDFront(value)
			elif position == "back":
				return setLEDBack(value)
			elif position == "all":
				if isTrue(value):
					return _set(SET_LED_ALL_ON)
				else:
					return _set(SET_LED_ALL_OFF)
			else:
				raise AttributeError("no such LED: '%s'" % position)
	elif item == "whitebalance":
		setWhiteBalance(position)
	elif item == "irpower":
		setIRPower(position)
	elif item == "volume":
		if isTrue(position):
			scrib._volume = 1
			return _set(SET_LOUD)
		else:
			scrib._volume = 0
			return _set(SET_QUIET)
	elif item == "data":
		return setData(position, value)
		#Not implimented
	elif item == "password":
		return setPassword(position)
	elif item == "forwardness":
		return setForwardness(position)
	else:
		raise ("invalid set item name: '%s'" % item)


def setLEDFront(value):
	writer.setLEDFront(value)

def setLEDBack(value):
	writer.setLEDBack(value)

def setWhiteBalance(pos):
	writer.setWhiteBalance(pos)

def setIRPower(pos):
	DEBUG(str(pos))
def setEchoMode(pos):
	DEBUG(str(pos))
def setPassword(pos):
	DEBUG(str(pos))
def setForwardness(pos):
	DEBUG("NOT YET IMPLIMENTED")

#Python only functions
#------------------------------

def wait(secs):
	return time.sleep(secs)

def currentTime():
	return time.time()

def pickOne(*args):
		"""
		Randomly pick one of a list, or one between [0, arg).
		"""
		if len(args) == 1:
			return random.randrange(args[0])
		else:
			return args[random.randrange(len(args))]

def pickOneInRange(start, stop):
		"""
		Randomly pick one of a list, or one between [0, arg).
		"""
		return random.randrange(start, stop)

def heads(): return flipCoin() == "heads"
def tails(): return flipCoin() == "tails"

def flipCoin():
		"""
		Randomly returns "heads" or "tails".
		"""
		return ("heads", "tails")[random.randrange(2)]

def randomNumber():
		"""
		Returns a number between 0 (inclusive) and 1 (exclusive).
		"""
		return random.random()
#------------------------------
#Utility Functions
#------------------------------
def flushBuffer():
	writer.read(20)

def read_2byte():
	hbyte = writer.read(1)[0]
	lbyte = writer.read(1)[0]
	lbyte = (hbyte << 8) | lbyte
	return lbyte

def _get(value, bytes = 1, mode = "byte"):
	writer.write([value])
	writer.read(PACKET_LENGTH) # read the echo
	if mode == "byte":
		retval = writer.read(bytes)
	elif mode == "word":
		retvalBytes = writer.read(bytes)
		retval = []
		for p in range(0,len(retvalBytes),2):
			retval.append(retvalBytes[p] << 8 | retvalBytes[p + 1])
	elif mode == "line": # until hit \n newline
		retval = "NOT HERE YET"
		DEBUG("_get(line)")
	
		return retval

def _set(values):
	writer.write([values],len([values]))
	test = writer.read(PACKET_LENGTH + 11) # read echo
	_lastSensors = test[9:] # single bit sensors

def isTrue(value):
	"""
	Returns True if value is something we consider to be "on".
	Otherwise, return False.
	"""
	if type(value) == str:
		return (value.lower() == "on")
	elif value: return True
	return False

def DEBUG(s):
	if(debug):
		print(s)

