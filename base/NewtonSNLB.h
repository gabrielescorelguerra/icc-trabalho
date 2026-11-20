#ifndef NEWTONSNLB_H
#define NEWTONSNLB_H

// Função para resolver o sistema de equações não lineares usando o método de Newton
int newton(double *X, double epsilon, int n, int MAXIT);

// Função para calcular a norma do vetor V de tamanho n
double norma(double *V, int n);

#endif