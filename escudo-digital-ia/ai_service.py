"""Comunicação segura com a API de inteligência Artificial."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)


MODELO_PADRAO = "gpt-5.6-luna"

FORMATO_ANALISE_RISCO = {
    "format": {
        "type": "json_schema",
        "name": "analise_risco",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "classificacao": {
                    "type": "string",
                    "enum": [
                        "baixo_risco",
                        "moderado",
                        "alto_risco",
                        "informacao_insuficiente",
                    ],
                },
                "confianca": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
                "sinais": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "recomendacoes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "explicacao_simples": {
                    "type": "string",
                    "minLength": 1,
                },
                "informacao_insuficiente": {"type": "boolean"},
            },
            "required": [
                "classificacao",
                "confianca",
                "sinais",
                "recomendacoes",
                "explicacao_simples",
                "informacao_insuficiente",
            ],
            "additionalProperties": False,
        },
    }
}


class AIServiceError(Exception):
    """Erro geral do serviço de inteligência artificial."""


class AITimeoutError(AIServiceError):
    """A API demorou mais que o limite permitido."""


class AIAuthenticationError(AIServiceError):
    """A chave da API está ausente ou foi recusada."""


class AIUnavailableError(AIServiceError):
    """A API está temporariamente indisponível."""


def criar_cliente() -> OpenAI:
    """Cria um cliente configurado sem expor a chave da API."""
    caminho_env = Path(__file__).with_name(".env")
    load_dotenv(caminho_env)

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise AIAuthenticationError("A chave da API não foi configurada.")

    return OpenAI(
        api_key=api_key,
        timeout=20.0,
        max_retries=1,
    )


def analisar_mensagem(
    mensagem_anonimizada: str,
    prompt: str,
    cliente: Optional[OpenAI] = None,
) -> str:
    """Envia conteúdo anonimizado e retorna a resposta textual bruta.

    Este módulo não valida o JSON retornado. Essa responsabilidade pertence
    ao ``validator.py``. O parâmetro ``cliente`` permite testes sem rede.
    """
    if not isinstance(mensagem_anonimizada, str):
        raise TypeError("mensagem_anonimizada deve ser uma string")
    if not mensagem_anonimizada.strip():
        raise ValueError("mensagem_anonimizada não pode estar vazia")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt não pode estar vazio")

    cliente_api = cliente or criar_cliente()
    modelo = os.getenv("OPENAI_MODEL", MODELO_PADRAO).strip()
    if not modelo:
        raise AIServiceError("O modelo da API não foi configurado.")

    try:
        resposta = cliente_api.responses.create(
            model=modelo,
            instructions=prompt,
            input=mensagem_anonimizada,
            text=FORMATO_ANALISE_RISCO,
        )
        texto_bruto = getattr(resposta, "output_text", None)
        if not isinstance(texto_bruto, str) or not texto_bruto.strip():
            raise AIServiceError("A API retornou uma resposta vazia.")
        return texto_bruto.strip()

    except APITimeoutError as erro:
        raise AITimeoutError(
            "A análise demorou demais. Tente novamente mais tarde."
        ) from erro
    except AuthenticationError as erro:
        raise AIAuthenticationError(
            "A API recusou a configuração de autenticação."
        ) from erro
    except (APIConnectionError, InternalServerError, RateLimitError) as erro:
        raise AIUnavailableError(
            "O serviço de análise está temporariamente indisponível."
        ) from erro
    except APIStatusError as erro:
        if erro.status_code >= 500:
            raise AIUnavailableError(
                "O serviço de análise está temporariamente indisponível."
            ) from erro
        raise AIServiceError("A API recusou a solicitação de análise.") from erro
