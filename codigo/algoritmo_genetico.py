import random
import time
import json
import argparse

# ──────────────────────────────────────────────────────────────────────────────
# Constantes do Problema
# ──────────────────────────────────────────────────────────────────────────────
N_RAINHAS = 8           # Tamanho do tabuleiro
BITS_POR_RAINHA = 3     # ceil(log2(8)) = 3 bits por rainha
CROMOSSOMO_LEN = N_RAINHAS * BITS_POR_RAINHA  # 24 bits por cromossomo
MAX_CONFLITOS = 28      # C(8,2) = 28 pares possíveis → fitness máximo = 28

# Parâmetros fixos conforme especificação do professor
TAXA_CRUZAMENTO = 0.80  # 80 % dos pares passam pelo cruzamento
TAXA_MUTACAO = 0.03     # 3 % de chance por bit de sofrer bit-flip
TAMANHO_POPULACAO = 100 # tamanho padrão da população


# ──────────────────────────────────────────────────────────────────────────────
# Codificação / Decodificação
# ──────────────────────────────────────────────────────────────────────────────

def codificar(estado):
    """
    Converte um vetor de posições (lista de 8 inteiros 0-7) para um cromossomo
    binário representado como lista de 24 bits (inteiros 0 ou 1).

    Exemplo: [3, 5, ...] → [0,1,1, 1,0,1, ...]
    """
    cromossomo = []
    for gene in estado:
        # Representa cada inteiro em 3 bits (MSB → LSB)
        for bit_pos in range(BITS_POR_RAINHA - 1, -1, -1):
            cromossomo.append((gene >> bit_pos) & 1)
    return cromossomo


def decodificar(cromossomo):
    """
    Converte o cromossomo binário (24 bits) de volta ao vetor de posições.
    Valores resultantes são truncados para o intervalo [0, 7] com módulo 8,
    garantindo validade mesmo com mutações que gerem valores > 7.
    """
    estado = []
    for i in range(N_RAINHAS):
        inicio = i * BITS_POR_RAINHA
        valor = 0
        for bit in cromossomo[inicio:inicio + BITS_POR_RAINHA]:
            valor = (valor << 1) | bit
        estado.append(valor % N_RAINHAS)  # Garante [0, 7]
    return estado


# ──────────────────────────────────────────────────────────────────────────────
# Avaliação de Fitness
# ──────────────────────────────────────────────────────────────────────────────

def calcular_conflitos(estado):
    """Calcula o número de pares de rainhas em conflito."""
    h = 0
    for i in range(N_RAINHAS):
        for j in range(i + 1, N_RAINHAS):
            if estado[i] == estado[j]:                          # Mesma linha
                h += 1
            elif abs(estado[i] - estado[j]) == abs(i - j):     # Mesma diagonal
                h += 1
    return h


def calcular_fitness(cromossomo):
    """
    fitness = MAX_CONFLITOS − conflitos_atuais
    fitness = 28  →  solução perfeita (zero conflitos)
    fitness = 0   →  pior caso possível (28 conflitos)
    """
    estado = decodificar(cromossomo)
    conflitos = calcular_conflitos(estado)
    return MAX_CONFLITOS - conflitos


# ──────────────────────────────────────────────────────────────────────────────
# Geração Inicial
# ──────────────────────────────────────────────────────────────────────────────

def criar_individuo():
    """Gera um cromossomo aleatório de 24 bits."""
    return [random.randint(0, 1) for _ in range(CROMOSSOMO_LEN)]


def criar_populacao(tamanho):
    return [criar_individuo() for _ in range(tamanho)]


# ──────────────────────────────────────────────────────────────────────────────
# Seleção por Roleta
# ──────────────────────────────────────────────────────────────────────────────

def selecionar_roleta(populacao, fitness_list):
    """
    Seleciona um indivíduo da população com probabilidade proporcional ao fitness.
    Utiliza o método da roleta (roulette wheel selection).
    """
    total_fitness = sum(fitness_list)

    if total_fitness == 0:
        # Todos com fitness zero: seleção uniforme
        return random.choice(populacao)

    ponto = random.uniform(0, total_fitness)
    acumulado = 0.0

    for individuo, fit in zip(populacao, fitness_list):
        acumulado += fit
        if acumulado >= ponto:
            return individuo

    return populacao[-1]  # Fallback de segurança


# ──────────────────────────────────────────────────────────────────────────────
# Cruzamento por Ponto de Corte
# ──────────────────────────────────────────────────────────────────────────────

def cruzar(pai1, pai2):
    """
    Cruzamento por um único ponto de corte aleatório.
    Retorna dois filhos. Taxa de 80% é aplicada externamente na main loop.
    """
    ponto = random.randint(1, CROMOSSOMO_LEN - 1)
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2


# ──────────────────────────────────────────────────────────────────────────────
# Mutação por Bit Flip
# ──────────────────────────────────────────────────────────────────────────────

def mutar(cromossomo, taxa_mutacao=TAXA_MUTACAO):
    """
    Cada bit tem `taxa_mutacao` de probabilidade de ser invertido (bit flip).
    Operação in-place sobre uma cópia; retorna o cromossomo mutado.
    """
    return [1 - bit if random.random() < taxa_mutacao else bit
            for bit in cromossomo]


# ──────────────────────────────────────────────────────────────────────────────
# Execução Principal do Algoritmo Genético
# ──────────────────────────────────────────────────────────────────────────────

def executar_genetico(id_execucao, max_geracoes, tamanho_populacao):
    """
    Executa uma instância do Algoritmo Genético para o problema das 8-rainhas.

    Parâmetros fixos pelo professor:
    - Representação: binária (24 bits)
    - Seleção: roleta
    - Cruzamento: ponto de corte único, taxa 80%
    - Mutação: bit flip, taxa 3%
    - Elitismo: melhor indivíduo sempre preservado
    - Critério de parada: max_geracoes gerações ou fitness = 28

    Retorna dicionário com métricas da execução.
    """
    n = N_RAINHAS

    # Estado inicial: estado do melhor indivíduo da população inicial
    estado_inicial = decodificar(criar_individuo())

    inicio_tempo = time.perf_counter()

    # Cria a população inicial
    populacao = criar_populacao(tamanho_populacao)
    fitness_list = [calcular_fitness(ind) for ind in populacao]

    melhor_idx = fitness_list.index(max(fitness_list))
    melhor_individuo = list(populacao[melhor_idx])
    melhor_fitness = fitness_list[melhor_idx]

    geracao_parada = 0
    sucesso = False

    for geracao in range(1, max_geracoes + 1):
        geracao_parada = geracao

        # Verifica critério de parada
        if melhor_fitness == MAX_CONFLITOS:
            sucesso = True
            break

        nova_populacao = []

        # Elitismo: preserva o melhor indivíduo sem modificação
        nova_populacao.append(list(melhor_individuo))

        # Gera o restante da população
        while len(nova_populacao) < tamanho_populacao:
            # Seleção por roleta
            pai1 = selecionar_roleta(populacao, fitness_list)
            pai2 = selecionar_roleta(populacao, fitness_list)

            # Cruzamento (80% de chance)
            if random.random() < TAXA_CRUZAMENTO:
                filho1, filho2 = cruzar(pai1, pai2)
            else:
                filho1, filho2 = list(pai1), list(pai2)

            # Mutação (3% por bit)
            filho1 = mutar(filho1)
            filho2 = mutar(filho2)

            nova_populacao.append(filho1)
            if len(nova_populacao) < tamanho_populacao:
                nova_populacao.append(filho2)

        populacao = nova_populacao
        fitness_list = [calcular_fitness(ind) for ind in populacao]

        # Atualiza o melhor global
        melhor_idx_atual = fitness_list.index(max(fitness_list))
        if fitness_list[melhor_idx_atual] > melhor_fitness:
            melhor_fitness = fitness_list[melhor_idx_atual]
            melhor_individuo = list(populacao[melhor_idx_atual])

    fim_tempo = time.perf_counter()
    tempo_ms = round((fim_tempo - inicio_tempo) * 1000, 2)

    estado_final = decodificar(melhor_individuo)
    h_final = calcular_conflitos(estado_final)

    return {
        "id_execucao": id_execucao,
        "estado_inicial": estado_inicial,
        "iteracoes": geracao_parada,          # alias para compatibilidade com CSV
        "geracao_parada": geracao_parada,
        "tempo_ms": tempo_ms,
        "estado_final": estado_final,
        "h_final": h_final,
        "fitness_final": melhor_fitness,
        "sucesso": sucesso,
        "tamanho_populacao": tamanho_populacao,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Ponto de Entrada
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Algoritmo Genético (Binário) para o Problema das 8-Rainhas"
    )
    parser.add_argument("--num_execucoes", type=int, default=1,
                        help="Número de execuções independentes do AG")
    parser.add_argument("--max_geracoes", type=int, default=1000,
                        help="Número máximo de gerações por execução")
    parser.add_argument("--tamanho_populacao", type=int, default=100,
                        help="Tamanho da população em cada geração")
    parser.add_argument("--seed", type=int, default=None,
                        help="Semente para o gerador de números aleatórios")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    resultados = []
    for i in range(1, args.num_execucoes + 1):
        resultado = executar_genetico(i, args.max_geracoes, args.tamanho_populacao)
        resultados.append(resultado)

    if args.num_execucoes == 1:
        print(json.dumps(resultados[0], ensure_ascii=False))
    else:
        print(json.dumps(resultados, ensure_ascii=False))


if __name__ == "__main__":
    main()
