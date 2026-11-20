#!/bin/bash

CMD_DIR=`dirname $0`
# executavel gerado pelo Makefile da raiz
PROG=${1:-../broyden}

# core usado pelo likwid
CPU=${2:-3}

# define onde os dados serao armazenados
DATA_DIR="resultados"
TEMPOS="${DATA_DIR}/Tempos.csv"

# metricas a serem avaliadas pelo likwid
METRICA="MEM L2CACHE FLOPS_DP FLOPS_AVX"

# tamanhos a serem testados
# apenas ate 4000 devido ao tempo de execucao muito elevado
TAMANHOS="32 64 128 256 512 1000 2000 4000 8000 9000 10000 20000"

# entradas do broyden
X0=-1
EPS=0
MAXIT=25

# numero de execucoes de cada teste (o grafico usa a media)
REPS=10

# diretorio de saida
mkdir -p ${DATA_DIR}

likwid-setFrequencies -g performance -c ${CPU}

# remove os arquivos gerados na ultima compilacao e compila novamente
make -C .. clean
make -C ..
rm -f ${TEMPOS}

# execucao de aquecimento (descartada): evita que o 1o grupo medido seja mais lento
printf "%s\n%s\n%s\n%s\n" "32" "$X0" "$EPS" "$MAXIT" | likwid-perfctr -O -C ${CPU} -g MEM -m ${PROG} >/dev/null 2>&1


for m in ${METRICA}
do
    LIKWID_LOG="${DATA_DIR}/${m}.log"

    # remove resultados anteriores
    rm -f ${LIKWID_LOG}
    
    for n in $TAMANHOS
    do
      for rep in $(seq 1 ${REPS})
      do
        # temporario que vai receber os resultados
        LIKWID_OUT="${DATA_DIR}/${m}_${n}.txt"
        
        echo "n: ${n} , x0: ${X0}, EPS: ${EPS}, MAXIT: ${MAXIT}, rep: ${rep}/${REPS} --->>  $m: ${PROG}" >/dev/tty

        # executa o programa com o likwid, redirecionando a saida para um arquivo temporario
        printf "%s\n%s\n%s\n%s\n" "$n" "$X0" "$EPS" "$MAXIT" | likwid-perfctr -O -C ${CPU} -g ${m} -o ${LIKWID_OUT} -m ${PROG} \
                | awk '/^###########$/ {f = !f; next} f' | paste -sd, - | sed "s/^/${n},/" >> ${TEMPOS}
            
        cat ${LIKWID_OUT} >> ${LIKWID_LOG}

        rm -f ${LIKWID_OUT}
      done
    done
done

likwid-setFrequencies -g powersave -c ${CPU}

echo ""
echo ""
