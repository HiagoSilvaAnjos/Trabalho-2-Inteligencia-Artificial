"""
analisar_comparativo.py
-----------------------
Lê os CSVs de GRASP e Algoritmo Genético, gera gráficos e tabelas comparativas
entre os dois algoritmos para o problema das 8-rainhas.

Saídas geradas em resultados/:
  comp_grafico1_taxa_sucesso.png
  comp_grafico2_tempo_execucao.png
  comp_grafico3_iteracoes_geracoes.png
  comp_grafico4_evolucao_fitness.png
  comp_tabela_resumo_estatistico.png
  comp_tabela_top5_ag.png
"""

import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR    = os.path.join(BASE_DIR, "resultados")
CSV_GRASP  = os.path.join(OUT_DIR, "execucoes_grasp.csv")
CSV_AG     = os.path.join(OUT_DIR, "execucoes_genetico.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# ── Paleta Visual ─────────────────────────────────────────────────────────────
PALETTE = {
    "grasp":    "#1f77b4",   # Azul — GRASP
    "ag":       "#ff7f0e",   # Laranja — AG
    "sucesso":  "#2ca02c",   # Verde
    "falha":    "#d62728",   # Vermelho
    "grid":     "#e0e0e0",
    "bg":       "#ffffff",
    "text":     "#333333",
}

plt.style.use("default")


def apply_base_style(ax, title, xlabel="", ylabel=""):
    ax.set_facecolor(PALETTE["bg"])
    ax.set_title(title, color=PALETTE["text"], fontsize=14, fontweight="bold", pad=12)
    if xlabel: ax.set_xlabel(xlabel, color=PALETTE["text"], fontsize=11)
    if ylabel: ax.set_ylabel(ylabel, color=PALETTE["text"], fontsize=11)
    ax.tick_params(colors=PALETTE["text"])
    for spine in ["bottom", "left"]:
        ax.spines[spine].set_color(PALETTE["text"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=PALETTE["grid"], linestyle="--", alpha=0.7)


def render_table(fig_name, title, data, header_color="#1f77b4"):
    """Renderiza e salva uma tabela como imagem PNG."""
    n_rows = len(data)
    fig, ax = plt.subplots(figsize=(12, max(2, n_rows * 0.55)))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.axis("tight")
    ax.axis("off")

    table = ax.table(cellText=data, colLabels=None, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        if row == 0:
            cell.set_text_props(weight="bold", color="white")
            cell.set_facecolor(header_color)
        else:
            alt = "#f5f5f5" if row % 2 == 0 else "white"
            cell.set_facecolor(alt)
            cell.set_text_props(color=PALETTE["text"])

    plt.title(title, color=PALETTE["text"], fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, fig_name)
    plt.savefig(path, dpi=150, facecolor=PALETTE["bg"], bbox_inches="tight")
    plt.close()
    print(f"[OK] {fig_name} salvo.")


# ── Leitura dos CSVs ──────────────────────────────────────────────────────────
def carregar_csv(path, nome):
    if not os.path.exists(path):
        print(f"[AVISO] CSV do {nome} não encontrado em {path}. Pulando análise.")
        return None
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    # Normaliza booleanos
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].replace(
                {"True": True, "False": False, "true": True, "false": False}
            )
    return df


df_grasp = carregar_csv(CSV_GRASP, "GRASP")
df_ag    = carregar_csv(CSV_AG,    "Algoritmo Genético")

if df_grasp is None and df_ag is None:
    print("[ERRO] Nenhum CSV encontrado. Execute os algoritmos antes de gerar os gráficos.")
    sys.exit(1)


# ── Métricas por algoritmo ───────────────────────────────────────────────────
def metricas(df, iter_col, tempo_col, sucesso_col, h_col):
    n = len(df)
    sucessos = int(df[sucesso_col].sum())
    return {
        "n":              n,
        "sucessos":       sucessos,
        "taxa_sucesso":   round(sucessos / n * 100, 2) if n > 0 else 0,
        "media_iter":     round(df[iter_col].mean(), 2),
        "std_iter":       round(df[iter_col].std(), 2),
        "min_iter":       int(df[iter_col].min()),
        "max_iter":       int(df[iter_col].max()),
        "media_tempo":    round(df[tempo_col].mean(), 2),
        "std_tempo":      round(df[tempo_col].std(), 2),
        "min_tempo":      round(df[tempo_col].min(), 2),
        "max_tempo":      round(df[tempo_col].max(), 2),
        "media_h_final":  round(df[h_col].mean(), 4),
    }


stats = {}

if df_grasp is not None:
    iter_g  = next(c for c in df_grasp.columns if "iter" in c.lower())
    tempo_g = next(c for c in df_grasp.columns if "tempo" in c.lower())
    suc_g   = next(c for c in df_grasp.columns if "sucesso" in c.lower())
    h_g     = next(c for c in df_grasp.columns if "h_final" in c.lower())
    df_grasp[iter_g]  = pd.to_numeric(df_grasp[iter_g],  errors="coerce").fillna(0).astype(int)
    df_grasp[tempo_g] = pd.to_numeric(df_grasp[tempo_g], errors="coerce").fillna(0.0)
    df_grasp[h_g]     = pd.to_numeric(df_grasp[h_g],     errors="coerce").fillna(0)
    stats["GRASP"] = metricas(df_grasp, iter_g, tempo_g, suc_g, h_g)

if df_ag is not None:
    # AG pode ter coluna 'geracao_parada' ou 'iteracoes'
    iter_ag  = "geracao_parada" if "geracao_parada" in df_ag.columns else \
               next(c for c in df_ag.columns if "iter" in c.lower() or "gera" in c.lower())
    tempo_ag = next(c for c in df_ag.columns if "tempo" in c.lower())
    suc_ag   = next(c for c in df_ag.columns if "sucesso" in c.lower())
    h_ag     = next(c for c in df_ag.columns if "h_final" in c.lower())
    df_ag[iter_ag]  = pd.to_numeric(df_ag[iter_ag],  errors="coerce").fillna(0).astype(int)
    df_ag[tempo_ag] = pd.to_numeric(df_ag[tempo_ag], errors="coerce").fillna(0.0)
    df_ag[h_ag]     = pd.to_numeric(df_ag[h_ag],     errors="coerce").fillna(0)
    stats["AG"] = metricas(df_ag, iter_ag, tempo_ag, suc_ag, h_ag)


print(json.dumps(stats, ensure_ascii=False, indent=2))


# ── Gráfico 1: Taxa de Sucesso (Barras Comparativas) ─────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])

algoritmos = list(stats.keys())
taxas = [stats[a]["taxa_sucesso"] for a in algoritmos]
cores = [PALETTE["grasp"] if a == "GRASP" else PALETTE["ag"] for a in algoritmos]

bars = ax.bar(algoritmos, taxas, color=cores, width=0.45, zorder=3, edgecolor="black")
for bar, val in zip(bars, taxas):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
            f"{val:.1f}%", ha="center", va="bottom",
            color=PALETTE["text"], fontweight="bold", fontsize=13)

apply_base_style(ax, "Taxa de Sucesso por Algoritmo (%)", "Algoritmo", "Taxa de Sucesso (%)")
ax.set_ylim(0, 115)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "comp_grafico1_taxa_sucesso.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] comp_grafico1_taxa_sucesso.png salvo.")


# ── Gráfico 2: Tempo de Execução (Barras com Erro) ───────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])

medias_t  = [stats[a]["media_tempo"] for a in algoritmos]
desvios_t = [stats[a]["std_tempo"]   for a in algoritmos]
cores = [PALETTE["grasp"] if a == "GRASP" else PALETTE["ag"] for a in algoritmos]

x_pos = np.arange(len(algoritmos))
bars = ax.bar(x_pos, medias_t, yerr=desvios_t,
              color=cores, width=0.45, zorder=3, edgecolor="black",
              capsize=8, error_kw={"elinewidth": 2, "ecolor": "#555555"})

ax.set_xticks(x_pos)
ax.set_xticklabels(algoritmos)
for bar, val, std in zip(bars, medias_t, desvios_t):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + std + 0.5,
            f"{val:.1f} ms", ha="center", va="bottom",
            color=PALETTE["text"], fontweight="bold", fontsize=11)

apply_base_style(ax, "Tempo Médio de Execução (ms)", "Algoritmo", "Tempo (ms)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "comp_grafico2_tempo_execucao.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] comp_grafico2_tempo_execucao.png salvo.")


# ── Gráfico 3: Iterações / Gerações (Boxplot Lado a Lado) ────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor(PALETTE["bg"])

box_data  = []
box_labels = []

if df_grasp is not None:
    box_data.append(df_grasp[iter_g].values)
    box_labels.append("GRASP\n(iterações)")

if df_ag is not None:
    box_data.append(df_ag[iter_ag].values)
    box_labels.append("AG\n(gerações)")

if box_data:
    bp = ax.boxplot(
        box_data,
        # pyrefly: ignore [unexpected-keyword]
        labels=box_labels,
        patch_artist=True,
        medianprops=dict(color=PALETTE["text"], linewidth=2.5),
        whiskerprops=dict(color="black"),
        capprops=dict(color="black"),
        flierprops=dict(marker="o", markerfacecolor=PALETTE["falha"],
                        markersize=6, linestyle="none"),
    )
    colors_box = [PALETTE["grasp"], PALETTE["ag"]]
    for patch, color in zip(bp["boxes"], colors_box):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

apply_base_style(ax, "Distribuição de Iterações / Gerações", "Algoritmo", "Quantidade")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "comp_grafico3_iteracoes_geracoes.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] comp_grafico3_iteracoes_geracoes.png salvo.")


# ── Gráfico 4: Conflitos Finais (h_final) por Execução ───────────────────────
fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(PALETTE["bg"])

if df_grasp is not None:
    id_g = next(c for c in df_grasp.columns if "id_exec" in c.lower())
    ax.plot(df_grasp[id_g].tolist(), df_grasp[h_g].tolist(),
            color=PALETTE["grasp"], linewidth=1.8, marker="o", markersize=4,
            label="GRASP", zorder=3)

if df_ag is not None:
    id_ag = next(c for c in df_ag.columns if "id_exec" in c.lower())
    ax.plot(df_ag[id_ag].tolist(), df_ag[h_ag].tolist(),
            color=PALETTE["ag"], linewidth=1.8, marker="s", markersize=4,
            label="AG", zorder=3)

apply_base_style(ax, "Conflitos Finais (h_final) por Execução",
                 "ID da Execução", "h_final (conflitos)")
ax.legend(facecolor=PALETTE["bg"], edgecolor=PALETTE["text"])
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "comp_grafico4_hfinal_execucoes.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] comp_grafico4_hfinal_execucoes.png salvo.")


# ── Tabela 1: Resumo Estatístico Completo ────────────────────────────────────
header = ["Métrica", "GRASP", "AG"]
linhas = [header]

metricas_labels = [
    ("Total de Execuções",       "n",             "{}"),
    ("Sucessos",                 "sucessos",      "{}"),
    ("Taxa de Sucesso (%)",      "taxa_sucesso",  "{:.2f}"),
    ("Média Iterações/Gerações", "media_iter",    "{:.2f}"),
    ("Desvio Padrão Iter/Ger",  "std_iter",      "{:.2f}"),
    ("Mín. Iterações/Gerações", "min_iter",      "{}"),
    ("Máx. Iterações/Gerações", "max_iter",      "{}"),
    ("Média Tempo (ms)",         "media_tempo",   "{:.2f}"),
    ("Desvio Padrão Tempo (ms)", "std_tempo",     "{:.2f}"),
    ("Mín. Tempo (ms)",          "min_tempo",     "{:.2f}"),
    ("Máx. Tempo (ms)",          "max_tempo",     "{:.2f}"),
    ("Média h_final",            "media_h_final", "{:.4f}"),
]

for label, chave, fmt in metricas_labels:
    g_val = fmt.format(stats["GRASP"][chave]) if "GRASP" in stats else "N/A"
    a_val = fmt.format(stats["AG"][chave])    if "AG"    in stats else "N/A"
    linhas.append([label, g_val, a_val])

render_table("comp_tabela_resumo_estatistico.png",
             "Resumo Estatístico Comparativo — GRASP vs AG",
             linhas, header_color=PALETTE["grasp"])


# ── Tabela 2: Top 5 Soluções Distintas do AG ─────────────────────────────────
if df_ag is not None:
    estado_col_ag = next((c for c in df_ag.columns if "estado_final" in c.lower()), None)
    fitness_col   = next((c for c in df_ag.columns if "fitness" in c.lower()), None)

    sucessos_ag = df_ag[df_ag[suc_ag] == True].copy() if not df_ag.empty else pd.DataFrame()

    if not sucessos_ag.empty and estado_col_ag:
        # Ordena por h_final e tempo, depois deduplica por estado_final
        sucessos_ag_sorted = sucessos_ag.sort_values(by=[h_ag, tempo_ag])
        vistos = set()
        top5 = []

        for _, row in sucessos_ag_sorted.iterrows():
            estado_str = str(row[estado_col_ag])
            if estado_str not in vistos:
                vistos.add(estado_str)
                top5.append(row)
            if len(top5) == 5:
                break

        if top5:
            header_t5 = ["Rank", "ID Exec", "Estado Final", "h_final", "Fitness", "Tempo (ms)", "Geração"]
            dados_t5 = [header_t5]
            for idx, row in enumerate(top5, 1):
                fit_val = str(row[fitness_col]) if fitness_col else "N/A"
                ger_val = str(int(row["geracao_parada"])) if "geracao_parada" in row.index else "N/A"
                dados_t5.append([
                    f"#{idx}",
                    str(int(row[id_ag])),
                    str(row[estado_col_ag]),
                    str(int(row[h_ag])),
                    fit_val,
                    f"{float(row[tempo_ag]):.2f}",
                    ger_val,
                ])
            render_table("comp_tabela_top5_ag.png",
                         "Top 5 Soluções Distintas — Algoritmo Genético",
                         dados_t5, header_color=PALETTE["ag"])
        else:
            print("[AVISO] AG não encontrou soluções com sucesso para gerar o Top 5.")
    else:
        print("[AVISO] Sem dados suficientes do AG para o Top 5.")

print("\n[CONCLUÍDO] Análise comparativa salva em:", OUT_DIR)
