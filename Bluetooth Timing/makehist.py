import time, random, serial, math, pygal


def _read(bytes):
	c = ""
	while(len(c) < bytes ):
		c += str(ord(ser.read(1)))
	print("	" + str(c))
	return c

def writeChar(charByte):
	
	global ser

	towrite = []
	totBytes = pow(2, charByte-224)

	print(" Writing " + str(pow(2,charByte - 224)) + " bytes")


	for i in range( totBytes ):
		towrite.append( ord(chr(224)) )

	towrite[0] = charByte


	ser.write(towrite)

	retstring = "	wrote: "
	for i in towrite:
		retstring += ( str(i) + " ")
	#print(retstring)



def readChar(toread):
	print(" Reading ")
	size = ser.read(1)

	while(toread>1 and len(size)<toread):
		print("		...")
		size += ser.read(1)
	print("DONE!: " + size)
	return size


allresults = []
iterations = 10
bytesToWrite = 8


print("Opening Port")
ser = serial.Serial("/dev/tty.Fluke2-0640-Fluke2",57600,timeout = 1)
print("Port Open! \n")

for i in range(bytesToWrite):

	tot = 0.0
	results = []
	towrite = [chr(224+i)]* (pow(2,i))
	print("Testing "+ str(224+1))
	for t in range(iterations):
		#curChar = chr( ord(towrite) + i)
		#curChar = [chr(225),chr(225)]
		
		pre = time.clock()

		wri = writeChar(224 +i)
		
		inchr = ser.read(1)
		
		post = time.clock()
		
		print(	'Trial '+ str(t) + ' completed')

		tot = (post-pre)
		results.append(tot)

	allresults.append(results)