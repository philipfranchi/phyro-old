import time, random, serial, math


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
	'''
	if(totBytes > 255):
		 idx = 0
		 print("Alot of Writing")

		 while(idx<totBytes):
		 	
		 	tempList = []
		 	for i in range(256):
		 		tempList.append(towrite[idx])
		 		if(idx == 0):
		 			print("YES")
		 			tempList[0] = chr(255)
		 		print( towrite[idx] ),
		 		idx+=1
		 	ser.write(tempList)

		 return 1
	'''

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


thing = []
iterations = 10



print("Opening Port")
ser = serial.Serial("/dev/tty.Fluke2-0640-Fluke2",57600,timeout = 1)
print("Port Open! \n")

for i in range(8):

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

	thing.append(results)
		
for x in range(8):
	for y in thing[x]:
		print("		"+str(y))
	print(str(x))


