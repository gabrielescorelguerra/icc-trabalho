#ifndef __UTILS_H__
#define __UTILS_H__

#include <stdlib.h>
#include <time.h>
#include <sys/time.h>

// rtime_t: tipo usado para representar valores de tempo em ponto flutuante
typedef double rtime_t;

// Funções
rtime_t timestamp(void);

#endif // __UTILS_H__

