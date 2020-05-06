# Stupid Makefile for program CheckIERS
#
# Valid for kis001
#
# $Id$
#
# Uses weekly casacore. 
#
CFLAGS = -g -Wall
CC = g++
AIPSFLAGS = -DAIPS -DAIPS_LINUX -DAIPS_LITTLE_ENDIAN -DAIPS_AUTO_STL -DAIPS_NO_TEMPLATE_SRC
#AIPSLIBD = -L/data/casacore/weekly/casacore/lib
AIPSLIBD = -L/opt/casacore/lib -Wl,-rpath=/opt/casacore/lib
AIPSLIBS = -lcasa_measures -lcasa_tables -lcasa_casa
#AIPSINCD = -I/data/casacore/weekly/casacore/include/casacore
AIPSINCD = -I/opt/casacore/include

INCLUDES = -I. $(AIPSINCD)
LIBS = $(AIPSLIBD) $(AIPSLIBS) -ldl
FLAGS = $(AIPSFLAGS)
OBJS = CheckIERS.o
SRCS = CheckIERS.cc

all: CheckIERS

CheckIERS: $(OBJS) ${HDRS}
	   ${CC} ${CFLAGS} ${FLAGS} ${INCLUDES} -o $@ $(OBJS) ${LIBS}

.cc.o:
	${CC} ${CFLAGS} ${FLAGS} ${INCLUDES} -c $<

depend: 
	makedepend ${SRCS}

clean:
	rm *.o 
