"""Validacao da resposta estruturada retornada pela IA."""

from __future__ import annotations

from typing import Any


CAMPOS_OBRIGATORIOS = (
    "classificacao",
    "confianca",
    "sinais",
    "recomendacoes",
    "explicacao_simples",
    "informacao_insuficiente",
)

CLASSIFICACOES_PERMITIDAS = {
    "baixo_risco",
    "moderado",
    "alto_risco",
    "informacao_insuficiente",
}


def _eh_numero(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_lista_de_textos(nome_campo: str, valor: Any) -> list[str]:
    if not isinstance(valor, list):
        return [f"{nome_campo} deve ser uma lista"]

    if not all(isinstance(item, str) and item.strip() for item in valor):
        return [f"{nome_campo} deve conter apenas textos nao vazios"]

    return []


def validar_resposta_ia(resposta: Any) -> list[str]:
    """Retorna erros de validacao encontrados na resposta da IA."""
    if not isinstance(resposta, dict):
        return ["resposta deve ser um objeto JSON"]

    erros = []

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in resposta:
            erros.append(f"campo ausente: {campo}")

    if "classificacao" in resposta:
        classificacao = resposta["classificacao"]
        if classificacao not in CLASSIFICACOES_PERMITIDAS:
            erros.append("classificacao invalida")

    if "confianca" in resposta:
        confianca = resposta["confianca"]
        if not _eh_numero(confianca) or not 0 <= confianca <= 1:
            erros.append("confianca deve ser um numero entre 0 e 1")

    if "sinais" in resposta:
        erros.extend(_validar_lista_de_textos("sinais", resposta["sinais"]))

    if "recomendacoes" in resposta:
        erros.extend(
            _validar_lista_de_textos("recomendacoes", resposta["recomendacoes"])
        )

    if "explicacao_simples" in resposta:
        explicacao = resposta["explicacao_simples"]
        if not isinstance(explicacao, str) or not explicacao.strip():
            erros.append("explicacao_simples deve ser um texto nao vazio")

    if "informacao_insuficiente" in resposta and not isinstance(
        resposta["informacao_insuficiente"], bool
    ):
        erros.append("informacao_insuficiente deve ser booleano")

    return erros


def resposta_eh_valida(resposta: Any) -> bool:
    """Indica se a resposta da IA pode seguir no fluxo da aplicacao."""
    return not validar_resposta_ia(resposta)
