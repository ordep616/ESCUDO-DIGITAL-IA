"""Modo educativo com exercícios locais, sem chamada à API."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
EXERCICIOS_PATH = BASE_DIR / "data" / "exercicios_aprender.json"

QUANTIDADE_EXERCICIOS = 10

CLASSIFICACOES_VALIDAS = {
    "baixo_risco",
    "moderado",
    "alto_risco",
    "informacao_insuficiente",
}

CAMPOS_OBRIGATORIOS = {
    "id",
    "mensagem",
    "classificacao_esperada",
    "sinais",
    "explicacao",
    "recomendacoes",
}


def _validar_lista_textos(nome_campo: str, valor: Any) -> None:
    if not isinstance(valor, list):
        raise ValueError(f"{nome_campo} deve ser uma lista")

    if not all(isinstance(item, str) and item.strip() for item in valor):
        raise ValueError(f"{nome_campo} deve conter apenas textos nao vazios")


def _validar_exercicio(exercicio: Any) -> dict[str, Any]:
    if not isinstance(exercicio, dict):
        raise ValueError("cada exercicio deve ser um objeto")

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in exercicio:
            raise ValueError(f"campo ausente no exercicio: {campo}")

    if exercicio["classificacao_esperada"] not in CLASSIFICACOES_VALIDAS:
        raise ValueError("classificacao_esperada invalida")

    for campo in ("id", "mensagem", "explicacao"):
        if not isinstance(exercicio[campo], str) or not exercicio[campo].strip():
            raise ValueError(f"{campo} deve ser um texto nao vazio")

    _validar_lista_textos("sinais", exercicio["sinais"])
    _validar_lista_textos("recomendacoes", exercicio["recomendacoes"])

    return exercicio


def carregar_exercicios(
    caminho: str | Path = EXERCICIOS_PATH,
) -> list[dict[str, Any]]:
    caminho = Path(caminho)

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        raise ValueError("arquivo de exercicios nao contem JSON valido") from erro

    if not isinstance(dados, list):
        raise ValueError("arquivo de exercicios deve conter uma lista")

    if len(dados) != QUANTIDADE_EXERCICIOS:
        raise ValueError("arquivo deve conter exatamente 10 exercicios")

    return [_validar_exercicio(exercicio) for exercicio in dados]


def _formatar_lista(titulo: str, valores: list[str]) -> str:
    if not valores:
        return f"{titulo}: nenhum"

    itens = ", ".join(valores)
    return f"{titulo}: {itens}"


def _pedir_classificacao(
    entrada: Callable[[str], str],
    saida: Callable[[str], None],
) -> str:
    opcoes = ", ".join(sorted(CLASSIFICACOES_VALIDAS))

    while True:
        resposta = entrada(f"Sua classificação ({opcoes}): ").strip()

        if resposta in CLASSIFICACOES_VALIDAS:
            return resposta

        saida("Classificação inválida. Tente novamente.")


def executar_modo_aprender(
    entrada: Callable[[str], str] = input,
    saida: Callable[[str], None] = print,
    caminho: str | Path = EXERCICIOS_PATH,
) -> int:
    exercicios = carregar_exercicios(caminho)
    acertos = 0

    saida("=== Modo Aprender ===")

    for indice, exercicio in enumerate(exercicios, start=1):
        saida("")
        saida(f"Exercício {indice}/{len(exercicios)}")
        saida(f"Mensagem: {exercicio['mensagem']}")

        resposta_usuario = _pedir_classificacao(entrada, saida)
        classificacao_esperada = exercicio["classificacao_esperada"]

        if resposta_usuario == classificacao_esperada:
            acertos += 1
            saida("Resultado: você acertou.")
        else:
            saida("Resultado: você errou.")
            saida(f"Resposta esperada: {classificacao_esperada}")

        saida(_formatar_lista("Sinais", exercicio["sinais"]))
        saida(f"Explicação: {exercicio['explicacao']}")
        saida(_formatar_lista("Recomendações", exercicio["recomendacoes"]))

    aproveitamento = round((acertos / len(exercicios)) * 100, 2)

    saida("")
    saida("=== Resultado final ===")
    saida(f"Acertos: {acertos}/{len(exercicios)}")
    saida(f"Aproveitamento: {aproveitamento}%")

    return 0
