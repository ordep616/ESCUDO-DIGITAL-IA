"""Funções locais para anonimização de dados pessoais."""

import re


MARCADOR_CPF = "[CPF OCULTADO]"
MARCADOR_TELEFONE = "[TELEFONE OCULTADO]"
MARCADOR_EMAIL = "[E-MAIL OCULTADO]"
MARCADOR_CARTAO = "[CARTÃO OCULTADO]"
MARCADOR_CODIGO = "[CÓDIGO OCULTADO]"
MARCADOR_LINK = "[LINK OCULTADO]"


_CPF_PATTERN = re.compile(
    r"(?<!\d)(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?!\d)"
)

_TELEFONE_PATTERN = re.compile(
    r"(?<!\d)(?:(?:\+?55)\s*)?"
    r"(?:\(\d{2}\)|\d{2})[\s.-]*"
    r"(?:9\d{4}|\d{4})[\s.-]?\d{4}(?!\d)"
)

_EMAIL_PATTERN = re.compile(
    r"(?<![\w.-])"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    r"(?![\w.-])"
)

_CARTAO_PATTERN = re.compile(
    r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)"
)

_CODIGO_PATTERN = re.compile(
    r"(?i)"
    r"(\b(?:c[oó]digo|token|otp|pin)"
    r"(?:\s+de\s+(?:acesso|seguran[cç]a|verifica[cç][aã]o|"
    r"autentica[cç][aã]o))?"
    r"\s*(?:é|:|-)?\s*)"
    r"\d{4,8}\b"
)

_LINK_PATTERN = re.compile(
    r"(?i)\b(?:https?://|www\.)[^\s<>()]+"
)

def anonimizar_dados_sensiveis(texto: str) -> str:
    """Oculta dados sensíveis antes do envio para serviços externos."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    resultado = _CPF_PATTERN.sub(MARCADOR_CPF, texto)
    resultado = _TELEFONE_PATTERN.sub(MARCADOR_TELEFONE, resultado)
    resultado = _EMAIL_PATTERN.sub(MARCADOR_EMAIL, resultado)
    resultado = _CARTAO_PATTERN.sub(MARCADOR_CARTAO, resultado)
    resultado = _CODIGO_PATTERN.sub(
        lambda encontrado: (
            encontrado.group(1) + MARCADOR_CODIGO
        ),
        resultado,
    )
    resultado = _LINK_PATTERN.sub(MARCADOR_LINK, resultado)

    return resultado

def anonimizar_cpf_telefone(texto: str) -> str:
    """Mantém compatibilidade com o nome utilizado inicialmente."""
    return anonimizar_dados_sensiveis(texto)
