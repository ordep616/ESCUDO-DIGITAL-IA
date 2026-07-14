"""Ponto de entrada da interface de terminal do Escudo Digital IA."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from ai_service import AIServiceError, analisar_mensagem
from interface import formatar_resultado, texto_introducao
from privacy import anonimizar_cpf_telefone
from prompts import SYSTEM_PROMPT_V1
from safety import validar_mensagem_usuario
from storage import registrar_consumo_basico
from validator import validar_resposta_ia


class RespostaIAInvalidaError(Exception):
    """Indica que a API retornou conteúdo que não pode ser apresentado."""


def processar_mensagem(mensagem: str, cliente: Any = None) -> dict[str, Any]:
    """Anonimiza, consulta a IA e valida a resposta estruturada."""
    mensagem_validada = validar_mensagem_usuario(mensagem)
    mensagem_segura = anonimizar_cpf_telefone(mensagem_validada)
    resposta_textual = analisar_mensagem(
        mensagem_segura,
        SYSTEM_PROMPT_V1,
        cliente,
    )

    registrar_consumo_basico(mensagem_segura)

    try:
        resposta = json.loads(resposta_textual)
    except json.JSONDecodeError as erro:
        raise RespostaIAInvalidaError(
            "A IA retornou uma resposta que não está em JSON válido."
        ) from erro

    erros = validar_resposta_ia(resposta)
    if erros:
        raise RespostaIAInvalidaError(
            "A resposta da IA está incompleta ou possui formato inválido."
        )

    return resposta


def executar_cli(
    entrada: Callable[[str], str] = input,
    saida: Callable[[str], None] = print,
) -> int:
    """Executa uma análise interativa e retorna um código de saída."""
    saida(texto_introducao())

    try:
        mensagem = entrada("\nMensagem: ")
        resultado = processar_mensagem(mensagem)
    except (EOFError, KeyboardInterrupt):
        saida("\nOperação cancelada.")
        return 130
    except (ValueError, AIServiceError, RespostaIAInvalidaError) as erro:
        saida(f"\nNão foi possível concluir a análise: {erro}")
        return 1

    saida("\n" + formatar_resultado(resultado))
    return 0


if __name__ == "__main__":
    raise SystemExit(executar_cli())
