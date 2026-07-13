"""Testes do serviço de API sem chamadas externas."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
)

from ai_service import (
    AIAuthenticationError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
    analisar_mensagem,
    criar_cliente,
)


def criar_resposta_http(status: int) -> httpx.Response:
    requisicao = httpx.Request(
        "POST", "https://openrouter.ai/api/v1/chat/completions"
    )
    return httpx.Response(status, request=requisicao)


class AIServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cliente = Mock()

    def test_retorna_texto_da_api(self) -> None:
        self.cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"classificacao":"alto_risco"}'
                    )
                )
            ]
        )

        resultado = analisar_mensagem("texto anonimizado", "prompt", self.cliente)

        self.assertEqual(resultado, '{"classificacao":"alto_risco"}')
        self.cliente.chat.completions.create.assert_called_once()

    def test_rejeita_mensagem_vazia_sem_chamar_api(self) -> None:
        with self.assertRaisesRegex(ValueError, "não pode estar vazia"):
            analisar_mensagem("   ", "prompt", self.cliente)

        self.cliente.chat.completions.create.assert_not_called()

    def test_rejeita_prompt_vazio_sem_chamar_api(self) -> None:
        with self.assertRaisesRegex(ValueError, "prompt não pode estar vazio"):
            analisar_mensagem("texto anonimizado", "", self.cliente)

        self.cliente.chat.completions.create.assert_not_called()

    def test_trata_timeout(self) -> None:
        requisicao = httpx.Request(
            "POST", "https://openrouter.ai/api/v1/chat/completions"
        )
        self.cliente.chat.completions.create.side_effect = APITimeoutError(
            requisicao
        )

        with self.assertRaises(AITimeoutError):
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

    def test_trata_erro_de_autenticacao(self) -> None:
        resposta = criar_resposta_http(401)
        self.cliente.chat.completions.create.side_effect = AuthenticationError(
            "chave inválida", response=resposta, body=None
        )

        with self.assertRaises(AIAuthenticationError):
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

    def test_trata_falha_de_conexao_como_indisponibilidade(self) -> None:
        requisicao = httpx.Request(
            "POST", "https://openrouter.ai/api/v1/chat/completions"
        )
        self.cliente.chat.completions.create.side_effect = APIConnectionError(
            request=requisicao
        )

        with self.assertRaises(AIUnavailableError):
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

    def test_trata_erro_interno_como_indisponibilidade(self) -> None:
        resposta = criar_resposta_http(500)
        self.cliente.chat.completions.create.side_effect = InternalServerError(
            "erro interno", response=resposta, body=None
        )

        with self.assertRaises(AIUnavailableError):
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

    def test_trata_resposta_vazia(self) -> None:
        self.cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content="   "))
            ]
        )

        with self.assertRaisesRegex(AIServiceError, "resposta vazia"):
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

    def test_trata_resposta_sem_texto(self) -> None:
        self.cliente.chat.completions.create.return_value = SimpleNamespace()

        with self.assertRaisesRegex(AIServiceError, "resposta vazia"):
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

    def test_trata_outro_erro_da_api_sem_expor_detalhes(self) -> None:
        resposta = criar_resposta_http(400)
        self.cliente.chat.completions.create.side_effect = APIStatusError(
            "conteúdo técnico sensível", response=resposta, body=None
        )

        with self.assertRaisesRegex(
            AIServiceError, "A API recusou a solicitação de análise"
        ) as contexto:
            analisar_mensagem("texto anonimizado", "prompt", self.cliente)

        self.assertNotIn("conteúdo técnico sensível", str(contexto.exception))

    def test_criar_cliente_rejeita_chave_ausente(self) -> None:
        variaveis = {"OPENROUTER_API_KEY": "", "OPENAI_API_KEY": ""}
        with patch.dict(os.environ, variaveis, clear=False):
            with patch("ai_service.load_dotenv"):
                with self.assertRaises(AIAuthenticationError):
                    criar_cliente()

    def test_criar_cliente_configura_endpoint_openrouter(self) -> None:
        variaveis = {
            "OPENROUTER_API_KEY": "chave-de-teste",
            "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
        }
        with patch.dict(os.environ, variaveis, clear=False):
            with patch("ai_service.load_dotenv"):
                with patch("ai_service.OpenAI") as classe_cliente:
                    criar_cliente()

        classe_cliente.assert_called_once_with(
            api_key="chave-de-teste",
            base_url="https://openrouter.ai/api/v1",
            timeout=20.0,
            max_retries=1,
        )


if __name__ == "__main__":
    unittest.main()
