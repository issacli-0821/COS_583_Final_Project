CFLAGS ?= -O -g

SRC_DIR = macro11/
BIN_DIR = bin/

MACRO11_SRCS = $(SRC_DIR)macro11.c \
	$(SRC_DIR)assemble.c $(SRC_DIR)assemble_globals.c $(SRC_DIR)assemble_aux.c \
	$(SRC_DIR)extree.c $(SRC_DIR)listing.c $(SRC_DIR)macros.c $(SRC_DIR)parse.c $(SRC_DIR)rept_irpc.c $(SRC_DIR)symbols.c \
	$(SRC_DIR)mlb.c $(SRC_DIR)object.c $(SRC_DIR)stream2.c $(SRC_DIR)util.c $(SRC_DIR)rad50.c

MACRO11_OBJS = $(MACRO11_SRCS:.c=.o)

DUMPOBJ_SRCS = $(SRC_DIR)dumpobj.c $(SRC_DIR)rad50.c

DUMPOBJ_OBJS = $(DUMPOBJ_SRCS:.c=.o)

ALL_SRCS = $(MACRO11_SRCS) $(DUMPOBJ_SRCS)

all: $(BIN_DIR)macro11 $(BIN_DIR)dumpobj

tags: $(BIN_DIR)macro11 $(BIN_DIR)dumpobj
	ctags $(SRC_DIR)*.c $(SRC_DIR)*.h

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)macro11: $(MACRO11_OBJS) Makefile $(BIN_DIR)
	$(CC) $(CFLAGS) -o $(BIN_DIR)macro11 $(MACRO11_OBJS) -lm

$(BIN_DIR)dumpobj: $(DUMPOBJ_OBJS) Makefile $(BIN_DIR)
	$(CC) $(CFLAGS) -o $(BIN_DIR)dumpobj $(DUMPOBJ_OBJS)

MACRO11_OBJS: Makefile
DUMPOBJ_OBJS: Makefile

clean:
	-rm -f $(MACRO11_OBJS) $(DUMPOBJ_OBJS)
	-rm -f $(BIN_DIR)macro11 $(BIN_DIR)dumpobj
	-rmdir $(BIN_DIR) 2>/dev/null || true

$(SRC_DIR)macro11.o: $(SRC_DIR)macro11.c $(SRC_DIR)macro11.h $(SRC_DIR)rad50.h $(SRC_DIR)object.h $(SRC_DIR)stream2.h \
 $(SRC_DIR)mlb.h $(SRC_DIR)util.h
$(SRC_DIR)mlb.o: $(SRC_DIR)mlb.c $(SRC_DIR)rad50.h $(SRC_DIR)stream2.h $(SRC_DIR)mlb.h $(SRC_DIR)macro11.h $(SRC_DIR)util.h
$(SRC_DIR)object.o: $(SRC_DIR)object.c $(SRC_DIR)rad50.h $(SRC_DIR)object.h
$(SRC_DIR)stream2.o: $(SRC_DIR)stream2.c $(SRC_DIR)macro11.h $(SRC_DIR)stream2.h
$(SRC_DIR)util.o: $(SRC_DIR)util.c $(SRC_DIR)util.h
$(SRC_DIR)rad50.o: $(SRC_DIR)rad50.c $(SRC_DIR)rad50.h
$(SRC_DIR)dumpobj.o: $(SRC_DIR)dumpobj.c $(SRC_DIR)rad50.h $(SRC_DIR)util.h
$(SRC_DIR)rad50.o: $(SRC_DIR)rad50.c $(SRC_DIR)rad50.h

# Since the only tests we have so far are for crashes,
# just try to assemble. Later, we will need expected/actual tests.

# Test that all options requiring a value bail out if it's not present.
argtests: $(BIN_DIR)macro11
	@ for OPT in -e -d -m -p -o -l -ysl ; do \
	  $(BIN_DIR)macro11 $(SRC_DIR)foo.mac $$OPT     2> /dev/null; \
    if (( $$? == 1 )); then echo PASS; else echo FAIL; fi; \
    echo "  $$OPT missing value"; \
	  $(BIN_DIR)macro11 $(SRC_DIR)foo.mac $$OPT -v  2> /dev/null; \
    if (( $$? == 1 )); then echo PASS; else echo FAIL; fi; \
    echo "  $$OPT fol. by option"; \
	done
	@ $(BIN_DIR)macro11 $(SRC_DIR)foo.mac $$OPT -x -v 2> /dev/null; \
    if (( $$? == 1 )); then echo PASS; else echo FAIL; fi; \
    echo "  -x must be the last option"

tests: $(BIN_DIR)macro11 argtests
	@ ACTUAL=`$(BIN_DIR)macro11 $(SRC_DIR)tests/test-undef.mac 2>&1`; \
	if [ "$(SRC_DIR)tests/test-undef.mac:1: ***ERROR MACRO .TTYOU not found" == "$$ACTUAL" ]; then echo PASS; else echo FAIL; fi; \
	echo "  test-undef.mac"