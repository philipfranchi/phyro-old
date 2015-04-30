import time, random, serial


def _read(bytes):
	c = ""
	while(len(c) < bytes ):
		c += str(ord(ser.read(1)))
	print("	" + str(c))
	return c


thing = []
iterations = 10



print("Opening Port")
ser = serial.Serial("/dev/tty.Fluke2-0640-Fluke2",57600,timeout = 1)
print("Port Open! \n")

for i in range(32):

	tot = 0.0
	results = []
	towrite = [chr(224+i)]*i
	
	for t in range(iterations):
		#curChar = chr( ord(towrite) + i)
		#curChar = [chr(225),chr(225)]
		
		pre = time.clock()
		

		ser.write(towrite)
		
		inchr = ser.read(1)

		print(towrite)
		
		post = time.clock()
		
		print("cur char: " + str(towrite) + " returned "+str(towrite));
		
		tot = (post-pre)
		results.append(tot)

	thing.append(results)
		
for x in thing:
	for y in x:
		print("	"+str(y))
	print(str(x))


