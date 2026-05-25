"""
analisar_comparativo.py
-----------------------
Lê os CSVs de GRASP e Algoritmo Genético e gera gráficos e tabelas
comparativas completas entre os dois algoritmos para o problema das 8-rainhas.

Saídas geradas em resultados/:
  Gráficos (10):
    comp_grafico1_taxa_sucesso.png
    comp_grafico2_tempo_execucao.png
    comp_grafico3_iteracoes_geracoes.png
    comp_grafico4_hfinal_execucoes.png
    comp_grafico5_distribuicao_tempo.png
    comp_grafico6_scatter_tempo_iter.png
    comp_grafico7_histograma_hfinal.png
    comp_grafico8_convergencia_acumulada.png
    comp_grafico9_violin_tempo.png
    comp_grafico10_radar_comparativo.png

  Tabelas (5):
    comp_tabela_resumo_estatistico.png
    comp_tabela_top5_ag.png
    comp_tabela_top5_grasp.png
    comp_tabela_percentis.png
    comp_tabela_analise_qualidade.png
"""

import os
import sys
import json
import ast
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.patches import FancyBboxPatch

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
    "neutro":   "#9467bd",   # Roxo
    "acento":   "#17becf",   # Ciano
    "grid":     "#e0e0e0",
    "bg":       "#ffffff",
    "bg_alt":   "#f8f9fa",
    "text":     "#222222",
    "subtext":  "#666666",
}

plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "axes.titlesize":  14,
    "axes.labelsize":  11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
})

plt.style.use("default")


# ── Funções utilitárias ───────────────────────────────────────────────────────

def apply_base_style(ax, title, xlabel="", ylabel=""):
    ax.set_facecolor(PALETTE["bg"])
    ax.set_title(title, color=PALETTE["text"], fontsize=14,
                 fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, color=PALETTE["text"], fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, color=PALETTE["text"], fontsize=11)
    ax.tick_params(colors=PALETTE["text"])
    for spine in ["bottom", "left"]:
        ax.spines[spine].set_color("#aaaaaa")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=PALETTE["grid"], linestyle="--", alpha=0.7)


def save_fig(fig, filename):
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=150, facecolor=PALETTE["bg"], bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {filename} salvo.")


def render_table(fig_name, title, data, header_color="#1f77b4", col_widths=None):
    """Renderiza e salva uma tabela como imagem PNG."""
    n_rows = len(data)
    n_cols = len(data[0]) if data else 1
    fig_w  = max(10, n_cols * 2.2)
    fig_h  = max(2.5, n_rows * 0.62)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.axis("tight")
    ax.axis("off")

    table = ax.table(
        cellText=data, colLabels=None,
        cellLoc="center", loc="center",
        colWidths=col_widths,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.scale(1, 1.85)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#cccccc")
        if row == 0:
            cell.set_text_props(weight="bold", color="white")
            cell.set_facecolor(header_color)
        else:
            alt = PALETTE["bg_alt"] if row % 2 == 0 else "white"
            cell.set_facecolor(alt)
            cell.set_text_props(color=PALETTE["text"])

    plt.title(title, color=PALETTE["text"], fontsize=13,
              fontweight="bold", pad=16)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, fig_name)
    plt.savefig(path, dpi=150, facecolor=PALETTE["bg"], bbox_inches="tight")
    plt.close()
    print(f"[OK] {fig_name} salvo.")


# ── Leitura dos CSVs ──────────────────────────────────────────────────────────

def carregar_csv(path, nome):
    if not os.path.exists(path):
        print(f"[AVISO] CSV do {nome} não encontrado em {path}. Pulando.")
        return None
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].replace(
                {"True": True, "False": False, "true": True, "false": False}
            )
    return df


df_grasp = carregar_csv(CSV_GRASP, "GRASP")
df_ag    = carregar_csv(CSV_AG,    "Algoritmo Genético")

if df_grasp is None and df_ag is None:
    print("[ERRO] Nenhum CSV encontrado. Execute os algoritmos antes.")
    sys.exit(1)


# ── Identificação de colunas ───────────────────────────────────────────────────

def _col(df, keywords, fallback=None):
    """Retorna o nome da primeira coluna que contém qualquer keyword."""
    for kw in keywords:
        for c in df.columns:
            if kw in c.lower():
                return c
    return fallback

if df_grasp is not None:
    iter_g  = _col(df_grasp, ["iter"])
    tempo_g = _col(df_grasp, ["tempo"])
    suc_g   = _col(df_grasp, ["sucesso"])
    h_g     = _col(df_grasp, ["h_final"])
    id_g    = _col(df_grasp, ["id_exec"])

    df_grasp[iter_g]  = pd.to_numeric(df_grasp[iter_g],  errors="coerce").fillna(0).astype(int)
    df_grasp[tempo_g] = pd.to_numeric(df_grasp[tempo_g], errors="coerce").fillna(0.0)
    df_grasp[h_g]     = pd.to_numeric(df_grasp[h_g],     errors="coerce").fillna(0)

if df_ag is not None:
    iter_ag  = "geracao_parada" if "geracao_parada" in df_ag.columns else \
               _col(df_ag, ["gera", "iter"])
    tempo_ag = _col(df_ag, ["tempo"])
    suc_ag   = _col(df_ag, ["sucesso"])
    h_ag     = _col(df_ag, ["h_final"])
    id_ag    = _col(df_ag, ["id_exec"])
    fit_ag   = _col(df_ag, ["fitness"])

    df_ag[iter_ag]  = pd.to_numeric(df_ag[iter_ag],  errors="coerce").fillna(0).astype(int)
    df_ag[tempo_ag] = pd.to_numeric(df_ag[tempo_ag], errors="coerce").fillna(0.0)
    df_ag[h_ag]     = pd.to_numeric(df_ag[h_ag],     errors="coerce").fillna(0)


# ── Cálculo de métricas por algoritmo ────────────────────────────────────────

def metricas(df, iter_col, tempo_col, sucesso_col, h_col):
    n = len(df)
    sucessos = int(df[sucesso_col].sum())
    iters = df[iter_col]
    tempos = df[tempo_col]
    h_vals = df[h_col]
    return {
        "n":             n,
        "sucessos":      sucessos,
        "falhas":        n - sucessos,
        "taxa_sucesso":  round(sucessos / n * 100, 2) if n > 0 else 0,
        "media_iter":    round(iters.mean(),  2),
        "std_iter":      round(iters.std(),   2),
        "min_iter":      int(iters.min()),
        "max_iter":      int(iters.max()),
        "q1_iter":       round(iters.quantile(0.25), 2),
        "mediana_iter":  round(iters.median(), 2),
        "q3_iter":       round(iters.quantile(0.75), 2),
        "media_tempo":   round(tempos.mean(),  2),
        "std_tempo":     round(tempos.std(),   2),
        "min_tempo":     round(tempos.min(),   2),
        "max_tempo":     round(tempos.max(),   2),
        "q1_tempo":      round(tempos.quantile(0.25), 2),
        "mediana_tempo": round(tempos.median(), 2),
        "q3_tempo":      round(tempos.quantile(0.75), 2),
        "media_h":       round(h_vals.mean(),  4),
        "std_h":         round(h_vals.std(),   4),
        "max_h":         int(h_vals.max()),
    }


stats = {}
if df_grasp is not None:
    stats["GRASP"] = metricas(df_grasp, iter_g, tempo_g, suc_g, h_g)
if df_ag is not None:
    stats["AG"] = metricas(df_ag, iter_ag, tempo_ag, suc_ag, h_ag)

print(json.dumps(stats, ensure_ascii=False, indent=2))

algoritmos = list(stats.keys())


# ════════════════════════════════════════════════════════════════════════════════
# GRÁFICOS
# ════════════════════════════════════════════════════════════════════════════════

# ── Gráfico 1: Taxa de Sucesso (Barras Comparativas) ─────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])

taxas  = [stats[a]["taxa_sucesso"] for a in algoritmos]
falhas = [100 - t for t in taxas]
cores  = [PALETTE["grasp"] if a == "GRASP" else PALETTE["ag"] for a in algoritmos]

x_pos = np.arange(len(algoritmos))
bars_s = ax.bar(x_pos, taxas,  color=cores,             width=0.5, label="Sucesso (%)", zorder=3, edgecolor="black", linewidth=0.7)
bars_f = ax.bar(x_pos, falhas, color=PALETTE["falha"],  width=0.5, label="Falha (%)",   zorder=3, edgecolor="black", linewidth=0.7, alpha=0.6, bottom=taxas)

for bar, val in zip(bars_s, taxas):
    ax.text(bar.get_x() + bar.get_width() / 2, val / 2,
            f"{val:.1f}%", ha="center", va="center",
            color="white", fontweight="bold", fontsize=13)

ax.set_xticks(x_pos)
ax.set_xticklabels(algoritmos, fontsize=12)
ax.set_ylim(0, 115)
ax.legend(loc="upper right")
apply_base_style(ax, "Taxa de Sucesso e Falha por Algoritmo (%)", "Algoritmo", "Percentual (%)")
plt.tight_layout()
save_fig(fig, "comp_grafico1_taxa_sucesso.png")


# ── Gráfico 2: Tempo de Execução (Barras com Erro) ───────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])

medias_t  = [stats[a]["media_tempo"] for a in algoritmos]
desvios_t = [stats[a]["std_tempo"]   for a in algoritmos]
cores = [PALETTE["grasp"] if a == "GRASP" else PALETTE["ag"] for a in algoritmos]

bars = ax.bar(x_pos, medias_t, yerr=desvios_t,
              color=cores, width=0.5, zorder=3, edgecolor="black",
              capsize=9, error_kw={"elinewidth": 2, "ecolor": "#555555"},
              linewidth=0.7)

ax.set_xticks(x_pos)
ax.set_xticklabels(algoritmos)
for bar, val, std in zip(bars, medias_t, desvios_t):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + std + max(desvios_t) * 0.05 + 0.5,
            f"{val:.1f} ms", ha="center", va="bottom",
            color=PALETTE["text"], fontweight="bold", fontsize=11)

apply_base_style(ax, "Tempo Médio de Execução ± Desvio Padrão (ms)", "Algoritmo", "Tempo (ms)")
plt.tight_layout()
save_fig(fig, "comp_grafico2_tempo_execucao.png")


# ── Gráfico 3: Iterações / Gerações (Boxplot Lado a Lado) ────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor(PALETTE["bg"])

box_data   = []
box_labels = []
box_colors = []

if df_grasp is not None:
    box_data.append(df_grasp[iter_g].values)
    box_labels.append("GRASP\n(iterações)")
    box_colors.append(PALETTE["grasp"])

if df_ag is not None:
    box_data.append(df_ag[iter_ag].values)
    box_labels.append("AG\n(gerações)")
    box_colors.append(PALETTE["ag"])

if box_data:
    bp = ax.boxplot(
        box_data,
        labels=box_labels,
        patch_artist=True,
        notch=False,
        medianprops=dict(color="black", linewidth=2.5),
        whiskerprops=dict(color="#555555", linewidth=1.5),
        capprops=dict(color="#555555", linewidth=1.5),
        flierprops=dict(marker="o", markerfacecolor=PALETTE["falha"],
                        markersize=6, linestyle="none", alpha=0.7),
    )
    for patch, color in zip(bp["boxes"], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    # Adiciona média como losango
    for i, data in enumerate(box_data, 1):
        ax.plot(i, np.mean(data), marker="D", color="white",
                markersize=8, zorder=5, markeredgecolor="black", linewidth=1.5)

apply_base_style(ax, "Distribuição de Iterações / Gerações (Boxplot)", "Algoritmo", "Quantidade")
ax.text(0.98, 0.98, "◆ = Média", transform=ax.transAxes,
        ha="right", va="top", fontsize=9, color=PALETTE["subtext"])
plt.tight_layout()
save_fig(fig, "comp_grafico3_iteracoes_geracoes.png")


# ── Gráfico 4: Conflitos Finais (h_final) por Execução ───────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor(PALETTE["bg"])

if df_grasp is not None:
    ax.plot(df_grasp[id_g].tolist(), df_grasp[h_g].tolist(),
            color=PALETTE["grasp"], linewidth=1.8, marker="o", markersize=4.5,
            label="GRASP", zorder=3, alpha=0.9)

if df_ag is not None:
    ax.plot(df_ag[id_ag].tolist(), df_ag[h_ag].tolist(),
            color=PALETTE["ag"], linewidth=1.8, marker="s", markersize=4.5,
            label="AG", zorder=3, alpha=0.9)

ax.axhline(0, color=PALETTE["sucesso"], linestyle="--", linewidth=1.5,
           label="Solução Ótima (h=0)", alpha=0.8)
apply_base_style(ax, "Conflitos Finais (h_final) por Execução",
                 "ID da Execução", "h_final (conflitos)")
ax.legend(facecolor=PALETTE["bg"], edgecolor="#aaaaaa")
plt.tight_layout()
save_fig(fig, "comp_grafico4_hfinal_execucoes.png")


# ── Gráfico 5: Histograma de Tempo de Execução ───────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
fig.patch.set_facecolor(PALETTE["bg"])
fig.suptitle("Distribuição do Tempo de Execução por Algoritmo",
             fontsize=14, fontweight="bold", color=PALETTE["text"])

for ax, (nome, df_ref, tempo_col, cor) in zip(axes, [
    ("GRASP", df_grasp, tempo_g if df_grasp is not None else None, PALETTE["grasp"]),
    ("AG",    df_ag,    tempo_ag if df_ag    is not None else None, PALETTE["ag"]),
]):
    if df_ref is None or tempo_col is None:
        ax.text(0.5, 0.5, "Sem dados", ha="center", va="center",
                transform=ax.transAxes, color=PALETTE["subtext"])
        continue

    vals = df_ref[tempo_col].values
    bins = min(15, max(5, len(vals) // 4))
    ax.hist(vals, bins=bins, color=cor, edgecolor="white",
            linewidth=0.7, alpha=0.85, zorder=3)
    ax.axvline(np.mean(vals), color="black", linestyle="--", linewidth=1.8,
               label=f"Média: {np.mean(vals):.1f} ms")
    ax.axvline(np.median(vals), color=PALETTE["neutro"], linestyle=":",
               linewidth=1.8, label=f"Mediana: {np.median(vals):.1f} ms")
    apply_base_style(ax, nome, "Tempo (ms)", "Frequência")
    ax.legend(fontsize=9)

plt.tight_layout()
save_fig(fig, "comp_grafico5_distribuicao_tempo.png")


# ── Gráfico 6: Scatter — Tempo × Iterações/Gerações ──────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor(PALETTE["bg"])

if df_grasp is not None:
    suc_mask_g  = df_grasp[suc_g].astype(bool)
    ax.scatter(df_grasp.loc[ suc_mask_g, iter_g],  df_grasp.loc[ suc_mask_g, tempo_g],
               color=PALETTE["grasp"], marker="o", s=55, alpha=0.8,
               label="GRASP — Sucesso", zorder=4, edgecolors="white", linewidth=0.5)
    ax.scatter(df_grasp.loc[~suc_mask_g, iter_g],  df_grasp.loc[~suc_mask_g, tempo_g],
               color=PALETTE["grasp"], marker="x", s=70, alpha=0.8,
               label="GRASP — Falha", zorder=4)

if df_ag is not None:
    suc_mask_ag = df_ag[suc_ag].astype(bool)
    ax.scatter(df_ag.loc[ suc_mask_ag, iter_ag], df_ag.loc[ suc_mask_ag, tempo_ag],
               color=PALETTE["ag"], marker="s", s=55, alpha=0.8,
               label="AG — Sucesso", zorder=4, edgecolors="white", linewidth=0.5)
    ax.scatter(df_ag.loc[~suc_mask_ag, iter_ag], df_ag.loc[~suc_mask_ag, tempo_ag],
               color=PALETTE["ag"], marker="P", s=70, alpha=0.8,
               label="AG — Falha", zorder=4)

apply_base_style(ax, "Dispersão: Iterações/Gerações × Tempo de Execução",
                 "Iterações / Gerações", "Tempo (ms)")
ax.legend(fontsize=9, facecolor=PALETTE["bg"], edgecolor="#aaaaaa")
plt.tight_layout()
save_fig(fig, "comp_grafico6_scatter_tempo_iter.png")


# ── Gráfico 7: Histograma comparativo de h_final ─────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor(PALETTE["bg"])

all_h_vals = []
if df_grasp is not None:
    all_h_vals.extend(df_grasp[h_g].unique().tolist())
if df_ag is not None:
    all_h_vals.extend(df_ag[h_ag].unique().tolist())

unique_h = sorted(set(int(v) for v in all_h_vals))
width    = 0.35
x_h      = np.arange(len(unique_h))

if df_grasp is not None:
    cnt_g = [int((df_grasp[h_g] == v).sum()) for v in unique_h]
    ax.bar(x_h - width / 2, cnt_g, width=width, color=PALETTE["grasp"],
           edgecolor="white", label="GRASP", alpha=0.85, zorder=3)

if df_ag is not None:
    cnt_ag = [int((df_ag[h_ag] == v).sum()) for v in unique_h]
    ax.bar(x_h + width / 2, cnt_ag, width=width, color=PALETTE["ag"],
           edgecolor="white", label="AG", alpha=0.85, zorder=3)

ax.set_xticks(x_h)
ax.set_xticklabels([str(v) for v in unique_h])
apply_base_style(ax, "Frequência de Conflitos Finais (h_final) por Algoritmo",
                 "h_final (número de conflitos)", "Frequência")
ax.legend(facecolor=PALETTE["bg"], edgecolor="#aaaaaa")
plt.tight_layout()
save_fig(fig, "comp_grafico7_histograma_hfinal.png")


# ── Gráfico 8: Convergência Acumulada de Sucesso ─────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(PALETTE["bg"])

if df_grasp is not None:
    cum_g = df_grasp.sort_values(id_g)[suc_g].astype(int).cumsum().values
    ax.plot(range(1, len(cum_g) + 1), cum_g,
            color=PALETTE["grasp"], linewidth=2.2, marker="o", markersize=4,
            label="GRASP — Sucessos Acumulados", zorder=3)

if df_ag is not None:
    cum_ag = df_ag.sort_values(id_ag)[suc_ag].astype(int).cumsum().values
    ax.plot(range(1, len(cum_ag) + 1), cum_ag,
            color=PALETTE["ag"], linewidth=2.2, marker="s", markersize=4,
            label="AG — Sucessos Acumulados", zorder=3)

apply_base_style(ax, "Convergência Acumulada de Sucessos por Execução",
                 "Execução (ordem)", "Total de Sucessos Acumulados")
ax.legend(facecolor=PALETTE["bg"], edgecolor="#aaaaaa")
plt.tight_layout()
save_fig(fig, "comp_grafico8_convergencia_acumulada.png")


# ── Gráfico 9: Violin Plot — Tempo de Execução ───────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor(PALETTE["bg"])

violin_data   = []
violin_labels = []
violin_colors = []

if df_grasp is not None:
    violin_data.append(df_grasp[tempo_g].values)
    violin_labels.append("GRASP")
    violin_colors.append(PALETTE["grasp"])

if df_ag is not None:
    violin_data.append(df_ag[tempo_ag].values)
    violin_labels.append("AG")
    violin_colors.append(PALETTE["ag"])

if violin_data:
    parts = ax.violinplot(violin_data, positions=range(1, len(violin_data) + 1),
                          showmeans=True, showmedians=True, showextrema=True)

    for pc, col in zip(parts["bodies"], violin_colors):
        pc.set_facecolor(col)
        pc.set_alpha(0.7)

    parts["cmeans"].set_color("black")
    parts["cmeans"].set_linewidth(2)
    parts["cmedians"].set_color(PALETTE["neutro"])
    parts["cmedians"].set_linewidth(2)

    ax.set_xticks(range(1, len(violin_labels) + 1))
    ax.set_xticklabels(violin_labels, fontsize=12)

mean_patch   = mpatches.Patch(color="black",          label="Média")
median_patch = mpatches.Patch(color=PALETTE["neutro"], label="Mediana")
ax.legend(handles=[mean_patch, median_patch], fontsize=9,
          facecolor=PALETTE["bg"], edgecolor="#aaaaaa")

apply_base_style(ax, "Distribuição do Tempo de Execução (Violin Plot)",
                 "Algoritmo", "Tempo (ms)")
plt.tight_layout()
save_fig(fig, "comp_grafico9_violin_tempo.png")


# ── Gráfico 10: Radar Chart — Métricas Normalizadas ──────────────────────────
categorias = [
    "Taxa de\nSucesso (%)",
    "Velocidade\n(1/tempo norm.)",
    "Estabilidade\n(1/std_iter)",
    "Qualidade\nh_final = 0",
    "Eficiência\nIterações",
]
N_cat = len(categorias)

def normalizar(val, min_v, max_v):
    if max_v == min_v:
        return 0.5
    return (val - min_v) / (max_v - min_v)

radar_scores = {}
for nome in algoritmos:
    st = stats[nome]
    scores = [
        st["taxa_sucesso"] / 100,
        1 - normalizar(st["media_tempo"], 0,
                       max(stats[a]["media_tempo"] for a in algoritmos)),
        normalizar(1 / (st["std_iter"] + 1),
                   min(1 / (stats[a]["std_iter"] + 1) for a in algoritmos),
                   max(1 / (stats[a]["std_iter"] + 1) for a in algoritmos)),
        st["taxa_sucesso"] / 100,
        1 - normalizar(st["media_iter"],
                       min(stats[a]["media_iter"] for a in algoritmos),
                       max(stats[a]["media_iter"] for a in algoritmos)),
    ]
    radar_scores[nome] = scores

angles = np.linspace(0, 2 * np.pi, N_cat, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
fig.patch.set_facecolor(PALETTE["bg"])

for nome, cor in [("GRASP", PALETTE["grasp"]), ("AG", PALETTE["ag"])]:
    if nome not in radar_scores:
        continue
    valores = radar_scores[nome] + radar_scores[nome][:1]
    ax.plot(angles, valores, "o-", linewidth=2.2, color=cor, label=nome)
    ax.fill(angles, valores, alpha=0.18, color=cor)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categorias, fontsize=10, color=PALETTE["text"])
ax.set_yticklabels([])
ax.set_ylim(0, 1)
ax.set_title("Comparação Radar — Métricas Normalizadas\nGRASP vs Algoritmo Genético",
             fontsize=13, fontweight="bold", color=PALETTE["text"], pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
          facecolor=PALETTE["bg"], edgecolor="#aaaaaa")
ax.grid(color=PALETTE["grid"], linestyle="--", alpha=0.6)
plt.tight_layout()
save_fig(fig, "comp_grafico10_radar_comparativo.png")


# ════════════════════════════════════════════════════════════════════════════════
# TABELAS
# ════════════════════════════════════════════════════════════════════════════════

# ── Tabela 1: Resumo Estatístico Completo ────────────────────────────────────
header = ["Métrica", "GRASP", "AG"]
linhas = [header]

metricas_labels = [
    ("Total de Execuções",          "n",             "{}"),
    ("Sucessos",                    "sucessos",      "{}"),
    ("Falhas",                      "falhas",        "{}"),
    ("Taxa de Sucesso (%)",         "taxa_sucesso",  "{:.2f}"),
    ("──────── Iterações ────────", "",               ""),
    ("Média Iterações/Gerações",    "media_iter",    "{:.2f}"),
    ("Desvio Padrão Iter/Ger",     "std_iter",      "{:.2f}"),
    ("Mínimo Iterações/Gerações",  "min_iter",      "{}"),
    ("Máximo Iterações/Gerações",  "max_iter",      "{}"),
    ("──────── Tempo ────────",    "",               ""),
    ("Média Tempo (ms)",            "media_tempo",   "{:.2f}"),
    ("Desvio Padrão Tempo (ms)",   "std_tempo",     "{:.2f}"),
    ("Mínimo Tempo (ms)",           "min_tempo",     "{:.2f}"),
    ("Máximo Tempo (ms)",           "max_tempo",     "{:.2f}"),
    ("──────── Qualidade ────────", "",              ""),
    ("Média h_final",               "media_h",       "{:.4f}"),
    ("Desvio Padrão h_final",      "std_h",         "{:.4f}"),
    ("h_final Máximo Observado",    "max_h",         "{}"),
]

for label, chave, fmt in metricas_labels:
    if chave == "":
        # Linha separadora
        linhas.append([label, "—", "—"])
        continue
    g_val = fmt.format(stats["GRASP"][chave]) if "GRASP" in stats else "N/A"
    a_val = fmt.format(stats["AG"][chave])    if "AG"    in stats else "N/A"
    linhas.append([label, g_val, a_val])

render_table("comp_tabela_resumo_estatistico.png",
             "Resumo Estatístico Completo — GRASP vs Algoritmo Genético",
             linhas, header_color=PALETTE["grasp"])


# ── Tabela 2: Top 5 Soluções Distintas do AG ─────────────────────────────────
if df_ag is not None:
    estado_col_ag = _col(df_ag, ["estado_final"])
    fitness_col   = _col(df_ag, ["fitness"])

    sucessos_ag = df_ag[df_ag[suc_ag] == True].copy() if not df_ag.empty else pd.DataFrame()

    if not sucessos_ag.empty and estado_col_ag:
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
            header_t5 = ["Rank", "ID Exec", "Estado Final", "h_final",
                          "Fitness", "Tempo (ms)", "Geração"]
            dados_t5 = [header_t5]
            for idx, row in enumerate(top5, 1):
                fit_val = str(row[fitness_col]) if fitness_col else "N/A"
                ger_val = str(int(row["geracao_parada"])) \
                          if "geracao_parada" in row.index else "N/A"
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


# ── Tabela 3: Top 5 Soluções Distintas do GRASP ──────────────────────────────
if df_grasp is not None:
    estado_col_g = _col(df_grasp, ["estado_final"])
    sucessos_g   = df_grasp[df_grasp[suc_g] == True].copy() if not df_grasp.empty else pd.DataFrame()

    if not sucessos_g.empty and estado_col_g:
        suc_g_sorted = sucessos_g.sort_values(by=[h_g, tempo_g])
        vistos_g = set()
        top5_g   = []

        for _, row in suc_g_sorted.iterrows():
            estado_str = str(row[estado_col_g])
            if estado_str not in vistos_g:
                vistos_g.add(estado_str)
                top5_g.append(row)
            if len(top5_g) == 5:
                break

        if top5_g:
            header_t5g = ["Rank", "ID Exec", "Estado Final", "h_final",
                           "Tempo (ms)", "Iterações GRASP", "Alpha"]
            dados_t5g = [header_t5g]
            alpha_col = _col(df_grasp, ["alpha"])
            for idx, row in enumerate(top5_g, 1):
                alpha_val = f"{float(row[alpha_col]):.2f}" if alpha_col else "N/A"
                dados_t5g.append([
                    f"#{idx}",
                    str(int(row[id_g])),
                    str(row[estado_col_g]),
                    str(int(row[h_g])),
                    f"{float(row[tempo_g]):.2f}",
                    str(int(row[iter_g])),
                    alpha_val,
                ])
            render_table("comp_tabela_top5_grasp.png",
                         "Top 5 Soluções Distintas — GRASP",
                         dados_t5g, header_color=PALETTE["grasp"])
        else:
            print("[AVISO] GRASP: sem soluções com sucesso para o Top 5.")
    else:
        print("[AVISO] Sem dados suficientes do GRASP para o Top 5.")


# ── Tabela 4: Percentis Detalhados ───────────────────────────────────────────
header_pct = ["Percentil", "Iter/Ger GRASP", "Tempo GRASP (ms)",
              "Iter/Ger AG", "Tempo AG (ms)"]
dados_pct = [header_pct]

percentis_labels = [
    ("Mínimo (0%)",  0.00),
    ("P10",          0.10),
    ("P25 (Q1)",     0.25),
    ("P50 (Mediana)",0.50),
    ("P75 (Q3)",     0.75),
    ("P90",          0.90),
    ("Máximo (100%)",1.00),
]

for lbl, q in percentis_labels:
    g_iter = f"{df_grasp[iter_g].quantile(q):.1f}"  if df_grasp is not None else "N/A"
    g_tmp  = f"{df_grasp[tempo_g].quantile(q):.2f}" if df_grasp is not None else "N/A"
    a_iter = f"{df_ag[iter_ag].quantile(q):.1f}"    if df_ag    is not None else "N/A"
    a_tmp  = f"{df_ag[tempo_ag].quantile(q):.2f}"   if df_ag    is not None else "N/A"
    dados_pct.append([lbl, g_iter, g_tmp, a_iter, a_tmp])

render_table("comp_tabela_percentis.png",
             "Análise de Percentis — Iterações e Tempo por Algoritmo",
             dados_pct, header_color=PALETTE["neutro"])


# ── Tabela 5: Análise de Qualidade e Estabilidade ────────────────────────────
header_qual = ["Indicador", "GRASP", "AG", "Melhor Desempenho"]
dados_qual  = [header_qual]

def melhor(v1, v2, maior_melhor=True, nome1="GRASP", nome2="AG"):
    """Retorna qual dos dois é melhor."""
    try:
        f1, f2 = float(v1), float(v2)
        if maior_melhor:
            return nome1 if f1 > f2 else (nome2 if f2 > f1 else "Empate")
        else:
            return nome1 if f1 < f2 else (nome2 if f2 < f1 else "Empate")
    except Exception:
        return "—"

indicadores = []

if "GRASP" in stats and "AG" in stats:
    sg, sa = stats["GRASP"], stats["AG"]
    indicadores = [
        ("Taxa de Sucesso (%)",        f"{sg['taxa_sucesso']:.2f}",  f"{sa['taxa_sucesso']:.2f}",  True),
        ("Média Iterações/Gerações",   f"{sg['media_iter']:.2f}",   f"{sa['media_iter']:.2f}",    False),
        ("Desvio Padrão Iterações",    f"{sg['std_iter']:.2f}",     f"{sa['std_iter']:.2f}",      False),
        ("Coef. Variação Iterações",
         f"{sg['std_iter']/sg['media_iter']*100:.1f}%",
         f"{sa['std_iter']/sa['media_iter']*100:.1f}%",             False),
        ("Média Tempo (ms)",           f"{sg['media_tempo']:.2f}",  f"{sa['media_tempo']:.2f}",   False),
        ("Desvio Padrão Tempo (ms)",   f"{sg['std_tempo']:.2f}",    f"{sa['std_tempo']:.2f}",     False),
        ("Coef. Variação Tempo",
         f"{sg['std_tempo']/sg['media_tempo']*100:.1f}%",
         f"{sa['std_tempo']/sa['media_tempo']*100:.1f}%",           False),
        ("Média h_final",              f"{sg['media_h']:.4f}",      f"{sa['media_h']:.4f}",       False),
        ("Iteração Mínima (melhor caso)", f"{sg['min_iter']}",      f"{sa['min_iter']}",          False),
        ("Iteração Máxima (pior caso)",   f"{sg['max_iter']}",      f"{sa['max_iter']}",          False),
    ]
    for lbl, vg, va, mais_melhor in indicadores:
        m = melhor(
            vg.replace("%", "").replace(",", "."),
            va.replace("%", "").replace(",", "."),
            mais_melhor
        )
        dados_qual.append([lbl, vg, va, m])

render_table("comp_tabela_analise_qualidade.png",
             "Análise de Qualidade e Estabilidade — GRASP vs AG",
             dados_qual, header_color="#2c7bb6")


print("\n[CONCLUÍDO] Análise comparativa completa salva em:", OUT_DIR)
print("  Graficos gerados (10): grafico1 ao grafico10")
print("  Tabelas geradas  (5):  tabela_resumo_estatistico, top5_ag, top5_grasp, percentis, analise_qualidade")
