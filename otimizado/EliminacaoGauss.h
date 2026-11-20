// algoritmo de eliminacao de Gauss, agora sem pivoteamento
// jacobiana representada explicitamente apenas por sua diagonal, demais elementos tem valor conhecido
void eliminacaoGauss(double *Jdiag, double *S, double *f, int n);

// triangularização
void triang(double *Jdiag, double *f, int n);

// retrossubstituição
void retrossubs(double *Jdiag, double *S, double *f, int n);
