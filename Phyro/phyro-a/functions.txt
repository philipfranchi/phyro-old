class Scribbler
    def __init__(self, serialport = None, baudrate = 38400):
    def search(self):
    def open(self):
    def close(self):
    def manual_flush(self):
    def restart(self):
    def beep(self, duration, frequency, frequency2 = None):
    def get(self, sensor = "all", *position):
    def getData(self, *position):
    def getInfo(self, *item):
    def set_blob_yuv(self, picture, x1, y1, x2, y2):
    def configureBlob(self,
    def conf_rle(self, delay = 90, smooth_thresh = 4, 
    def read_uint32(self):
    def read_jpeg_scan(self):
    def read_jpeg_header(self):
    def grab_jpeg_color(self, reliable):
    def grab_jpeg_gray(self, reliable):
    def takePicture(self, mode=None):
    def _grab_blob_array(self):
    def _grab_gray_array(self):
    def _grab_array(self):
    def _grab_array_bilinear_horizontal(self):
    def _grab_array_bilinear_vert(self):
    def getBattery(self):
    def identifyRobot(self):
    def getIRMessage(self):
    def sendIRMessage(self, data):
    def setCommunicateLeft(self, on=True):
    def setCommunicateCenter(self, on=True):
    def setCommunicateRight(self, on=True):
    def setCommunicateAll(self, on=True):
    def setCommunicate(self):
    def setBrightPower(self, power):
    def setLEDFront(self, value):
    def setLEDBack(self, value):
    def getObstacle(self, value=None):
    def getDistance(self, value=None):
    def getBright(self, window=None):
    def getBlob(self):
    def setForwardness(self, direction):
    def setIRPower(self, power):
    def setWhiteBalance(self, value):
    def reboot(self):
    def set_cam_param(self, addr, byte):
    def get_cam_param(self, addr):
    def darkenCamera(self, level=0):
    def manualCamera(self, gain=0x00, brightness=0x80, exposure=0x41):
    def autoCamera(self):
    def setPicSize(self, size):
    def servo(self, id, position):
    def getFlukeLog(self):
    def enablePanNetworking(self):
    def reset(self):
    def setData(self, position, value):
    def setSingleData(self,position,value):
    def setEchoMode(self, value):
    def set(self, item, position, value = None):
    def setFudge(self,f1,f2,f3,f4):
    def loadFudge(self):
    def getFudge(self):
    def stop(self):
    def hardStop(self):
    def translate(self, amount):
    def rotate(self, amount):
    def move(self, translate, rotate):
    def getPosition(self):
    def setHereIs(self, x, y):
    def getAngle(self):
    def setAngle(self, angle):
    def setBeginPath(self, speed=7):
    def setTurn(self, angle, turnType="to", radOrDeg="rad"):
    def setMove(self, x, y, moveType = "to"):
    def setArc(self, x, y, radius, arcType="to"):
    def setEndPath(self):
    def setS2Volume(self, level):
    def getMicEnvelope(self):
    def getMotorStats(self):
    def getEncoders(self, zeroEncoders=False):
    def getLastSensors(self):
    def update(self):
    def _IsScribbler2(self):
    def _IsInTransit(self):
    def _adjustSpeed(self):
    def _read(self, bytes = 1):
    def _write(self, rawdata):
    def _set(self, *values):
    def _setWithTime(self, waitTime, *values):
    def _getWithSetByte(self, packetValue, bytes = 1, mode = "byte", setByte=0xff):
    def _get(self, value, bytes = 1, mode = "byte", setByte=0xff):
    def _set_speaker(self, frequency, duration):            
    def _set_speaker_2(self, freq1, freq2, duration):
def cap(c):
def conf_window(self, window, X_LOW, Y_LOW, X_HIGH, Y_HIGH, X_STEP, Y_STEP):
def conf_gray_window(self, window, lx, ly, ux, uy, xstep, ystep):
def conf_gray_image(self):
def grab_rle_on(self):
def read_2byte(ser):
def read_3byte(ser):
def write_2byte(ser, value):
def read_mem(ser, page, offset):
def write_mem(ser, page, offset, byte):
def erase_mem(ser, page):
def set_scribbler_memory(ser, offset, byte):
def get_scribbler_memory(ser, offset):
def set_scribbler_start_program(ser, size):
def set_scribbler2_start_program(ser, size):
def get_window_avg(ser, window):
def quadrupleSize(line, width):
def set_ir_power(ser, power):
