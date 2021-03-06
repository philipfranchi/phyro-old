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

scribblerCom = [
	GET_ALL,
	GET_ALL_BINARY,
	GET_LIGHT_LEFT,
	GET_LIGHT_CENTER,
	GET_LIGHT_RIGHT,
	GET_LIGHT_ALL,
	GET_IR_LEFT,
	GET_IR_RIGHT,
	GET_IR_ALL,
	GET_LINE_LEFT,
	GET_LINE_RIGHT,
	GET_LINE_ALL,
	GET_STATE,
	GET_NAME1,
	GET_NAME2,
	GET_STALL,
	GET_INFO,
	GET_DATA,
	GET_BATTERY,
	SET_LED_LEFT_ON,
	SET_LED_LEFT_OFF,
	SET_LED_CENTER_ON,
	SET_LED_CENTER_OFF,
	SET_LED_RIGHT_ON,
	SET_LED_RIGHT_OFF,
	SET_LED_ALL_ON,
	SET_LED_ALL_OFF,
	SET_LED_ALL,
	SET_MOTORS_OFF,
	SET_MOTORS,
	SET_NAME1, 
	SET_NAME2,   # set name2 byte
	SET_LOUD,
	SET_QUIET,
	SET_SPEAKER,
	SET_SPEAKER_2	
	]
dongleCom = []

#library_path = "/home/phil/Work/Phyro/phyroC.so"
library_path = "/root/test/phyro.so"
debug = True

class Scribbler:
	def __init__(self):	
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

		if (toWrite.type() == int):
			toWrite = [toWrite]

		DEBUG("    Write called with com " + str(comByte) + " and args: " + str(toWrite[1:]) )
		if(self.onboard == False):
			#ret = self.ser.write(comByte)
			print("COMING SOON")
		else:	
			if(comByte in scribblerCom):
				DEBUG("	write to scrib")
				ret = self.scribWrite(toWrite,None)
			elif(comByte in dongleCom):
				DEBUG("DONGLE DONGLE")
			else:
				DEBUG("NOOOO")
		return ret


	def scribWrite(self,com, nbytes=9):

                DEBUG("    Scrib Write called with arg com: " + str(com[0]) + " and bytes: "+ str(com[1:]))
                toWrite = ""
                for c in com:
                        toWrite += chr(c)

                if(len(com) < 9):
                        for i in range(9-len(com)):
                                toWrite += chr(ord('0'))
                if(nbytes == None):
                        nbytes = 9
                n = c_int(int(nbytes))
                DEBUG("    CWRITE passed: "+ str(toWrite) + "," +str(n) +"," + str(self.fd))
                writeRes = self.serialLib.write_to_port(toWrite,n,self.fd)

                return writeRes



	def readOLD(self, nbytes = 20):
		read_port = self.serialLib.read_port
		read_port.argtypes = [c_int,c_int]
		read_port.restpye = POINTER(c_char_p)
		
		res = read_port(c_int(nbytes),c_int(self.fd))
		
		for c in res:
			print c
		return res
		'''		
		DEBUG("Called Read for: " + str(nbytes))
		readRet= self.serialLib.read_port(nbytes,self.fd)
		DEBUG("Scrib Read says: " + str(readRet))
		return readRet
		'''
	def read(self, nbytes = 20):
		return self.scribRead(nbytes)

	def scribRead(self, nbytes = 20):
		read_port = self.serialLib.read_port
		read_port.argtypes = [c_char_p,c_int,c_int]
		read_port.restpye = c_int
		
		buf = create_string_buffer(nbytes)
		ret = []
		readRet  = read_port(buf,c_int(nbytes),c_int(self.fd))
		for c in buf.raw:
			ret.append(ord(c))
		DEBUG("Read these values: " + str(ret))
		return ret 
	
def init(serial_port):

	global writer
	global scrib

	writer = Writer(serial_port)
	scrib = Scribbler()

def motors(leftValue, rightValue):
	"""
	Move function that takes desired motor values
	and converts to trans and rotate.
	"""
	trans = (rightValue + leftValue) / 2.0
	rotate = (rightValue - leftValue) / 2.0
	return move(trans, rotate)
	
def move(trans, rotate):
	DEBUG("    Move called with parameters " + str(trans) + " , " + str(rotate))
	scrib._lastTranslate = trans
	scrib._lastRotate = rotate
	return adjustSpeed()
	#return writer.read(PACKET_LENGTH)

def stop():
	scrib._lastTranslate = 0
	scrib._lastRotate = 0
	return writer.write([SET_MOTORS_OFF],9)

def hardStop():
	scrib._lastTranslate = 0
	scrib._lastRotate = 0
	writer.write([SET_MOTORS_OFF])
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

	DEBUG("    Adjust Speed called with values "+ str(left) + " , " + str(right))
	ret = str(writer.write([SET_MOTORS, int(rightPower), int(leftPower)]))
	DEBUG("    Writer returned: " + ret)

	#writer.read(PACKET_LENGTH) #Catch that echo

def turnRight(speed, timeout = None):
	ret = move(0,-speed)
	if(timeout != None):
		time.sleep(timeout)
	return ret
def turnLeft(spee, timeout = None):
	ret = move(0, speed)
	if(timeout != None):
		time.sleep(timeout)
	return ret

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
        	return writeBeep(duration, f1, f2)
    else:
	return writeBeep(duration, frequency1, frequency2)

def writeBeep(dur, _freq1, _freq2):
	duration = int(dur*1000)
	freq1 = int(_freq1)
	if(_freq2 != None):
		freq2 = int(_freq2)
	if(_freq2 == None):
		wRet =    writer.write([SET_SPEAKER, 
                              duration >> 8,
                              duration % 256,
                              freq1 >> 8,
                              freq1 % 256])
	else:
		wRet =     writer.write([SET_SPEAKER_2, 
                              duration >> 8,
                              duration % 256,
                              freq1 >> 8,
                              freq1 % 256,
              		      freq2 >> 8,
                              freq2 % 256])
	return wRet

def get(sensor = "all", *position):
	sensor = sensor.lower()
	if(sensor == "config"):
		return {"ir": 2, "line": 2, "stall": 1, "light": 3,"battery": 1, "obstacle": 3, "bright": 3}
	elif(sensor ==  "stall"):
		ret = getAll()
		scrib._lastSensors = ret
		return ret[9:]
	elif(sensor == "name"):
		n1 = _get(GET_NAME1,8)
		n2 = _get(GET_NAME2,8)
		c = n1 + n2
		c = string.join([chr(x) for x in c if "0" <= chr(x) <= "z"], '').strip()
		return c
	elif(sensor == "password"):
		c = _get(Scribbler.GET_PASS1, 8)
		c += _get(Scribbler.GET_PASS2, 8)
		c = string.join([chr(x) for x in c if "0" <= chr(x) <= "z"], '').strip()
		return c
	elif(sensor == "volume"):
		return scrib.volume

	elif(sensor == "battery"):
		return getBattery()

	elif(sensor == "blob"):
		return "blob"
	else:
		if(len(position)==0):
			if(sensor == "light"):
				return _get(GET_LIGHT_ALL, 6, "word")
			elif(sensor == "line"):
				return _get(GET_LINE_ALL, 2)
			elif(sensor == "ir"):
				return _get(GET_IR,2)
			elif(sensor == "obstacle"):
                    		return [getObstacle("left"), getObstacle("center"), getObstacle("right")]
                	elif(sensor == "bright"):
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
	return writer.read(20)

def getBattery():
	writer.write([GET_BATTERY])
	val = writer.read(PACKET_LENGTH)
	return read_2byte()

def identifyRobot():
	writer.write([GET_ROBOT_ID])
	ret = writer.read(PACKET_LENGTH + 11)
	return ret

def getIR():
	writer.write([GET_IR_ALL])
	writer.read(PACKET_LENGTH)
	writer.read(2)

def getObstacle(self, value=None):
	if value == None:
		return 	get("obstacle")           
	if value in ["left", 0]:
                writer.write(GET_DONGLE_L_IR)
        elif value in ["middle", "center", 1]:
        	writer.write(GET_DONGLE_C_IR)
        elif value in ["right", 2]:
		writer.write(GET_DONGLE_R_IR)
        retval = read_2byte()
        return retval  

def set(item, position, value = None):
        item = item.lower()
        if item == "led":
            if type(position) in [int, float]:
                if position == 0:
                    if isTrue(value): return _set(SET_LED_LEFT_ON)
                    else:             return _set(SET_LED_LEFT_OFF)
                elif position == 1:
                    if isTrue(value): return _set(SET_LED_CENTER_ON)
                    else:             return _set(SET_LED_CENTER_OFF)
                elif position == 2:
                    if isTrue(value): return _set(SET_LED_RIGHT_ON)
                    else:             return _set(SET_LED_RIGHT_OFF)
                else:
                    raise AttributeError("no such LED: '%s'" % position)
            else:
                position = position.lower()
                if position == "center":
                    if isTrue(value): return _set(SET_LED_CENTER_ON)
                    else:             return _set(SET_LED_CENTER_OFF)
                elif position == "left":
                    if isTrue(value): return _set(SET_LED_LEFT_ON)
                    else:             return _set(SET_LED_LEFT_OFF)
                elif position == "right":
                    if isTrue(value): return _set(SET_LED_RIGHT_ON)
                    else:             return _set(SET_LED_RIGHT_OFF)
                elif position == "front":
                    return setLEDFront(value)
                elif position == "back":
                    return setLEDBack(value)
                elif position == "all":
                    if isTrue(value): return _set(SET_LED_ALL_ON)
                    else:             return _set(SET_LED_ALL_OFF)
                else:
                    raise AttributeError("no such LED: '%s'" % position)
        elif item == "name":
            position = position + (" " * 16)
            name1 = position[:8].strip()
            name1_raw = map(lambda x:  ord(x), name1)
            name2 = position[8:16].strip()
            name2_raw = map(lambda x:  ord(x), name2)
            _set(*([SET_NAME1] + name1_raw))
            _set(*([SET_NAME2] + name2_raw))
        elif item == "password":
            position = position + (" " * 16)
            pass1 = position[:8].strip()
            pass1_raw = map(lambda x:  ord(x), pass1)
            pass2 = position[8:16].strip()
            pass2_raw = map(lambda x:  ord(x), pass2)
            _set(*([SET_PASS1] + pass1_raw))
            _set(*([SET_PASS2] + pass2_raw))
        elif item == "whitebalance":
            setWhiteBalance(position)
        elif item == "irpower":
            setIRPower(position)
        elif item == "volume":
            if isTrue(position):
                _volume = 1
                return _set(SET_LOUD)
            else:
                _volume = 0
                return _set(SET_QUIET)
        elif item == "startsong":
            startsong = position
        elif item == "echomode":
            return setEchoMode(position)
        elif item == "data":
            return setData(position, value)
        elif item == "password":
            return setPassword(position)
        elif item == "forwardness":
            return setForwardness(position)
        else:
            raise ("invalid set item name: '%s'" % item)


def setLEDFront(pos):
	DEBUG(str(pos))
def setLEDBack(pos):
	DEBUG(str(pos))
def setWhiteBalance(pos):
	DEBUG(str(pos))
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

def ask(*args):
	"""
	Doesnt do anything for now
	"""

	return None 
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
	writer.write([values],len(values))
	test = writer.read(PACKET_LENGTH) # read echo
	_lastSensors = writer.read(11) # single bit sensors

def DEBUG(s):
	if(debug):
		print(s)

