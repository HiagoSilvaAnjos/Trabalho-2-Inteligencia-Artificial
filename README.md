# Automação de IA: GRASP e Algoritmo Genético (8-Rainhas) + n8n

Este projeto implementa uma solução completa e automatizada para o problema das **8-Rainhas** utilizando dois algoritmos metaheurísticos: **GRASP** (Greedy Randomized Adaptive Search Procedure) e **Algoritmo Genético com codificação binária**. Toda a orquestração do experimento, análise comparativa e geração de relatórios visuais é feita de forma integrada através do **n8n**, da inteligência do **Google Gemini** e de uma **API Flask em Python**.

---

## A ARQUITETURA DO SISTEMA

O sistema foi arquitetado em um formato de **Microsserviços**.

O n8n opera como o controlador central da integração, enquanto a API Python atua como a camada de processamento, detendo permissões de acesso integral ao sistema de arquivos local.

### O Pipeline de Dados:

1. **Execução paralela:** O n8n aciona simultaneamente duas rotas — `/executar-grasp` e `/executar-genetico`. Cada uma executa o respectivo algoritmo **50 vezes**, salva o histórico bruto em `.csv` e devolve um JSON encapsulado.

2. **Merge de resultados:** Um nó *Code* no n8n une os dados dos dois algoritmos em um único objeto JSON para envio ao Gemini.

3. **Análise IA comparativa:** O n8n envia o JSON combinado para a API do **Google Gemini**, que analisa tempos de execução, iterações/gerações, taxas de sucesso e extrai as 5 melhores soluções do AG — gerando uma categorização textual detalhada para ambos os algoritmos.

4. **Persistência de Métricas:** O n8n devolve a resposta do Gemini para a API Python, que converte para JSON estruturado e salva em `metricas_gemini.json`.

5. **Relatórios Visuais:** O n8n aciona `/gerar-graficos`, que dispara o `analisar_comparativo.py`. Esse script produz 10 gráficos e 5 tabelas comparativas detalhadas (GRASP vs AG) em `.png`.

---

## ESTRUTURA DO PROJETO

```text
Trabalho-IA - 2/
│
├── api_projeto.py               # API Flask Principal
├── README.md                    # Este arquivo de documentação
│
├── codigo/                      # Scripts de algoritmos e análise
│   ├── grasp.py                 # Algoritmo GRASP (construção + busca local)
│   ├── algoritmo_genetico.py    # Algoritmo Genético com codificação binária
│   └── analisar_comparativo.py  # Gráficos e tabelas comparativas GRASP vs AG
│
├── resultados/                  # Diretório de saída (gerado dinamicamente)
│   ├── execucoes_grasp.csv                  # Histórico das 50 execuções do GRASP
│   ├── execucoes_genetico.csv               # Histórico das 50 execuções do AG
│   ├── metricas_gemini.json                 # Análise estruturada do Google Gemini
│   ├── comp_grafico1_taxa_sucesso.png       # Barras: Taxa de sucesso e falha
│   ├── comp_grafico2_tempo_execucao.png     # Barras com erro: Tempo médio ± desvio
│   ├── comp_grafico3_iteracoes_geracoes.png # Boxplot: Iterações vs Gerações
│   ├── comp_grafico4_hfinal_execucoes.png   # Linha: h_final por execução
│   ├── comp_grafico5_distribuicao_tempo.png # Histograma duplo de tempo
│   ├── comp_grafico6_scatter_tempo_iter.png # Dispersão: Tempo x Iterações
│   ├── comp_grafico7_histograma_hfinal.png  # Frequência de conflitos finais
│   ├── comp_grafico8_convergencia_acumulada.png # Sucessos acumulados
│   ├── comp_grafico9_violin_tempo.png       # Densidade completa do tempo
│   ├── comp_grafico10_radar_comparativo.png # Comparação multidimensional
│   ├── comp_tabela_resumo_estatistico.png   # Tabela comparativa completa
│   ├── comp_tabela_top5_ag.png              # Top 5 soluções distintas do AG
│   ├── comp_tabela_top5_grasp.png           # Top 5 soluções distintas do GRASP
│   ├── comp_tabela_percentis.png            # Percentis de iter. e tempo (P0-P100)
│   └── comp_tabela_analise_qualidade.png    # Estabilidade e coef. de variação
│
└── workflow/                    # Arquivo de exportação do n8n
    └── Trabalho2_n8n_workflow.json  # Fluxo completo do Trabalho 2
```

---

## PRÉ-REQUISITOS DO SISTEMA

1. **Python 3.8+** instalado.
2. **n8n** instalado (App Desktop, Docker ou `npx n8n`).
3. **Chave de API do Google Gemini** (gratuita no Google AI Studio).

---

## COMO RODAR O PROJETO

Siga estas instruções cronologicamente para garantir o sucesso na execução do pipeline.

### PASSO 1: Instalação das Bibliotecas

Abra um terminal na raiz do projeto e instale todas as dependências exigidas:

```bash
pip install flask pandas matplotlib numpy
```

### PASSO 2: Iniciar a API

No mesmo terminal, inicie o servidor Flask:

```bash
python api_projeto.py
```

> **Atenção:** Mantenha este terminal aberto. Ele escutará as requisições na porta `5000` (`http://127.0.0.1:5000`). Sem isso, o n8n não conseguirá se comunicar com os algoritmos.

### PASSO 3: Iniciar o n8n

Abra um novo terminal e execute:

```bash
n8n start
```

> Caso o n8n não esteja instalado globalmente, instale com `npm install -g n8n`.

### PASSO 4: Importar o Workflow no n8n

1. Acesse a interface web do n8n (normalmente `http://localhost:5678`).
2. Faça login ou cadastro na plataforma.
3. Clique em **Add Workflow** > **Import from File**.
4. Selecione o arquivo `Trabalho2_n8n_workflow.json` da pasta `workflow/`.

### PASSO 5: Configurar a Chave da API do Gemini

1. No fluxo importado, clique no nó **"Análise Gemini (Comparativa)"**.
2. Na aba de parâmetros, localize o campo **URL**.
3. Substitua `SUA_CHAVE_AQUI` pela sua chave de API do Google Gemini (ex: `...?key=AIzaSy...`).
4. Salve o fluxo.

### PASSO 6: Execução do Pipeline

1. Clique em **Execute Workflow** (ou *Test Workflow*).

2. O sistema percorrerá as seguintes etapas automaticamente:
   - Acionará **paralelamente** `/executar-grasp` e `/executar-genetico` (50 execuções cada).
   - Unirá os resultados no nó **Unir Resultados**.
   - Enviará os dados combinados ao **Google Gemini** para análise comparativa.
   - Acionará `/salvar-metricas` para persistir o JSON do Gemini.
   - Acionará `/gerar-graficos` para gerar todos os gráficos e tabelas comparativas.

3. Quando todos os nós exibirem sinal verde, abra a pasta `resultados/`. Lá estarão os gráficos PNG e o JSON de métricas do experimento.

---

## DETALHES DOS ALGORITMOS

### GRASP (`grasp.py`)

| Parâmetro | Valor padrão | Descrição |
|---|---|---|
| `--num_execucoes` | 50 | Execuções independentes |
| `--max_iter` | 1000 | Máximo de iterações (construção + busca local) |
| `--alpha` | 0.3 | Parâmetro da RCL (0 = guloso, 1 = aleatório) |

**Fase construtiva:** Para cada coluna, calcula o custo incremental de posicionar a rainha em cada linha, monta a **Lista Restrita de Candidatos (RCL)** por qualidade (`custo ≤ custo_min + α × (custo_max − custo_min)`) e sorteia uma posição da RCL aleatoriamente.

**Fase de busca local:** Aplica Hill Climbing *Steepest Ascent* à solução construída até atingir ótimo local ou h=0.

**Critério de parada:** Número máximo de iterações atingido ou h_final = 0 (solução perfeita).

---

### Algoritmo Genético (`algoritmo_genetico.py`)

| Parâmetro | Valor | Descrição |
|---|---|---|
| Codificação | Binária (24 bits) | 8 rainhas × 3 bits cada |
| Fitness | 28 − conflitos | Máximo = 28 (zero conflitos) |
| Seleção | Roleta | Proporcional ao fitness |
| Cruzamento | Ponto único | Taxa: **80%** |
| Mutação | Bit flip | Taxa: **3% por bit** |
| Elitismo | Sim | Melhor indivíduo sempre preservado |
| `--max_geracoes` | 1000 | Critério de parada por gerações |
| `--tamanho_populacao` | 100 | Indivíduos por geração |

---

## O COMPORTAMENTO DOS NÓS DO WORKFLOW

| Nó | Tipo | O que faz |
|---|---|---|
| **Iniciar Experimento** | Manual Trigger | Botão de início do pipeline |
| **GRASP (50 execuções)** | HTTP Request | `POST /executar-grasp` — executa o GRASP 50 vezes e salva `execucoes_grasp.csv` |
| **Algoritmo Genético (50 execuções)** | HTTP Request | `POST /executar-genetico` — executa o AG 50 vezes e salva `execucoes_genetico.csv` |
| **Unir Resultados** | Code | Merge dos JSONs dos dois algoritmos em um único objeto |
| **Análise Gemini (Comparativa)** | HTTP Request | `POST` à API Gemini com os dados dos dois algoritmos para análise comparativa |
| **Salvar Métricas Gemini** | HTTP Request | `POST /salvar-metricas` — persiste o JSON do Gemini em disco |
| **Gerar Gráficos e Tabelas** | HTTP Request | `POST /gerar-graficos` — dispara `analisar_comparativo.py` |
| **Resultado Final** | Code | Consolida o status e lista os arquivos gerados |

---

## ROTAS DA API FLASK

| Rota | Método | Descrição |
|---|---|---|
| `/executar-grasp` | POST | Executa o GRASP (parâmetros configuráveis no corpo JSON) |
| `/executar-genetico` | POST | Executa o AG (parâmetros configuráveis no corpo JSON) |
| `/gerar-graficos` | POST | Gera todos os gráficos e tabelas comparativas |
| `/salvar-metricas` | POST | Salva o JSON retornado pelo Gemini em `metricas_gemini.json` |