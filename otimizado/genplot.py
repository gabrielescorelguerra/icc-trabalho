#! /usr/bin/env python3

import os
import re

import matplotlib

matplotlib.use("Agg")  # so salva as imagens, nao tenta abrir janela
import matplotlib.pyplot as plt
import matplotlib.ticker

# nome dos campos que serao lidos dos arquivos de saida do likwid-perfctr -O
campos = {
    "L2CACHE": "L2 miss ratio",
    "FLOPS_DP": r"DP \[*MFLOP/s\]*",
    "FLOPS_AVX": r"Packed DP \[*MFLOP/s\]*",
    "MEM": r"Memory bandwidth \[*MBytes/s\]*",
}

# testes considerados
testes = {
    "MEM": ("Memory bandwidth [MBytes/s]", [("", "MEM")]),
    "L2CACHE": ("L2 miss ratio", [("", "L2CACHE")]),
    "FLOPS": ("MFLOP/s", [("DP", "FLOPS_DP"), ("AVX", "FLOPS_AVX")]),
}

# cor de cada versao; estilo de linha de cada grupo dentro do mesmo grafico
cores = {"base": "tab:blue", "otim": "tab:red"}
estilos = ("-", "--")

# nomes dos marcadores likwid usados no codigo C
trechos = ("newton", "calcJ", "eliminacaoGauss")

DIR_BASE = "../base/resultados"
DIR_OTIM = "./resultados"


def lerTamanhos(arquivo):
    """Tamanhos testados, na ordem em que foram rodados (1a coluna do
    Tempos.csv, sem repetir: cada N aparece uma vez por grupo do likwid)."""
    ns = []
    with open(arquivo) as f:
        for linha in f:
            p = linha.split(",")[0]
            if p.isdigit() and int(p) not in ns:
                ns.append(int(p))
    return ns


def lerDados(arquivo, trecho, campo, tamanhos):
    """Le o log de um grupo do likwid e devolve {N: valor} do campo no trecho.

    O log nao diz qual N gerou cada bloco, entao o i-esimo valor encontrado
    do trecho e associado ao i-esimo tamanho de 'tamanhos'.
    """
    valores = []
    dentro = False  # True enquanto estamos na tabela de metricas do trecho

    with open(arquivo) as f:
        for linha in f:
            if linha.startswith("TABLE"):
                partes = linha.split(",")
                dentro = partes[1] == "Region " + trecho and "Metric" in partes[2]

            elif dentro and re.match(campo, linha):
                valores.append(float(linha.split(",")[1]))
                dentro = False

    # verifica se o numero de valores encontrados bate com o numero de tamanhos
    if len(valores) != len(tamanhos):
        print(
            f"AVISO: {arquivo} ({trecho}): {len(valores)} valores "
            f"para {len(tamanhos)} tamanhos"
        )

    return dict(zip(tamanhos, valores))


def lerTempos(arquivo):
    """Le o Tempos.csv (linhas 'N,total,jacobiana,sistema') e devolve
    {trecho: {N: tempo medio}}. Cada N aparece varias vezes (uma por grupo
    do likwid), entao tira a media.
    """
    colunas = {"newton": 1, "calcJ": 2, "eliminacaoGauss": 3}
    medidas = {trecho: {} for trecho in colunas}  # {trecho: {N: [tempos]}}

    with open(arquivo) as f:
        for linha in f:
            partes = linha.strip().split(",")
            if len(partes) != 4 or not partes[0].isdigit():
                continue  # pula cabecalho e linhas estranhas
            n = int(partes[0])
            for trecho, i in colunas.items():
                medidas[trecho].setdefault(n, []).append(float(partes[i]))

    return {
        trecho: {n: sum(v) / len(v) for n, v in porN.items()}
        for trecho, porN in medidas.items()
    }


def gera_grafico(series, ylabel, titulo, arquivo, ylog=False):
    """series: lista de (legenda, {N: valor}, cor, estilo de linha)."""
    fig, ax = plt.subplots()
    Ns = set()

    for legenda, dados, cor, estilo in series:
        ns = sorted(dados)
        ys = [dados[n] for n in ns]
        ax.plot(ns, ys, marker="o", color=cor, linestyle=estilo, label=legenda)
        Ns |= set(ns)

    Ns = sorted(Ns)
    ax.set_xscale("log")
    if ylog:
        ax.set_yscale("log")
    ax.set_xticks(Ns)
    ax.set_xticklabels(Ns)  # mostra os N reais, não 10^x
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())  # sem ticks menores
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())  # evita sobreposicao
    ax.set_xlabel("N")
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    ax.legend()
    ax.grid(True)

    os.makedirs("graficos", exist_ok=True)
    fig.savefig(f"graficos/{arquivo}.png", dpi=150)  # salva como imagem
    plt.close(fig)


def main():
    versoes = tuple(
        (nome, d, lerTamanhos(f"{d}/Tempos.csv"))
        for nome, d in (("base", DIR_BASE), ("otim", DIR_OTIM))
    )

    for trecho in trechos:
        # teste de tempo (eixo y em log)
        series = []
        for nome, diretorio, _ in versoes:
            tempos = lerTempos(f"{diretorio}/Tempos.csv")[trecho]
            series.append((nome, tempos, cores[nome], "-"))
        gera_grafico(
            series, "Tempo medio [ms]", f"Tempo: {trecho}", f"tempo_{trecho}", ylog=True
        )

        # testes do likwid
        for teste, (ylabel, grupos) in testes.items():
            series = []
            for nome, diretorio, tamanhos in versoes:
                for (rotulo, grupo), estilo in zip(grupos, estilos):
                    dados = lerDados(
                        f"{diretorio}/{grupo}.log", trecho, campos[grupo], tamanhos
                    )
                    legenda = f"{nome} - {rotulo}" if rotulo else nome
                    series.append((legenda, dados, cores[nome], estilo))
            gera_grafico(series, ylabel, f"{teste}: {trecho}", f"{teste}_{trecho}")


if __name__ == "__main__":
    main()
