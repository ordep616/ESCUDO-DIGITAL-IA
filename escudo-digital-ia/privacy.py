"""Funções locais para anonimização de dados pessoais."""

import re


MARCADOR_CPF = "[CPF OCULTADO]"
MARCADOR_TELEFONE = "[TELEFONE OCULTADO]"

_CPF_PATTERN = re.compile(
    r"(?<!\d)(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?!\d)"
)

_TELEFONE_PATTERN = re.compile(
    r"(?<!\d)(?:(?:\+?55)\s*)?"
    r"(?:\(\d{2}\)|\d{2})[\s.-]*"
    r"(?:9\d{4}|\d{4})[\s.-]?\d{4}(?!\d)"
)


def anonimizar_cpf_telefone(texto: str) -> str:
    """Oculta CPF e telefone brasileiro presentes em ``texto``.

    CPFs são reconhecidos nos formatos ``000.000.000-00`` e
    ``00000000000``. Telefones devem incluir DDD e podem conter o código
    do país 55. O texto original não é alterado; uma nova string é retornada.

    Args:
        texto: Conteúdo fictício ou autorizado que será anonimizado.

    Returns:
        Texto com os dados encontrados substituídos por marcadores fixos.

    Raises:
        TypeError: Se ``texto`` não for uma string.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    texto_sem_cpf = _CPF_PATTERN.sub(MARCADOR_CPF, texto)
    return _TELEFONE_PATTERN.sub(MARCADOR_TELEFONE, texto_sem_cpf)
