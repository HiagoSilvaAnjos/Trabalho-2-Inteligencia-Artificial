# Análise do Projeto — GRASP & Algoritmo Genético (8-Rainhas)

---

## 1. FUNDAMENTAÇÃO — Como pode ser elaborada?

O projeto **já possui** uma base conceitual implícita na estrutura dos algoritmos e do README, mas a fundamentação formal para o relatório deve ser explicitada. Veja como cada ponto se sustenta:

### Problemas de Otimização e Metaheurísticas
O **Problema das 8-Rainhas** é um problema clássico de satisfação de restrições com espaço de busca de 8⁸ = 16.777.216 configurações possíveis (representação vetorial sem restrição de linha) ou 8! = 40.320 (permutações). A busca exaustiva é inviável para variantes maiores; metaheurísticas são a solução natural.

### Formulação formal que o projeto usa:
| Elemento | Definição no projeto |
|---|---|
| **Representação do estado** | Vetor `s = [s₀, s₁, ..., s₇]`, onde `sᵢ ∈ {0,...,7}` é a linha da rainha na coluna `i` |
| **Função objetivo (custo)** | `h(s) = nº de pares de rainhas em conflito` (mesma linha ou diagonal) |
| **Valor ótimo** | `h(s*) = 0` — nenhum par em conflito |
| **Espaço de busca** | 8⁸ = ~16,7 milhões de estados (GRASP) / 2²⁴ = 16.777.216 cromossomos binários (AG) |
| **Critério de parada** | `max_iter` atingido **ou** `h = 0` encontrado (ambos os algoritmos) |

### O que adicionar ao relatório para fortalecer a fundamentação:
- Citar a definição matemática de metaheurísticas (Glover, 1986; Blum & Roli, 2003).
- Mostrar o grafo de vizinhança: estado `s'` é vizinho de `s` se difere em exatamente um elemento `sᵢ`.
- Citar o número de soluções ótimas conhecidas para 8-rainhas: **92 soluções distintas** (12 fundamentais).
- Incluir o fluxograma geral da solução.

---

## 2. MODELAGEM DO PROBLEMA — Como foi feita?

A modelagem está **completamente correta e alinhada** com a especificação do professor:

| Critério exigido | Status | Como foi feito |
|---|---|---|
| Representação como vetor de 8 posições | ✅ | `estado = [s₀,...,s₇]`, índice = coluna, valor = linha |
| Função objetivo = minimizar conflitos | ✅ | `calcular_conflitos()` conta pares `(i,j)` com mesma linha ou diagonal |
| Função de custo | ✅ | `custo_incremental()` no GRASP calcula conflitos de forma incremental por coluna |
| Espaço de busca descrito | ✅ | Implícito no código (8⁸ estados) |
| Critério de parada | ✅ | `h = 0` ou `max_iter`/`max_geracoes` atingido |

> [!NOTE]
> Para o relatório, é recomendado formalizar com equação: `h(s) = Σᵢ<ⱼ [sᵢ=sⱼ ∨ |sᵢ-sⱼ|=|i-j|]` e mostrar o fluxograma.

---

## 3. IMPLEMENTAÇÃO DO GRASP — Análise de Conformidade

### ✅ O que está implementado e correto:

| Componente exigido | Implementado em | Descrição |
|---|---|---|
| Fase gulosa randomizada | `construir_solucao_gulosa_randomizada()` | Para cada coluna, calcula custo incremental de todas as linhas candidatas |
| Lista Restrita de Candidatos (RCL) | Mesma função, linha `rcl = [...]` | RCL por qualidade: candidatos com custo ≤ custo_min + α×(custo_max - custo_min) |
| Aleatoriedade controlada por α | Parâmetro `alpha=0.3` | α=0 → guloso puro; α=1 → aleatório puro |
| Busca local | `busca_local()` | Hill Climbing Steepest Ascent: explora toda a vizinhança e escolhe o melhor movimento |
| Critério de parada | `executar_grasp()` | Máximo de `max_iter=1000` iterações **ou** `h=0` |

### Como a solução inicial é construída:
A construção é **coluna por coluna** (posição 0 a 7). Para cada coluna, avalia-se o custo incremental de posicionar a rainha em cada uma das 8 linhas possíveis. Os candidatos com custo dentro do limiar α formam a RCL, e sorteia-se aleatoriamente entre eles.

### Como ocorre a aleatoriedade:
- O parâmetro `alpha = 0.3` cria uma RCL que aceita candidatos até 30% acima do mínimo.
- Se custo_min = custo_max, todos os candidatos entram na RCL (equivale a α=1).
- A escolha dentro da RCL é uniforme aleatória via `random.choice(rcl)`.

### Como a busca local melhora a solução:
O **Steepest Ascent Hill Climbing** varre toda a vizinhança de primeiro aprimoramento: testa trocar a rainha de cada coluna para cada linha alternativa (56 vizinhos possíveis por iteração). Move-se para o vizinho de menor `h`. Para se `h` não decrescer (ótimo local).

### Resultados observados (50 execuções):
- **Taxa de sucesso: 100%** (50/50 encontraram h=0)
- Média de iterações: **4.2 ± 3.34**
- Tempo médio: **1.41 ± 1.24 ms**
- Extremamente rápido e 100% confiável

### Vantagens e limitações:
| Vantagens | Limitações |
|---|---|
| Convergência muito rápida | Depende do parâmetro α (sensível à escolha) |
| 100% taxa de sucesso | Pode estagnar em ótimos locais se α muito baixo |
| Tempo < 6ms mesmo no pior caso | Aleatoriedade não garante diversidade máxima |
| Fácil de implementar | Sem memória entre iterações (é reiniciado a cada iter) |

---

## 4. IMPLEMENTAÇÃO DO ALGORITMO GENÉTICO — Análise de Conformidade

### ✅ O que está implementado e correto:

| Critério do professor | Status | Implementação |
|---|---|---|
| Codificação binária | ✅ | 24 bits (8 rainhas × 3 bits cada); `codificar()` e `decodificar()` |
| Tamanho da população: 20 indivíduos | ⚠️ | **Implementado com 100** (o padrão do CLI é 100, não 20 como especificado) |
| Seleção por roleta | ✅ | `selecionar_roleta()` — probabilidade proporcional ao fitness |
| Cruzamento ponto de corte | ✅ | `cruzar()` — único ponto de corte aleatório em [1, 23] |
| Taxa de cruzamento: 80% | ✅ | `TAXA_CRUZAMENTO = 0.80` |
| Mutação bit flip | ✅ | `mutar()` — cada bit tem 3% de chance de inversão |
| Taxa de mutação: 3% | ✅ | `TAXA_MUTACAO = 0.03` |
| Elitismo | ✅ | O melhor indivíduo sempre é copiado para a nova população sem alterações |
| Max. gerações: 1000 | ✅ | `--max_geracoes 1000` |
| Parada antecipada | ✅ | Ao detectar `fitness == 28` (h=0) |

> [!WARNING]
> **Divergência**: O professor especificou **tamanho de população = 20**, mas o código usa `TAMANHO_POPULACAO = 100` como padrão (linha 17 e argumento CLI `--tamanho_populacao 100`). Verifique com o professor ou ajuste o padrão para 20.

### Como a codificação binária foi usada:
Cada rainha ocupa 3 bits (pois `ceil(log₂(8)) = 3`). Um indivíduo = cromossomo de 24 bits. Exemplo: estado `[3,5,0,...]` → `[0,1,1, 1,0,1, 0,0,0, ...]`. Valores > 7 são mapeados com `% 8` ao decodificar, garantindo sempre um estado válido.

### Função fitness:
`fitness = 28 - h(s)`, onde 28 = C(8,2) é o número máximo de pares. fitness=28 → solução ótima. Isso transforma a minimização em maximização para a roleta.

### Seleção por roleta:
Sorteia um ponto aleatório entre 0 e `soma_fitness`. Percorre a população acumulando fitness até ultrapassar o ponto. Indivíduos com maior fitness têm fatia maior na roleta e maior chance de seleção.

### Cruzamento:
Ponto de corte sortado em [1,23]. Filho1 = primeiros `k` bits do pai1 + bits [k:] do pai2. Filho2 = inverso. A taxa de 80% é verificada antes: com 20% de chance, os filhos são cópias dos pais.

### Mutação:
Para cada um dos 24 bits do cromossomo, sorteia [0,1]. Se < 0.03, inverte o bit. Operação in-place sobre cópia.

### Elitismo:
O melhor indivíduo da geração anterior é sempre o primeiro inserido na nova população, garantindo que a melhor solução nunca se perde.

### Resultados observados (50 execuções):
- **Taxa de sucesso: 88%** (44/50)
- 6 execuções atingiram max_geracoes=1000 sem encontrar h=0
- Média de gerações: **437.76 ± 342.12**
- Tempo médio: **592.29 ± 462.57 ms**

---

## 5. AUTOMAÇÃO COM N8N — Documentação no README

### ✅ O README documenta completamente a automação n8n:

| Requisito da Parte 4 | Status | Onde no README |
|---|---|---|
| Receber parâmetros de execução | ✅ | Seção "COMO RODAR O PROJETO" → Passo 6 |
| Executar automaticamente os algoritmos | ✅ | Seção "O Pipeline de Dados" — execução paralela via HTTP |
| Registrar resultados | ✅ | Seção "COMPORTAMENTO DOS NÓS DO WORKFLOW" |
| Armazenar em formato estruturado (CSV/JSON) | ✅ | CSV + JSON (metricas_gemini.json) documentados na estrutura |
| algoritmo utilizado | ✅ | Campo `algoritmo` no JSON retornado por cada rota |
| tempo de execução | ✅ | Campo `tempo_ms` em cada CSV |
| número de iterações/gerações | ✅ | Campos `iteracoes`/`geracao_parada` nos CSVs |
| melhor solução encontrada | ✅ | Campo `estado_final` nos CSVs |
| valor final da função objetivo | ✅ | Campo `h_final` nos CSVs |
| indicação de sucesso ou falha | ✅ | Campo `sucesso` (True/False) nos CSVs |

> [!NOTE]
> O workflow JSON (`Trabalho2_n8n_workflow.json`) contém 8 nós completos e está exportável/importável diretamente no n8n. O README documenta cada nó na tabela "O COMPORTAMENTO DOS NÓS DO WORKFLOW".

> [!WARNING]
> **Atenção**: O workflow é configurado como sequencial (não paralelo). O README menciona "execução paralela" mas as conexões no JSON mostram: Iniciar → GRASP → AG → Unir → Gemini → Salvar → Gráficos → Resultado (sequencial). Verifique se isso é intencional.

---

## 6. ANÁLISE EXPERIMENTAL — Novos Gráficos e Tabelas

O script [`analisar_comparativo.py`](file:///c:/Users/Edivaldo/Documents/GitHub/Trabalho-2-Inteligencia-Artificial/codigo/analisar_comparativo.py) foi expandido de **4 gráficos + 2 tabelas** para **10 gráficos + 5 tabelas**.

### Gráficos (10 no total):

| # | Arquivo | Tipo | O que mostra | Critério do professor atendido |
|---|---|---|---|---|
| 1 | `comp_grafico1_taxa_sucesso.png` | Barras empilhadas | Sucesso **e** falha por algoritmo | Taxa de sucesso |
| 2 | `comp_grafico2_tempo_execucao.png` | Barras com erro | Tempo médio ± desvio padrão | Média e desvio do tempo |
| 3 | `comp_grafico3_iteracoes_geracoes.png` | Boxplot | Distribuição completa de iterações/gerações | Média, desvio, outliers |
| 4 | `comp_grafico4_hfinal_execucoes.png` | Linhas | h_final ao longo das 50 execuções | Comportamento em diferentes execuções |
| 5 | `comp_grafico5_distribuicao_tempo.png` | Histograma duplo | Distribuição do tempo por algoritmo (com média e mediana) | Estabilidade, velocidade |
| 6 | `comp_grafico6_scatter_tempo_iter.png` | Dispersão | Relação entre iterações e tempo (sucessos vs falhas) | Custo computacional, qualidade |
| 7 | `comp_grafico7_histograma_hfinal.png` | Barras agrupadas | Frequência de cada valor de h_final | Qualidade das soluções |
| 8 | `comp_grafico8_convergencia_acumulada.png` | Linhas acumuladas | Evolução do total de sucessos ao longo das execuções | Estabilidade, taxa de sucesso |
| 9 | `comp_grafico9_violin_tempo.png` | Violin Plot | Distribuição do tempo (densidade completa) | Influência da aleatoriedade |
| 10 | `comp_grafico10_radar_comparativo.png` | Radar/Spider | Comparação multidimensional normalizada | Comparação geral entre algoritmos |

### Tabelas (5 no total):

| # | Arquivo | O que contém | Critério atendido |
|---|---|---|---|
| 1 | `comp_tabela_resumo_estatistico.png` | Todas as métricas: n, sucessos, falhas, média/desvio iter/tempo/h | Todos os requisitos estatísticos |
| 2 | `comp_tabela_top5_ag.png` | Top 5 soluções distintas do AG com estado, fitness, geração, tempo | Exigência explícita da Parte 3 |
| 3 | `comp_tabela_top5_grasp.png` | Top 5 soluções distintas do GRASP com estado, iterações, alpha, tempo | Comparabilidade |
| 4 | `comp_tabela_percentis.png` | P0, P10, P25, P50, P75, P90, P100 de iterações e tempo | Distribuição detalhada |
| 5 | `comp_tabela_analise_qualidade.png` | Coeficiente de variação, estabilidade, indicador do melhor algoritmo | Estabilidade, eficiência |

---

## 7. RESULTADOS CONSOLIDADOS (Dados Reais — 50 execuções cada)

| Métrica | GRASP | AG |
|---|---|---|
| Taxa de sucesso | **100%** | 88% |
| Média iterações/gerações | **4.2** | 437.76 |
| Desvio padrão iter/ger | **3.34** | 342.12 |
| Tempo médio (ms) | **1.41** | 592.29 |
| Desvio padrão tempo | **1.24** | 462.57 |
| Mínimo tempo (ms) | **0.06** | 20.59 |
| Máximo tempo (ms) | **5.61** | 1355.28 |
| Média h_final | **0.0000** | 0.1200 |

### Interpretação:
- O **GRASP** é **superior em todos os indicadores** para este problema: 420× mais rápido, 100% de sucesso vs 88% do AG.
- O **AG** apresenta **alta variabilidade** (CV de gerações ≈ 78%), indicando forte influência da aleatoriedade na inicialização.
- O GRASP se beneficia da **construção gulosa-randomizada** que já parte de soluções de alta qualidade antes da busca local.
- O AG sofre com a representação binária: a decodificação com `% 8` pode gerar muitos indivíduos equivalentes inicialmente ruins.
