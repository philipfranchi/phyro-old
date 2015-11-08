from ctypes import *

libc = cdll.LoadLibrary("/home/phil/Work/Phyro/fluke2Server/testPhyroC/phyro.so")
buf = create_string_buffer(10000)
libc.test_buf(buf)
print buf.raw
