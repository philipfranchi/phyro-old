'''
Phyro: Myro on the fluke
'''

import os

class Scribbler:
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
    GET_WINDOW_LIGHT=88    # average intensity in the user defined region
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
    SET_NAME2=119           # set name2 byte
    SET_LOUD=111
    SET_QUIET=112
    SET_SPEAKER=113
    SET_SPEAKER_2=114

    SET_DONGLE_LED_ON=116   # turn binary dongle led on
    SET_DONGLE_LED_OFF=117  # turn binary dongle led off
    SET_RLE=118             # set rle parameters 
    SET_DONGLE_IR=120       # set dongle IR power
    SET_SERIAL_MEM=121      # set serial memory byte
    SET_SCRIB_PROGRAM=122   # set scribbler program memory byte
    SET_START_PROGRAM=123   # initiate scribbler programming process
    SET_RESET_SCRIBBLER=124 # hard reset scribbler
    SET_SERIAL_ERASE=125    # erase serial memory
    SET_DIMMER_LED=126      # set dimmer led
    SET_WINDOW=127          # set user defined window
    SET_FORWARDNESS=128     # set direction of scribbler
    SET_WHITE_BALANCE=129   # turn on white balance on camera 
    SET_NO_WHITE_BALANCE=130 # diable white balance on camera (default)
    SET_CAM_PARAM=131       # with address and value, sets the camera parameter at that address

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
    SET_SCRIB_BATCH=155      # upload scribbler2 firmware
    GET_ROBOT_ID=156
    SET_VOLUME          = 160 #Format 160 volume (0-100) Percent Volume Level
    SET_PATH            = 161 #Format 161 begin_or_end speed         0            1           2
                              #                                begin=0 end=1   hSpeedByte lSpeedByte
    SET_MOVE            = 162 #Format 162 type hXByte lXByte hYByte lYByte
    SET_ARC             = 163 #Format 163 type hXByte lXByte hYByte lYByte hRadByte lRadByte
    SET_TURN            = 164 #Format 164 type hAngleByte lAngleByte
    GET_POSN            = 165 #Format 165
    SET_POSN            = 166 #Format 166 x0Byte x1Byte x2Byte x3Byte y0Byte y1Byte y2Byte y3Byte
    GET_ANGLE           = 167 #Format 167
    SET_ANGLE           = 168 #Format 168 angle0Byte angle1Byte angle2Byte angle3Byte
    GET_MIC_ENV         = 169 #Format 169
    GET_MOTOR_STATS     = 170 #Format 170
    GET_ENCODERS        = 171 #Format 171 type    

    GET_IR_EX           = 172 #Format 172 side type thres
    GET_LINE_EX         = 173 #Format 173 side type thres
    GET_DISTANCE        = 175 #Format 175 side

    GET_ERRORS          = 10    # Fluke2 only
    SET_PIC_SIZE        = 11    # Fluke2 only
    SET_SERVO           = 12    # Fluke2 only
    ENABLE_PAN          = 13    # Fluke2 only
    
    PACKET_LENGTH       = 9
    BEGIN_PATH          = 0  #Used with SET_PATH to say beginning of a path
    END_PATH            = 1  #Used with SET_PATH to say end of a path
    BY             = 4       #Used in movement commands, by means how much you wish to move by
    TO             = 2       #Used in movement commands, to means the heading you want to turn to
    DEG            = 1       #Used in movement commands, specifies using degress instead of S2 angle units

	def __init__(self, serialport = None, baudrate = 38400):


def writeToScribbler(to_write):
	'''
	This function calls scribio.c, passing it details about to to_write
	'''

	print(to_write)

	ret = 1

	return ret

def readFromScribbler(to_read = 1):
	'''
	This function will read from the scribbler buffer for as long as we tell it to
	'''

	ret = 2

	print(ret)

	return ret
