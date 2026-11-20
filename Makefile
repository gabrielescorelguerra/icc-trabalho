# Compila a versao otimizada (fontes em otimizado/). O executavel fica na raiz.
SRC = otimizado

CFLAGS = -DLIKWID_PERFMON -I/home/soft/likwid/include
LFLAGS = -lm -L/home/soft/likwid/lib -llikwid

CC = gcc -O3 $(AVX_FLAGS)

PROG = broyden
OBJS = $(SRC)/utils.o $(SRC)/EliminacaoGauss.o $(SRC)/NewtonSNLB.o $(SRC)/SistNaoLinearBroyden.o

AVX_FLAGS = -mavx2 -march=native -fopt-info-vec

all: $(PROG)

$(PROG): $(OBJS) $(SRC)/$(PROG).o
	$(CC) $(CFLAGS) -o $@ $^ $(LFLAGS)

$(SRC)/$(PROG).o: $(SRC)/$(PROG).c $(SRC)/utils.h $(SRC)/EliminacaoGauss.h $(SRC)/NewtonSNLB.h $(SRC)/SistNaoLinearBroyden.h
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(PROG) $(OBJS) $(SRC)/$(PROG).o
