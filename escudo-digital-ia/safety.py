"""Regras locais de segurança antes da análise pela IA."""

from __future__ import annotations


LIMITE_CARACTERES_MENSAGEM = 1000


def validar_mensagem_usuario(mensagem: str) -> str:
    """Valida a mensagem antes de anonimizar e enviar para análise."""
    if not isinstance(mensagem, str):
        raise TypeError("mensagem deve ser uma string")

    mensagem_limpa = mensagem.strip()

    if not mensagem_limpa:
        raise ValueError("Digite uma mensagem fictícia para analisar.")

    if len(mensagem_limpa) > LIMITE_CARACTERES_MENSAGEM:
        raise ValueError("A mensagem é grande demais para análise.")

    return mensagem_limpa
