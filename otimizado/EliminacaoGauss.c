#include <math.h>
#include "EliminacaoGauss.h"


void eliminacaoGauss(double *Jdiag, double *S, double *f, int n) {
  triang(Jdiag, f, n);
  retrossubs(Jdiag, S, f, n);
}

void triang(double *Jdiag, double *f, int n) {
    for (int i = 0; i < n - 1; ++i) {
        // elimina as entradas nas linhas abaixo do pivo (apenas i + 1 precisa ser explicito)
        double m = -1 / Jdiag[i];
        Jdiag[i+1] -= -2 * m;

        // reflete a mudança no vetor f
        f[i+1] -= f[i] * m;
    }
}

void retrossubs(double *Jdiag, double *S, double *f, int n) {
    // ultima linha
    S[n-1] = f[n-1] / Jdiag[n-1];

    // demais linhas
    for (int i = n-2; i >=0; --i) {
        S[i] = (f[i] + 2*S[i + 1]) / Jdiag[i]; 
    }
}
