from flask import Flask, jsonify, request
import subprocess
import os
import json
import pandas as pd

app = Flask(__name__)

# Define o caminho base do projeto de forma dinâmica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────────────────────────────────────
# Utilitário: salvar lista de resultados em CSV
# ──────────────────────────────────────────────────────────────────────────────

def _salvar_csv(dados, nome_arquivo):
    """Serializa a lista de dicionários para CSV na pasta resultados/."""
    try:
        resultados_dir = os.path.join(BASE_DIR, "resultados")
        os.makedirs(resultados_dir, exist_ok=True)
        df = pd.DataFrame(dados)
        caminho = os.path.join(resultados_dir, nome_arquivo)
        df.to_csv(caminho, index=False)
    except Exception as e:
        print(f"[AVISO] Erro ao salvar CSV '{nome_arquivo}':", e)


def _executar_script(script_path, args_extra=None):
    """Executa um script Python e retorna a saída padrão como string."""
    cmd = ["python", script_path] + (args_extra or [])
    return subprocess.check_output(cmd, text=True, timeout=600)


# ──────────────────────────────────────────────────────────────────────────────
# Rota: GRASP
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/executar-grasp", methods=["POST"])
def executar_grasp():
    """
    Executa 50 rodadas do GRASP e retorna JSON + salva execucoes_grasp.csv.

    Parâmetros (corpo JSON opcional):
      num_execucoes : int   (padrão 50)
      max_iter      : int   (padrão 1000)
      alpha         : float (padrão 0.3)
    """
    body = request.get_json(silent=True) or {}
    num_exec  = str(body.get("num_execucoes", 50))
    max_iter  = str(body.get("max_iter",      1000))
    alpha     = str(body.get("alpha",         0.3))

    script_path = os.path.join(BASE_DIR, "codigo", "grasp.py")
    try:
        resultado = _executar_script(
            script_path,
            ["--num_execucoes", num_exec, "--max_iter", max_iter, "--alpha", alpha]
        )
        dados = json.loads(resultado)
        _salvar_csv(dados, "execucoes_grasp.csv")
        return jsonify({"execucoes": dados, "total": len(dados), "algoritmo": "GRASP"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Rota nova: Algoritmo Genético
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/executar-genetico", methods=["POST"])
def executar_genetico():
    """
    Executa 50 rodadas do Algoritmo Genético e retorna JSON + salva execucoes_genetico.csv.

    Parâmetros (corpo JSON opcional):
      num_execucoes      : int (padrão 50)
      max_geracoes       : int (padrão 1000)
      tamanho_populacao  : int (padrão 100)
    """
    body = request.get_json(silent=True) or {}
    num_exec  = str(body.get("num_execucoes",     50))
    max_ger   = str(body.get("max_geracoes",      1000))
    tam_pop   = str(body.get("tamanho_populacao", 100))

    script_path = os.path.join(BASE_DIR, "codigo", "algoritmo_genetico.py")
    try:
        resultado = _executar_script(
            script_path,
            [
                "--num_execucoes", num_exec,
                "--max_geracoes",  max_ger,
                "--tamanho_populacao", tam_pop,
            ]
        )
        dados = json.loads(resultado)
        _salvar_csv(dados, "execucoes_genetico.csv")
        return jsonify({"execucoes": dados, "total": len(dados), "algoritmo": "AG"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Rota: Gerar Gráficos (Hill Climbing + Comparativo)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/gerar-graficos", methods=["POST"])
def gerar_graficos():
    """
    Dispara o script de análise comparativa GRASP vs AG.
    Gera todos os gráficos e tabelas na pasta resultados/.
    """
    script_path = os.path.join(BASE_DIR, "codigo", "analisar_comparativo.py")
    try:
        saida = _executar_script(script_path)
        return jsonify({
            "status": "sucesso",
            "mensagem": "Gráficos e tabelas comparativos gerados em resultados/",
            "log": saida,
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"erro": str(e), "log": getattr(e, 'output', '')}), 500
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Rota: Salvar Métricas do Gemini (mantida da versão anterior)
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/salvar-metricas", methods=["POST"])
def salvar_metricas():
    try:
        dados_gemini = request.get_json()

        texto_resposta = (
            dados_gemini
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        if not texto_resposta:
            return jsonify({"erro": "Resposta do Gemini não contém texto."}), 400

        metricas_limpas = json.loads(texto_resposta)

        resultados_dir = os.path.join(BASE_DIR, "resultados")
        os.makedirs(resultados_dir, exist_ok=True)
        caminho_arquivo = os.path.join(resultados_dir, "metricas_gemini.json")

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(metricas_limpas, f, indent=4, ensure_ascii=False)

        return jsonify({
            "status": "sucesso",
            "mensagem": "Métricas do Gemini salvas com sucesso.",
            "arquivo": caminho_arquivo,
            "metricas": metricas_limpas,
        })
    except json.JSONDecodeError:
        return jsonify({
            "erro": "O texto retornado pelo Gemini não é um JSON válido.",
            "texto_recebido": texto_resposta,
        }), 400
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Ponto de Entrada
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(port=5000, debug=False)
