# local compile on fluke
CC = gcc   
CFLAGS  = -fPIC -Wall -O2
# only necessary for cross compile
INCLUDES = -Iarm-include
# only necessary for cross compile
LFLAGS = -Larm-lib
LIBS = -ljpeg -lm

all: phyroC.so

phyroC.so:	    pcam.o  pfluke2.o pgpio.o pmisc.o
		$(CC) -shared -Wall -o phyroC.so  pfluke2.o pgpio.o pcam.o pmisc.o $(LIBS) 


pfluke2.o:	    pfluke2.c phyro.h
		$(CC) $(CFLAGS) $(INCLUDES) -c pfluke2.c
pcam.o:		    pcam.c phyro.h
		$(CC) $(CFLAGS) $(INCLUDES) -c pcam.c
pgpio.o:		pgpio.c phyro.h
		$(CC) $(CFLAGS) $(INCLUDES) -c pgpio.c
pmisc.o:		pmisc.c phyro.h
		$(CC) $(CFLAGS) $(INCLUDES) -c pmisc.c
clean:
		rm -f phyroC.so *.o
