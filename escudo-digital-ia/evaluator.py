"""Avaliação dos resultados da IA nos casos fictícios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from validator import CLASSIFICACOES_PERMITIDAS, validar_resposta_ia
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent
CASOS_PATH = BASE_DIR / "data" / "casos_teste.json"
RESULTADOS_V1_PATH = BASE_DIR / "data" / "resultados_prompt_v1.json"

CAMPOS_OBRIGATORIOS_CASO = {
    "id",
    "mensagem",
    "classificacao_esperada",
}

def carregar_casos(
    caminho: str | Path = CASOS_PATH,
) -> list[dict[str, Any]]:
    """Carrega e valida os casos fictícios do arquivo JSON."""
    caminho = Path(caminho)

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError as erro:
        raise ValueError("arquivo de casos não encontrado") from erro
    except json.JSONDecodeError as erro:
        raise ValueError("arquivo de casos contém JSON inválido") from erro

    if not isinstance(dados, list) or not dados:
        raise ValueError("arquivo de casos deve conter uma lista não vazia")

    for indice, caso in enumerate(dados, start=1):
        if not isinstance(caso, dict):
            raise ValueError(f"caso {indice} deve ser um objeto")

        campos_ausentes = CAMPOS_OBRIGATORIOS_CASO - set(caso)

        if campos_ausentes:
            nomes = ", ".join(sorted(campos_ausentes))
            raise ValueError(
                f"caso {indice} possui campos ausentes: {nomes}"
            )

        if not isinstance(caso["id"], str) or not caso["id"].strip():
            raise ValueError(f"caso {indice} possui id inválido")

        if (
            not isinstance(caso["mensagem"], str)
            or not caso["mensagem"].strip()
        ):
            raise ValueError(f"caso {indice} possui mensagem inválida")

        if (
            caso["classificacao_esperada"]
            not in CLASSIFICACOES_PERMITIDAS
        ):
            raise ValueError(
                f"caso {indice} possui classificação esperada inválida"
            )

    return dados

def classificar_resultado(
    classificacao_esperada: str,
    classificacao_obtida: str | None,
    json_valido: bool = True,
) -> str:
    """Classifica o resultado como acerto ou tipo de erro."""
    if not json_valido:
        return "resposta_invalida"

    if classificacao_esperada not in CLASSIFICACOES_PERMITIDAS:
        raise ValueError("classificação esperada inválida")

    if classificacao_obtida not in CLASSIFICACOES_PERMITIDAS:
        return "resposta_invalida"

    if classificacao_obtida == classificacao_esperada:
        return "acerto"

    if (
        classificacao_esperada == "baixo_risco"
        and classificacao_obtida in {"moderado", "alto_risco"}
    ):
        return "falso_positivo"

    if (
        classificacao_esperada == "alto_risco"
        and classificacao_obtida == "baixo_risco"
    ):
        return "falso_negativo"

    return "erro_classificacao"
def avaliar_caso(
    caso: dict[str, Any],
    resposta_ia: Any,
) -> dict[str, Any]:
    """Compara uma resposta da IA com o resultado esperado."""
    if not isinstance(caso, dict):
        raise TypeError("caso deve ser um objeto")

    if "id" not in caso or "classificacao_esperada" not in caso:
        raise ValueError("caso incompleto")

    identificador = caso["id"]
    classificacao_esperada = caso["classificacao_esperada"]
    erros_validacao = validar_resposta_ia(resposta_ia)

    if erros_validacao:
        return {
            "id": identificador,
            "esperado": classificacao_esperada,
            "obtido": None,
            "json_valido": False,
            "resultado": "resposta_invalida",
            "erros_validacao": erros_validacao,
        }

    classificacao_obtida = resposta_ia["classificacao"]

    return {
        "id": identificador,
        "esperado": classificacao_esperada,
        "obtido": classificacao_obtida,
        "json_valido": True,
        "resultado": classificar_resultado(
            classificacao_esperada,
            classificacao_obtida,
        ),
        "erros_validacao": [],
    }
def calcular_metricas(
    resultados: list[dict[str, Any]],
) -> dict[str, int | float]:
    """Calcula as métricas mínimas exigidas pelo projeto."""
    if not isinstance(resultados, list):
        raise TypeError("resultados deve ser uma lista")

    contagens = {
        "acerto": 0,
        "falso_positivo": 0,
        "falso_negativo": 0,
        "resposta_invalida": 0,
        "erro_classificacao": 0,
    }

    for indice, resultado in enumerate(resultados, start=1):
        if not isinstance(resultado, dict):
            raise ValueError(f"resultado {indice} deve ser um objeto")

        tipo = resultado.get("resultado")

        if tipo not in contagens:
            raise ValueError(
                f"resultado {indice} possui tipo de resultado inválido"
            )

        contagens[tipo] += 1

    total = len(resultados)
    acertos = contagens["acerto"]
    total_erros = total - acertos

    taxa_acerto = 0.0
    if total:
        taxa_acerto = round((acertos / total) * 100, 2)

    return {
        "total_casos": total,
        "acertos": acertos,
        "erros": total_erros,
        "falsos_positivos": contagens["falso_positivo"],
        "falsos_negativos": contagens["falso_negativo"],
        "respostas_invalidas": contagens["resposta_invalida"],
        "outros_erros": contagens["erro_classificacao"],
        "taxa_acerto": taxa_acerto,
    }

def salvar_resultados(
    resultados: list[dict[str, Any]],
    versao_prompt: str,
    caminho: str | Path = RESULTADOS_V1_PATH,
) -> dict[str, Any]:
    """Salva métricas e resultados sem copiar as mensagens analisadas."""
    if versao_prompt not in {"v1", "v2"}:
        raise ValueError("versão do prompt deve ser v1 ou v2")

    metricas = calcular_metricas(resultados)
    resultados_seguros = []

    campos_permitidos = (
        "id",
        "esperado",
        "obtido",
        "json_valido",
        "resultado",
        "erros_validacao",
    )

    for resultado in resultados:
        resultado_seguro = {
            campo: resultado.get(campo)
            for campo in campos_permitidos
        }
        resultados_seguros.append(resultado_seguro)

    dados_saida = {
        "versao_prompt": versao_prompt,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "metricas": metricas,
        "resultados": resultados_seguros,
    }

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(dados_saida, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return dados_saida