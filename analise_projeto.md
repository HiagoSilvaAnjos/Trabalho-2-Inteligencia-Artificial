# Análise do Projeto — GRASP & Algoritmo Genético (8-Rainhas)

---
> **Dados atuais:** Esta análise usa exclusivamente os resultados presentes nos CSVs da pasta `resultados/` gerados pela última execução do workflow n8n. GRASP: alpha=0.3, max_iter=1000. AG: população=**20**, max_geracoes=1000.

---

## 1. FUNDAMENTAÇÃO — Como pode ser elaborada?

O projeto possui uma base conceitual sólida implementada nos algoritmos e documentada no README. Para o relatório formal, os seguintes pontos devem ser explicitados:

### Problemas de Otimização e Metaheurísticas
O **Problema das 8-Rainhas** é um problema clássico de satisfação de restrições com espaço de busca de 8⁸ = 16.777.216 configurações possíveis (representação vetorial sem restrição de linha única por linha). A busca exaustiva é computacionalmente cara para variantes maiores; metaheurísticas buscam boas soluções em tempo viável sem garantia de ótimo global.

### Formulação formal usada no projeto:
| Elemento | Definição no projeto |
|---|---|
| **Representação do estado** | Vetor `s = [s₀, s₁, ..., s₇]`, onde `sᵢ ∈ {0,...,7}` é a linha da rainha na coluna `i` |
| **Função objetivo (custo)** | `h(s) = nº de pares de rainhas em conflito` (mesma linha ou diagonal) |
| **Valor ótimo** | `h(s*) = 0` — nenhum par em conflito |
| **Espaço de busca** | 8⁸ ≈ 16,7 milhões de estados (GRASP) / 2²⁴ = 16.777.216 cromossomos binários (AG) |
| **Critério de parada** | `max_iter`/`max_geracoes` atingido **ou** `h = 0` encontrado |

### Para fortalecer a fundamentação no relatório:
- Citar a definição de metaheurísticas (Glover, 1986; Blum & Roli, 2003).
- Mostrar o grafo de vizinhança: estado `s'` é vizinho de `s` se difere em exatamente um elemento `sᵢ`.
- Destacar que existem **92 soluções distintas** para o problema das 8-rainhas (12 fundamentais).
- Incluir o fluxograma geral da solução com as duas fases do GRASP e o ciclo evolutivo do AG.
- Formalizar a função objetivo: `h(s) = Σᵢ<ⱼ [sᵢ=sⱼ ∨ |sᵢ-sⱼ|=|i-j|]`

---

## 2. MODELAGEM DO PROBLEMA — Como foi feita?

A modelagem está **completamente correta e alinhada** com a especificação do professor:

| Critério exigido | Status | Como foi feito |
|---|---|---|
| Representação como vetor de 8 posições | ✅ | `estado = [s₀,...,s₇]`, índice = coluna, valor = linha |
| Função objetivo = minimizar conflitos | ✅ | `calcular_conflitos()` conta pares `(i,j)` com mesma linha ou diagonal |
| Função de custo incremental | ✅ | `custo_incremental()` no GRASP calcula conflitos de forma incremental por coluna |
| Espaço de busca | ✅ | 8⁸ estados (GRASP) e 2²⁴ cromossomos (AG) |
| Critério de parada | ✅ | `h = 0` ou `max_iter`/`max_geracoes` atingido |

---

## 3. IMPLEMENTAÇÃO DO GRASP — Análise de Conformidade

### ✅ Todos os componentes exigidos estão implementados:

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
- `alpha = 0.3` aceita candidatos com custo até 30% acima do mínimo observado.
- Se custo_min = custo_max, todos os candidatos entram na RCL (equivale a α=1 nessa coluna).
- A escolha dentro da RCL é uniforme aleatória via `random.choice(rcl)`.

### Como a busca local melhora a solução:
O **Steepest Ascent Hill Climbing** testa trocar a rainha de cada coluna para cada linha alternativa (56 movimentos possíveis por iteração). Move-se para o vizinho com menor `h`. Para quando `h` não decresce (ótimo local atingido) ou quando `h = 0`.

### Resultados reais — última execução (50 execuções, alpha=0.3):

| Métrica | Valor |
|---|---|
| Taxa de sucesso | **100%** (50/50) |
| Falhas | **0** |
| Média de iterações GRASP | **5.04** |
| Desvio padrão iterações | **5.55** |
| Mínimo de iterações | **1** |
| Máximo de iterações | **37** |
| Q1 / Mediana / Q3 iterações | 2.0 / 4.0 / 6.0 |
| Tempo médio (ms) | **0.91** |
| Desvio padrão tempo (ms) | **1.03** |
| Mínimo tempo (ms) | **0.03** |
| Máximo tempo (ms) | **6.54** |
| Q1 / Mediana / Q3 tempo (ms) | 0.32 / 0.65 / 1.23 |
| Média h_final | **0.0000** |

### Top 5 soluções distintas encontradas pelo GRASP:

| Rank | Estado Final | h_final | Iterações | Tempo (ms) |
|---|---|---|---|---|
| #1 | `[3, 6, 4, 2, 0, 5, 7, 1]` | 0 | 1 | 0.03 |
| #2 | `[3, 1, 6, 2, 5, 7, 0, 4]` | 0 | 1 | 0.03 |
| #3 | `[3, 0, 4, 7, 5, 2, 6, 1]` | 0 | 1 | 0.04 |
| #4 | `[2, 5, 1, 6, 0, 3, 7, 4]` | 0 | 1 | 0.04 |
| #5 | `[4, 1, 5, 0, 6, 3, 7, 2]` | 0 | 1 | 0.04 |

### Vantagens e limitações:
| Vantagens | Limitações |
|---|---|
| **100% de taxa de sucesso** | Depende do parâmetro α (sensível à calibração) |
| Convergência rápida (< 7ms no pior caso) | Pode estagnar em ótimos locais se α muito baixo |
| Baixíssima variabilidade de tempo | Sem memória entre iterações (reinicia a cada iter) |
| Fácil implementação e interpretação | Aleatoriedade não garante cobertura uniforme do espaço |

---

## 4. IMPLEMENTAÇÃO DO ALGORITMO GENÉTICO — Análise de Conformidade

### ✅ Todos os parâmetros exigidos implementados e corrigidos:

| Critério do professor | Status | Implementação |
|---|---|---|
| Codificação binária | ✅ | 24 bits (8 rainhas × 3 bits cada); `codificar()` e `decodificar()` |
| Tamanho da população: **20** indivíduos | ✅ | `TAMANHO_POPULACAO = 20` no código, padrão 20 na API e no n8n |
| Seleção por roleta | ✅ | `selecionar_roleta()` — probabilidade proporcional ao fitness |
| Cruzamento ponto de corte | ✅ | `cruzar()` — único ponto de corte aleatório em [1, 23] |
| Taxa de cruzamento: 80% | ✅ | `TAXA_CRUZAMENTO = 0.80` |
| Mutação bit flip | ✅ | `mutar()` — cada bit tem 3% de chance de inversão |
| Taxa de mutação: 3% | ✅ | `TAXA_MUTACAO = 0.03` |
| Elitismo | ✅ | O melhor indivíduo sempre é copiado para a nova população sem modificações |
| Max. gerações: 1000 | ✅ | `--max_geracoes 1000` |
| Parada antecipada | ✅ | Ao detectar `fitness == 28` (h=0), para imediatamente |

### Como a codificação binária foi usada:
Cada rainha ocupa 3 bits (`ceil(log₂(8)) = 3`). Cromossomo = 24 bits. Exemplo: estado `[3,5,0,...]` → `[0,1,1, 1,0,1, 0,0,0, ...]`. Valores > 7 mapeados com `% 8` ao decodificar.

### Função fitness:
`fitness = 28 - h(s)`, onde 28 = C(8,2). fitness=28 → h=0 → solução ótima. A fórmula converte minimização de conflitos em maximização para a roleta.

### Seleção por roleta:
Sorteia ponto em [0, soma_fitness]. Percorre acumulando fitness até ultrapassar o ponto. Indivíduos com maior fitness têm maior fatia e maior chance de seleção.

### Cruzamento:
Ponto de corte em [1,23]. Filho1 = bits[0:k] do pai1 + bits[k:] do pai2. Filho2 = inverso. Com 20% de probabilidade, filhos são cópias diretas dos pais.

### Mutação:
Para cada um dos 24 bits: se `random() < 0.03`, inverte o bit.

### Elitismo:
O melhor indivíduo da geração anterior é inserido na posição 0 da nova população, garantindo monotonicidade crescente do melhor fitness.

### Resultados reais — última execução (50 execuções, população=20):

| Métrica | Valor |
|---|---|
| Taxa de sucesso | **56%** (28/50) |
| Falhas (atingiram 1000 gerações sem h=0) | **22** execuções |
| Média de gerações | **620.06** |
| Desvio padrão gerações | **382.75** |
| Mínimo de gerações | **21** |
| Máximo de gerações | **1000** |
| Q1 / Mediana / Q3 gerações | 202.5 / 643.0 / 1000.0 |
| Tempo médio (ms) | **134.45** |
| Desvio padrão tempo (ms) | **117.19** |
| Mínimo tempo (ms) | **2.73** |
| Máximo tempo (ms) | **475.75** |
| Q1 / Mediana / Q3 tempo (ms) | 43.99 / 124.62 / 149.95 |
| Média h_final | **0.44** |
| Média fitness_final | **27.56** |
| Tamanho da população | **20** |

> **Impacto da população=20:** Com população menor há menos diversidade genética, aumentando o risco de convergência prematura para ótimos locais. A taxa de sucesso de 56% (vs ~88% com pop=100 e ~100% do GRASP) deve ser discutida criticamente no relatório como evidência do impacto do tamanho da população na exploração do espaço de busca.

### Top 5 soluções distintas encontradas pelo AG:

| Rank | Estado Final | h_final | Fitness | Geração | Tempo (ms) |
|---|---|---|---|---|---|
| #1 | `[3, 1, 4, 7, 5, 0, 2, 6]` | 0 | 28 | 21 | 2.73 |
| #2 | `[6, 4, 2, 0, 5, 7, 1, 3]` | 0 | 28 | 62 | 7.45 |
| #3 | `[4, 2, 0, 6, 1, 7, 5, 3]` | 0 | 28 | 77 | 9.08 |
| #4 | `[6, 3, 1, 7, 5, 0, 2, 4]` | 0 | 28 | 64 | 9.33 |
| #5 | `[3, 5, 7, 2, 0, 6, 4, 1]` | 0 | 28 | 66 | 9.85 |

---

## 5. AUTOMAÇÃO COM N8N — Documentação e Status

### ✅ O README documenta completamente a automação n8n:

| Requisito da Parte 4 | Status | Onde no projeto |
|---|---|---|
| Receber parâmetros de execução | ✅ | Passo 6 do README + corpo JSON dos nós HTTP no workflow |
| Executar automaticamente os algoritmos | ✅ | Nós "GRASP (50 execuções)" e "AG (50 execuções)" |
| Registrar resultados | ✅ | Nó "Unir Resultados" + nó "Resultado Final" |
| Armazenar em CSV | ✅ | `execucoes_grasp.csv` e `execucoes_genetico.csv` em `resultados/` |
| Armazenar em JSON | ✅ | `metricas_gemini.json` em `resultados/` |
| Algoritmo utilizado | ✅ | Campo `algoritmo` no JSON de retorno de cada rota Flask |
| Tempo de execução | ✅ | Campo `tempo_ms` em cada CSV |
| Número de iterações/gerações | ✅ | Campos `iteracoes` e `geracao_parada` nos CSVs |
| Melhor solução encontrada | ✅ | Campo `estado_final` nos CSVs |
| Valor final da função objetivo | ✅ | Campo `h_final` nos CSVs |
| Indicação de sucesso ou falha | ✅ | Campo `sucesso` (True/False) nos CSVs |

> **Pipeline é sequencial:** O workflow executa os algoritmos em sequência — GRASP → AG → Unir → Gemini → Salvar → Gráficos — não em paralelo como mencionava a versão antiga do README. Isso já foi corrigido no README atual.

> **Prompt do Gemini atualizado:** O workflow agora solicita ao Gemini o Top 5 de soluções **tanto do GRASP quanto do AG**, além das métricas e categorizações das 50 execuções de cada algoritmo.

---

## 6. ANÁLISE EXPERIMENTAL — Gráficos e Tabelas

O script [`analisar_comparativo.py`](file:///c:/Users/Edivaldo/Documents/GitHub/Trabalho-2-Inteligencia-Artificial/codigo/analisar_comparativo.py) gera **10 gráficos e 5 tabelas**, cobrindo todos os critérios de análise experimental exigidos.

### Gráficos (10):

| # | Arquivo | Tipo | O que mostra | Critério atendido |
|---|---|---|---|---|
| 1 | `comp_grafico1_taxa_sucesso.png` | Barras empilhadas | Sucesso **e** falha por algoritmo | Taxa de sucesso |
| 2 | `comp_grafico2_tempo_execucao.png` | Barras com erro | Tempo médio ± desvio padrão | Média e desvio do tempo |
| 3 | `comp_grafico3_iteracoes_geracoes.png` | Boxplot com média | Distribuição completa de iter./gerações | Média, desvio, estabilidade |
| 4 | `comp_grafico4_hfinal_execucoes.png` | Linhas com referência | h_final por execução (linha h=0 destacada) | Comportamento por execução |
| 5 | `comp_grafico5_distribuicao_tempo.png` | Histograma duplo | Distribuição do tempo (com média e mediana) | Velocidade de convergência |
| 6 | `comp_grafico6_scatter_tempo_iter.png` | Dispersão | Iterações × Tempo, separando sucessos e falhas | Custo computacional, qualidade |
| 7 | `comp_grafico7_histograma_hfinal.png` | Barras agrupadas | Frequência de cada valor de h_final | Qualidade das soluções |
| 8 | `comp_grafico8_convergencia_acumulada.png` | Linhas acumuladas | Total de sucessos ao longo das execuções | Estabilidade, taxa de sucesso |
| 9 | `comp_grafico9_violin_tempo.png` | Violin Plot | Distribuição completa do tempo (densidade) | Influência da aleatoriedade |
| 10 | `comp_grafico10_radar_comparativo.png` | Radar / Spider | Comparação multidimensional normalizada | Visão geral comparativa |

### Tabelas (5):

| # | Arquivo | O que contém | Critério atendido |
|---|---|---|---|
| 1 | `comp_tabela_resumo_estatistico.png` | n, sucessos, falhas, média/desvio iter/tempo/h | Todos os requisitos estatísticos básicos |
| 2 | `comp_tabela_top5_ag.png` | Top 5 soluções distintas do AG | Exigência explícita da Parte 3 |
| 3 | `comp_tabela_top5_grasp.png` | Top 5 soluções distintas do GRASP | Comparabilidade entre algoritmos |
| 4 | `comp_tabela_percentis.png` | P0, P10, P25, P50, P75, P90, P100 de iter. e tempo | Análise de distribuição detalhada |
| 5 | `comp_tabela_analise_qualidade.png` | Coef. de variação e indicador do melhor algoritmo por critério | Estabilidade e eficiência |

---

## 7. RESULTADOS CONSOLIDADOS — Dados Reais da Última Execução (50 execuções cada)

| Métrica | GRASP (alpha=0.3) | AG (pop=20) |
|---|---|---|
| **Taxa de sucesso** | **100%** (50/50) | **56%** (28/50) |
| Falhas | **0** | **22** |
| Média iterações/gerações | **5.04** | 620.06 |
| Desvio padrão iter/ger | **5.55** | 382.75 |
| Mínimo iterações/gerações | **1** | 21 |
| Máximo iterações/gerações | **37** | 1000 |
| Q1 / Mediana / Q3 iter/ger | 2.0 / 4.0 / 6.0 | 202.5 / 643.0 / 1000.0 |
| **Tempo médio (ms)** | **0.91** | 134.45 |
| Desvio padrão tempo (ms) | **1.03** | 117.19 |
| Mínimo tempo (ms) | **0.03** | 2.73 |
| Máximo tempo (ms) | **6.54** | 475.75 |
| Q1 / Mediana / Q3 tempo (ms) | 0.32 / 0.65 / 1.23 | 43.99 / 124.62 / 149.95 |
| **Média h_final** | **0.0000** | 0.4400 |
| Média fitness_final | — | 27.56 / 28.00 |

### Interpretação e discussão crítica:

**Estabilidade:** O GRASP demonstra alta estabilidade — 100% das execuções convergem em < 7ms. O AG com pop=20 apresenta altíssima variabilidade: coeficiente de variação das gerações ≈ 62% e do tempo ≈ 87%, evidenciando forte sensibilidade à aleatoriedade da população inicial.

**Velocidade de convergência:** O GRASP converge em média em apenas 5.04 iterações (cada iteração = 1 construção + busca local). O AG necessita de 620 gerações em média — e mesmo assim falha em 44% das execuções.

**Qualidade das soluções:** O GRASP obteve h=0 em 100% das execuções. O AG com pop=20 falhou em 22 das 50 execuções, restando com h=1 (um par de rainhas em conflito) — nunca com h>1 nas falhas, pois o elitismo garante preservação do melhor indivíduo.

**Influência da aleatoriedade e do tamanho da população:** A redução da população de 100 para 20 (conforme especificação) reduziu drasticamente a diversidade genética, aumentando convergência prematura. Com pop=20, 44% das execuções ficam presas em ótimos locais. Isso é esperado e pedagogicamente relevante.

**Custo computacional:** O GRASP é em média **148× mais rápido** que o AG com pop=20 (0.91ms vs 134.45ms). Com pop=100, o AG era ~650× mais lento.

**Conclusão geral:** Para o problema das 8-rainhas especificamente, o GRASP supera o AG em todos os indicadores medidos. Isso ocorre porque a construção guiada por informação de domínio (custo incremental) posiciona o GRASP muito próximo da solução ótima já na fase construtiva, deixando pouco trabalho para a busca local. O AG, por operar com representação binária e população pequena, tem dificuldade em explorar eficientemente o espaço de busca.
