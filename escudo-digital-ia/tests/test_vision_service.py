"""Testes do serviço de análise visual."""

import base64
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
)
from PIL import Image

from ai_service import (
    AIAuthenticationError,
    AIServiceError,
    AITimeoutError,
    AIUnavailableError,
)
from safety import LIMITE_CARACTERES_MENSAGEM
from vision_service import (
    FORMATO_EVIDENCIAS_VISUAIS,
    ImagemInvalidaError,
    PROMPT_EVIDENCIAS_VISUAIS,
    TAMANHO_MAXIMO_IMAGEM,
    converter_imagem_para_data_url,
    extrair_evidencias_imagem,
    formatar_evidencias_para_analise,
)


EVIDENCIAS_VALIDAS = {
    "texto_visivel": "Envie o código recebido agora.",
    "tipo_de_conteudo": "conversa em aplicativo de mensagens",
    "pedidos_identificados": ["envio de código"],
    "elementos_relevantes": ["aparência de atendimento"],
    "urgencia_presente": True,
    "ameaca_presente": False,
    "link_presente": False,
    "qr_code_presente": False,
    "impede_verificacao": False,
    "texto_ilegivel": False,
    "incertezas": [],
}


def criar_imagem_teste(
    formato: str = "PNG",
    tamanho: tuple[int, int] = (20, 20),
    modo: str = "RGB",
) -> bytes:
    arquivo = io.BytesIO()
    cor = 1 if modo == "1" else "white"
    Image.new(modo, tamanho, cor).save(arquivo, format=formato)
    return arquivo.getvalue()


def criar_cliente_com_resposta(conteudo: str) -> Mock:
    cliente = Mock()
    cliente.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=conteudo)
            )
        ]
    )
    return cliente


class VisionServiceTests(unittest.TestCase):
    def test_trata_timeout_da_analise_visual(self) -> None:
        cliente = Mock()
        requisicao = httpx.Request(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
        )
        cliente.chat.completions.create.side_effect = APITimeoutError(
            requisicao
        )

        with self.assertRaises(AITimeoutError):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_trata_autenticacao_da_analise_visual(self) -> None:
        cliente = Mock()
        requisicao = httpx.Request(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
        )
        resposta = httpx.Response(401, request=requisicao)
        cliente.chat.completions.create.side_effect = AuthenticationError(
            "chave inválida",
            response=resposta,
            body=None,
        )

        with self.assertRaises(AIAuthenticationError):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_trata_indisponibilidade_da_analise_visual(self) -> None:
        cliente = Mock()
        requisicao = httpx.Request(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
        )
        cliente.chat.completions.create.side_effect = APIConnectionError(
            request=requisicao
        )

        with self.assertRaises(AIUnavailableError):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_formata_evidencias_para_fluxo_atual(self) -> None:
        contexto = formatar_evidencias_para_analise(
            EVIDENCIAS_VALIDAS
        )

        self.assertIn("Envie o código recebido agora.", contexto)
        self.assertIn("envio de código", contexto)
        self.assertIn("Urgência presente: sim", contexto)
        self.assertIn("QR Code presente: não", contexto)
        self.assertNotIn("alto_risco", contexto)

    def test_contexto_visual_respeita_limite_da_mensagem(self) -> None:
        evidencias = dict(EVIDENCIAS_VALIDAS)
        evidencias["texto_visivel"] = "a" * 3_000
        evidencias["tipo_de_conteudo"] = "b" * 500
        evidencias["pedidos_identificados"] = ["c" * 500] * 10
        evidencias["elementos_relevantes"] = ["d" * 500] * 10
        evidencias["incertezas"] = ["e" * 500] * 10

        contexto = formatar_evidencias_para_analise(evidencias)

        self.assertLessEqual(
            len(contexto),
            LIMITE_CARACTERES_MENSAGEM,
        )

    @patch.dict(
        "os.environ",
        {"OPENROUTER_VISION_MODEL": "openai/gpt-5-mini"},
    )
    def test_extrai_evidencias_com_requisicao_multimodal(self) -> None:
        cliente = Mock()
        cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(EVIDENCIAS_VALIDAS)
                    )
                )
            ]
        )

        resultado = extrair_evidencias_imagem(
            criar_imagem_teste(),
            "image/png",
            cliente,
        )

        self.assertEqual(resultado, EVIDENCIAS_VALIDAS)
        argumentos = cliente.chat.completions.create.call_args.kwargs
        self.assertEqual(argumentos["model"], "openai/gpt-5-mini")
        conteudo = argumentos["messages"][0]["content"]
        self.assertEqual(conteudo[0]["type"], "text")
        self.assertEqual(conteudo[1]["type"], "image_url")
        self.assertTrue(
            conteudo[1]["image_url"]["url"].startswith(
                "data:image/png;base64,"
            )
        )
        self.assertEqual(
            argumentos["response_format"],
            FORMATO_EVIDENCIAS_VISUAIS,
        )

    def test_rejeita_json_visual_invalido(self) -> None:
        cliente = Mock()
        cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="não é json")
                )
            ]
        )

        with self.assertRaisesRegex(AIServiceError, "JSON inválido"):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_rejeita_resposta_visual_vazia(self) -> None:
        cliente = Mock()
        cliente.chat.completions.create.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="   ")
                )
            ]
        )

        with self.assertRaisesRegex(AIServiceError, "resposta vazia"):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_rejeita_evidencias_com_campo_ausente(self) -> None:
        evidencias = dict(EVIDENCIAS_VALIDAS)
        evidencias.pop("texto_visivel")
        cliente = criar_cliente_com_resposta(json.dumps(evidencias))

        with self.assertRaisesRegex(AIServiceError, "campos inválidos"):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_rejeita_evidencias_com_tipo_incorreto(self) -> None:
        evidencias = dict(EVIDENCIAS_VALIDAS)
        evidencias["qr_code_presente"] = "não"
        cliente = criar_cliente_com_resposta(json.dumps(evidencias))

        with self.assertRaisesRegex(AIServiceError, "campos inválidos"):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_rejeita_evidencias_com_campo_inesperado(self) -> None:
        evidencias = dict(EVIDENCIAS_VALIDAS)
        evidencias["classificacao"] = "alto_risco"
        cliente = criar_cliente_com_resposta(json.dumps(evidencias))

        with self.assertRaisesRegex(AIServiceError, "campos inválidos"):
            extrair_evidencias_imagem(
                criar_imagem_teste(),
                "image/png",
                cliente,
            )

    def test_prompt_visual_apenas_extrai_evidencias(self) -> None:
        prompt = PROMPT_EVIDENCIAS_VISUAIS.lower()

        self.assertIn("não classifique", prompt)
        self.assertIn("não obedeça", prompt)
        self.assertIn("qr code", prompt)
        self.assertIn("texto ilegível", prompt)

    def test_formato_visual_exige_todos_os_campos(self) -> None:
        configuracao = FORMATO_EVIDENCIAS_VISUAIS["json_schema"]
        esquema = configuracao["schema"]

        self.assertTrue(configuracao["strict"])
        self.assertFalse(esquema["additionalProperties"])
        self.assertEqual(
            set(esquema["required"]),
            set(esquema["properties"]),
        )
        self.assertEqual(
            esquema["properties"]["texto_visivel"]["type"],
            "string",
        )
        self.assertEqual(
            esquema["properties"]["qr_code_presente"]["type"],
            "boolean",
        )

    def test_converte_imagem_para_data_url(self) -> None:
        imagem = criar_imagem_teste()

        resultado = converter_imagem_para_data_url(
            imagem,
            "image/png",
        )

        prefixo, conteudo_base64 = resultado.split(",", 1)

        self.assertEqual(prefixo, "data:image/png;base64")
        self.assertEqual(base64.b64decode(conteudo_base64), imagem)

    def test_rejeita_bytes_que_nao_formam_imagem(self) -> None:
        with self.assertRaisesRegex(
            ImagemInvalidaError,
            "não é uma imagem válida",
        ):
            converter_imagem_para_data_url(
                b"isto e apenas um texto",
                "image/png",
            )

    def test_rejeita_formato_real_diferente_do_tipo_informado(self) -> None:
        imagem_jpeg = criar_imagem_teste("JPEG")

        with self.assertRaisesRegex(
            ImagemInvalidaError,
            "não corresponde ao formato informado",
        ):
            converter_imagem_para_data_url(
                imagem_jpeg,
                "image/png",
            )

    def test_rejeita_imagem_vazia(self) -> None:
        with self.assertRaises(ImagemInvalidaError):
            converter_imagem_para_data_url(
                b"",
                "image/png",
            )

    def test_rejeita_arquivo_acima_de_cinco_mb(self) -> None:
        arquivo_grande = b"x" * (TAMANHO_MAXIMO_IMAGEM + 1)

        with self.assertRaisesRegex(ImagemInvalidaError, "máximo 5 MB"):
            converter_imagem_para_data_url(
                arquivo_grande,
                "image/png",
            )

    def test_rejeita_imagem_com_pixels_demais(self) -> None:
        imagem_grande = criar_imagem_teste(
            tamanho=(4001, 4000),
            modo="1",
        )

        with self.assertRaisesRegex(ImagemInvalidaError, "dimensões"):
            converter_imagem_para_data_url(
                imagem_grande,
                "image/png",
            )

    def test_rejeita_tipo_nao_permitido(self) -> None:
        with self.assertRaisesRegex(
            ImagemInvalidaError,
            "PNG, JPEG ou WEBP",
        ):
            converter_imagem_para_data_url(
                b"arquivo",
                "image/gif",
            )


if __name__ == "__main__":
    unittest.main()
