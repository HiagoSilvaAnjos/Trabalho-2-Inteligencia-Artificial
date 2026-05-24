import random
import time
import json
import argparse

# ──────────────────────────────────────────────────────────────────────────────
# Funções auxiliares (reutilizadas do Hill Climbing)
# ──────────────────────────────────────────────────────────────────────────────

def calcular_conflitos(estado):
    """Calcula o número de pares de rainhas em conflito (mesma linha ou diagonal)."""
    h = 0
    n = len(estado)
    for i in range(n):
        for j in range(i + 1, n):
            if estado[i] == estado[j]:               # Mesma linha
                h += 1
            elif abs(estado[i] - estado[j]) == abs(i - j):  # Mesma diagonal
                h += 1
    return h


def custo_incremental(estado_parcial, col, linha):
    """
    Calcula quantos conflitos a rainha na posição (col, linha) geraria
    com as rainhas já posicionadas em estado_parcial[0..col-1].
    """
    conflitos = 0
    for c in range(col):
        if estado_parcial[c] == linha:                     # Mesma linha
            conflitos += 1
        elif abs(estado_parcial[c] - linha) == abs(c - col):  # Mesma diagonal
            conflitos += 1
    return conflitos


# ──────────────────────────────────────────────────────────────────────────────
# Fase Construtiva Gulosa-Randomizada (GRASP)
# ──────────────────────────────────────────────────────────────────────────────

def construir_solucao_gulosa_randomizada(n, alpha):
    """
    Constrói uma solução para o problema das n-rainhas usando a fase construtiva
    do GRASP.

    Parâmetros
    ----------
    n : int
        Tamanho do tabuleiro (tipicamente 8).
    alpha : float
        Parâmetro da RCL por qualidade (0 ≤ α ≤ 1).
        α = 0  → puramente guloso (escolhe sempre o melhor candidato).
        α = 1  → puramente aleatório (qualquer candidato é válido).
        A RCL inclui todos os candidatos cujo custo está no intervalo
        [custo_min, custo_min + α × (custo_max − custo_min)].

    Retorna
    -------
    list[int] : estado com n rainhas posicionadas (índice = coluna, valor = linha).
    """
    estado = [0] * n

    for col in range(n):
        # Calcula o custo incremental de cada linha candidata
        candidatos = []
        for linha in range(n):
            custo = custo_incremental(estado, col, linha)
            candidatos.append((custo, linha))

        custo_min = min(c[0] for c in candidatos)
        custo_max = max(c[0] for c in candidatos)

        # Define a Lista Restrita de Candidatos (RCL) por qualidade
        limiar = custo_min + alpha * (custo_max - custo_min)
        rcl = [linha for custo, linha in candidatos if custo <= limiar]

        # Escolha aleatória dentro da RCL
        estado[col] = random.choice(rcl)

    return estado


# ──────────────────────────────────────────────────────────────────────────────
# Fase de Busca Local (idêntica ao Hill Climbing Steepest Ascent)
# ──────────────────────────────────────────────────────────────────────────────

def busca_local(estado, max_iter_local=500):
    """
    Aplica Hill Climbing (steepest ascent) à solução construída.
    Retorna (estado_melhorado, h_final, iteracoes_usadas).
    """
    estado_atual = list(estado)
    h_atual = calcular_conflitos(estado_atual)
    n = len(estado_atual)
    iteracoes = 0

    while h_atual > 0 and iteracoes < max_iter_local:
        melhores_vizinhos = []
        menor_h = float('inf')

        for col in range(n):
            for linha in range(n):
                if estado_atual[col] != linha:
                    vizinho = list(estado_atual)
                    vizinho[col] = linha
                    h_v = calcular_conflitos(vizinho)

                    if h_v < menor_h:
                        menor_h = h_v
                        melhores_vizinhos = [vizinho]
                    elif h_v == menor_h:
                        melhores_vizinhos.append(vizinho)

        iteracoes += 1

        if menor_h < h_atual:
            estado_atual = random.choice(melhores_vizinhos)
            h_atual = menor_h
        else:
            # Nenhuma melhora possível: ótimo local
            break

    return estado_atual, h_atual, iteracoes


# ──────────────────────────────────────────────────────────────────────────────
# Execução Principal do GRASP
# ──────────────────────────────────────────────────────────────────────────────

def executar_grasp(id_execucao, max_iter, alpha):
    """
    Executa uma instância do GRASP para o problema das 8-rainhas.

    Critério de parada: máximo de `max_iter` iterações (construção + busca local)
    ou solução com zero conflitos.

    Retorna um dicionário com os campos exigidos pelo pipeline.
    """
    n = 8
    estado_inicial = [random.randint(0, n - 1) for _ in range(n)]

    melhor_estado = None
    melhor_h = float('inf')
    sucesso = False
    iteracoes_totais = 0
    iter_bl_total = 0

    inicio_tempo = time.perf_counter()

    for _ in range(max_iter):
        # Fase 1: Construção gulosa-randomizada
        estado_construido = construir_solucao_gulosa_randomizada(n, alpha)

        # Fase 2: Busca local
        estado_melhorado, h_final, iters_bl = busca_local(estado_construido)

        iteracoes_totais += 1
        iter_bl_total += iters_bl

        if h_final < melhor_h:
            melhor_h = h_final
            melhor_estado = list(estado_melhorado)

        if melhor_h == 0:
            sucesso = True
            break

    fim_tempo = time.perf_counter()
    tempo_ms = round((fim_tempo - inicio_tempo) * 1000, 2)

    return {
        "id_execucao": id_execucao,
        "estado_inicial": estado_inicial,
        "iteracoes": iteracoes_totais,
        "iter_busca_local": iter_bl_total,
        "tempo_ms": tempo_ms,
        "estado_final": melhor_estado,
        "h_final": melhor_h,
        "sucesso": sucesso,
        "alpha": alpha,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Ponto de Entrada
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Algoritmo GRASP para o Problema das 8-Rainhas")
    parser.add_argument("--num_execucoes", type=int, default=1,
                        help="Número de execuções independentes do GRASP")
    parser.add_argument("--max_iter", type=int, default=1000,
                        help="Número máximo de iterações (construção+busca local) por execução")
    parser.add_argument("--alpha", type=float, default=0.3,
                        help="Parâmetro da RCL (0=guloso puro, 1=aleatório puro)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Semente para o gerador de números aleatórios")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    resultados = []
    for i in range(1, args.num_execucoes + 1):
        resultado = executar_grasp(i, args.max_iter, args.alpha)
        resultados.append(resultado)

    if args.num_execucoes == 1:
        print(json.dumps(resultados[0], ensure_ascii=False))
    else:
        print(json.dumps(resultados, ensure_ascii=False))


if __name__ == "__main__":
    main()
