
def trythis(*values):
	t = map(lambda x: chr(int(x)), *values)
	data = string.join(t, '') + (chr(0) * (PACKET_LENGTH - len(t)))[:9]
	return data

print(trythis(109,0,0,0,0))
