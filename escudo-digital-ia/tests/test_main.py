"""Testes do fluxo principal sem chamadas externas."""

import json
import unittest
from unittest.mock import patch

from ai_service import AIUnavailableError
from main import (
    RespostaIAInvalidaError,
    executar_cli,
    processar_imagem,
    processar_mensagem,
)
from safety import LIMITE_CARACTERES_MENSAGEM


RESPOSTA_VALIDA = {
    "classificacao": "alto_risco",
    "confianca": 0.92,
    "sinais": ["urgencia"],
    "recomendacoes": ["usar_canal_oficial"],
    "explicacao_simples": "A mensagem cria pressão.",
    "informacao_insuficiente": False,
}


class MainTests(unittest.TestCase):
    @patch("main.registrar_consumo_basico")
    @patch("main.analisar_mensagem")
    @patch("main.extrair_evidencias_imagem")
    def test_anonimiza_evidencias_visuais_antes_da_classificacao(
        self,
        extrair,
        analisar,
        registrar,
    ) -> None:
        extrair.return_value = {
            "texto_visivel": (
                "CPF 123.456.789-00, telefone (11) 99999-8888, "
                "código 123456 e https://exemplo.test/confirmar"
            ),
            "tipo_de_conteudo": "conversa em aplicativo de mensagens",
            "pedidos_identificados": ["envio de código"],
            "elementos_relevantes": ["urgência"],
            "urgencia_presente": True,
            "ameaca_presente": False,
            "link_presente": True,
            "qr_code_presente": False,
            "impede_verificacao": False,
            "texto_ilegivel": False,
            "incertezas": [],
        }
        analisar.return_value = json.dumps(RESPOSTA_VALIDA)

        resultado = processar_imagem(
            b"imagem simulada",
            "image/png",
        )

        self.assertEqual(resultado, RESPOSTA_VALIDA)
        mensagem_enviada = analisar.call_args.args[0]
        self.assertIn("[CPF OCULTADO]", mensagem_enviada)
        self.assertIn("[TELEFONE OCULTADO]", mensagem_enviada)
        self.assertIn("[CÓDIGO OCULTADO]", mensagem_enviada)
        self.assertIn("[LINK OCULTADO]", mensagem_enviada)
        self.assertNotIn("123.456.789-00", mensagem_enviada)
        self.assertNotIn("(11) 99999-8888", mensagem_enviada)
        self.assertNotIn("123456", mensagem_enviada)
        self.assertNotIn("https://exemplo.test", mensagem_enviada)
        registrar.assert_called_once_with(mensagem_enviada)

    @patch("main.processar_mensagem", return_value=RESPOSTA_VALIDA)
    @patch(
        "main.formatar_evidencias_para_analise",
        return_value="contexto visual estruturado",
    )
    @patch("main.extrair_evidencias_imagem")
    def test_processa_imagem_pelo_fluxo_atual(
        self,
        extrair,
        formatar,
        processar,
    ) -> None:
        evidencias = {"texto_visivel": "mensagem suspeita"}
        extrair.return_value = evidencias
        cliente = object()

        resultado = processar_imagem(
            b"imagem",
            "image/png",
            cliente,
        )

        self.assertEqual(resultado, RESPOSTA_VALIDA)
        extrair.assert_called_once_with(
            b"imagem",
            "image/png",
            cliente,
        )
        formatar.assert_called_once_with(evidencias)
        processar.assert_called_once_with(
            "contexto visual estruturado",
            cliente,
        )

    @patch("main.registrar_consumo_basico")
    @patch("main.analisar_mensagem")
    def test_processa_mensagem_anonimizada(self, analisar, _registrar) -> None:
        analisar.return_value = json.dumps(RESPOSTA_VALIDA)

        resultado = processar_mensagem("Meu CPF é 123.456.789-00")

        self.assertEqual(resultado, RESPOSTA_VALIDA)
        mensagem_enviada = analisar.call_args.args[0]
        self.assertIn("[CPF OCULTADO]", mensagem_enviada)
        self.assertNotIn("123.456.789-00", mensagem_enviada)

    @patch("main.registrar_consumo_basico")
    @patch("main.analisar_mensagem")
    def test_registra_consumo_com_mensagem_anonimizada(
        self,
        analisar,
        registrar,
    ) -> None:
        analisar.return_value = json.dumps(RESPOSTA_VALIDA)

        processar_mensagem("Meu CPF é 123.456.789-00")

        registrar.assert_called_once_with("Meu CPF é [CPF OCULTADO]")

    @patch("main.registrar_consumo_basico")
    @patch("main.analisar_mensagem")
    def test_rejeita_mensagem_grande_sem_chamar_ia(
        self,
        analisar,
        registrar,
    ) -> None:
        mensagem = "a" * (LIMITE_CARACTERES_MENSAGEM + 1)

        with self.assertRaisesRegex(ValueError, "grande demais"):
            processar_mensagem(mensagem)

        analisar.assert_not_called()
        registrar.assert_not_called()

    @patch("main.registrar_consumo_basico")
    @patch("main.analisar_mensagem", return_value="não é json")
    def test_rejeita_json_invalido(self, _analisar, _registrar) -> None:
        with self.assertRaises(RespostaIAInvalidaError):
            processar_mensagem("mensagem fictícia")

    @patch("main.registrar_consumo_basico")
    @patch("main.analisar_mensagem")
    def test_rejeita_resposta_incompleta(self, analisar, _registrar) -> None:
        analisar.return_value = json.dumps({"classificacao": "alto_risco"})

        with self.assertRaises(RespostaIAInvalidaError):
            processar_mensagem("mensagem fictícia")

    @patch("main.processar_mensagem", return_value=RESPOSTA_VALIDA)
    def test_cli_exibe_resultado_amigavel(self, _processar) -> None:
        saidas = []
        entradas = iter(["1", "mensagem fictícia"])

        codigo = executar_cli(
            entrada=lambda _prompt: next(entradas),
            saida=saidas.append,
        )

        self.assertEqual(codigo, 0)
        self.assertIn("Classificação: ALTO RISCO", "\n".join(saidas))

    @patch(
        "main.processar_mensagem",
        side_effect=AIUnavailableError("Serviço temporariamente indisponível."),
    )
    def test_cli_apresenta_erro_controlado(self, _processar) -> None:
        saidas = []
        entradas = iter(["1", "mensagem fictícia"])

        codigo = executar_cli(
            entrada=lambda _prompt: next(entradas),
            saida=saidas.append,
        )

        self.assertEqual(codigo, 1)
        self.assertIn("temporariamente indisponível", "\n".join(saidas))

    @patch("main.executar_modo_aprender", return_value=0)
    @patch("main.processar_mensagem")
    def test_cli_chama_modo_aprender(
        self,
        processar,
        executar_aprender,
    ) -> None:
        saidas = []

        codigo = executar_cli(
            entrada=lambda _prompt: "2",
            saida=saidas.append,
        )

        self.assertEqual(codigo, 0)
        executar_aprender.assert_called_once()
        processar.assert_not_called()

    @patch("main.executar_modo_aprender")
    @patch("main.processar_mensagem")
    def test_cli_sai_sem_executar_fluxos(
        self,
        processar,
        executar_aprender,
    ) -> None:
        saidas = []

        codigo = executar_cli(
            entrada=lambda _prompt: "3",
            saida=saidas.append,
        )

        self.assertEqual(codigo, 0)
        self.assertIn("Encerrando.", "\n".join(saidas))
        executar_aprender.assert_not_called()
        processar.assert_not_called()

    @patch("main.processar_mensagem")
    def test_cli_rejeita_opcao_invalida(self, processar) -> None:
        saidas = []

        codigo = executar_cli(
            entrada=lambda _prompt: "9",
            saida=saidas.append,
        )

        self.assertEqual(codigo, 1)
        self.assertIn("Opção inválida.", "\n".join(saidas))
        processar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
