"""Persistencia local de metricas permitidas pelo projeto."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
CONSUMO_PATH = BASE_DIR / "data" / "consumo.json"
CARACTERES_POR_TOKEN_APROXIMADO = 4


def _metricas_consumo_zeradas() -> dict[str, int | float]:
    return {
        "total_chamadas": 0,
        "total_caracteres_entrada": 0,
        "total_tokens_aproximados": 0,
        "media_caracteres_por_chamada": 0,
        "media_tokens_aproximados_por_chamada": 0,
        "ultima_entrada_caracteres": 0,
        "ultima_entrada_tokens_aproximados": 0,
    }


def _inteiro_nao_negativo(valor: Any) -> int:
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return 0

    return max(numero, 0)


def _calcular_tokens_aproximados(total_caracteres: int) -> int:
    if total_caracteres <= 0:
        return 0

    return (total_caracteres + CARACTERES_POR_TOKEN_APROXIMADO - 1) // (
        CARACTERES_POR_TOKEN_APROXIMADO
    )


def _normalizar_consumo(dados: Any) -> dict[str, int | float]:
    if not isinstance(dados, dict):
        return _metricas_consumo_zeradas()

    total_chamadas = _inteiro_nao_negativo(dados.get("total_chamadas"))
    total_caracteres = _inteiro_nao_negativo(
        dados.get("total_caracteres_entrada")
    )
    total_tokens = _inteiro_nao_negativo(dados.get("total_tokens_aproximados"))
    ultima_entrada_caracteres = _inteiro_nao_negativo(
        dados.get("ultima_entrada_caracteres")
    )
    ultima_entrada_tokens = _inteiro_nao_negativo(
        dados.get("ultima_entrada_tokens_aproximados")
    )

    media_caracteres = 0
    media_tokens = 0
    if total_chamadas:
        media_caracteres = round(total_caracteres / total_chamadas, 2)
        media_tokens = round(total_tokens / total_chamadas, 2)

    return {
        "total_chamadas": total_chamadas,
        "total_caracteres_entrada": total_caracteres,
        "total_tokens_aproximados": total_tokens,
        "media_caracteres_por_chamada": media_caracteres,
        "media_tokens_aproximados_por_chamada": media_tokens,
        "ultima_entrada_caracteres": ultima_entrada_caracteres,
        "ultima_entrada_tokens_aproximados": ultima_entrada_tokens,
    }


def carregar_consumo(caminho: str | Path = CONSUMO_PATH) -> dict[str, int | float]:
    """Carrega metricas de consumo sem depender da mensagem original."""
    caminho = Path(caminho)

    if not caminho.exists():
        return _metricas_consumo_zeradas()

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _metricas_consumo_zeradas()

    return _normalizar_consumo(dados)


def salvar_consumo(
    consumo: dict[str, int | float],
    caminho: str | Path = CONSUMO_PATH,
) -> None:
    """Salva metricas de consumo em JSON, criando a pasta se necessario."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    consumo_normalizado = _normalizar_consumo(consumo)

    caminho.write_text(
        json.dumps(consumo_normalizado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def calcular_tamanho_entrada(texto_entrada: str) -> dict[str, int]:
    """Calcula tamanho da entrada sem retornar ou persistir seu conteudo."""
    if not isinstance(texto_entrada, str):
        raise TypeError("texto_entrada deve ser uma string")

    total_caracteres = len(texto_entrada)

    return {
        "caracteres": total_caracteres,
        "tokens_aproximados": _calcular_tokens_aproximados(total_caracteres),
    }


def registrar_consumo_basico(
    texto_entrada: str,
    caminho: str | Path = CONSUMO_PATH,
) -> dict[str, int | float]:
    """Registra chamada e tamanho da entrada, nunca a mensagem integral."""
    tamanho = calcular_tamanho_entrada(texto_entrada)
    consumo_atual = carregar_consumo(caminho)

    total_chamadas = int(consumo_atual["total_chamadas"]) + 1
    total_caracteres = (
        int(consumo_atual["total_caracteres_entrada"]) + tamanho["caracteres"]
    )
    total_tokens = (
        int(consumo_atual["total_tokens_aproximados"])
        + tamanho["tokens_aproximados"]
    )

    consumo_atualizado = {
        "total_chamadas": total_chamadas,
        "total_caracteres_entrada": total_caracteres,
        "total_tokens_aproximados": total_tokens,
        "media_caracteres_por_chamada": round(
            total_caracteres / total_chamadas, 2
        ),
        "media_tokens_aproximados_por_chamada": round(
            total_tokens / total_chamadas, 2
        ),
        "ultima_entrada_caracteres": tamanho["caracteres"],
        "ultima_entrada_tokens_aproximados": tamanho["tokens_aproximados"],
    }

    salvar_consumo(consumo_atualizado, caminho)
    return consumo_atualizado
