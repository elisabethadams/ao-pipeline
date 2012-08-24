SHELL =		/bin/sh
RANLIB =	echo ranlib
CC =		cc
CFLAGS =	-O
LDFLAGS =	$(CFLAGS)
DEFS =		
FLEX =		flex
BISON =		bison

.c.o:
		$(CC) -c $(CFLAGS) $(DEFS) $<

all:		corquad

corquad:	corquad.o 
		${CC} $(CFLAGS) $(DEFS) -o corquad corquad.o -lcfitsio -lm
		strip corquad 

static:		corquad.o
		${CC} $(CFLAGS) -static $(DEFS) -o corquad corquad.o -lcfitsio -lm
		strip corquad 

clean:
	-	/bin/rm -f *~ *.o corquad
