"""Testes do fluxo principal sem chamadas externas."""

import json
import unittest
from unittest.mock import patch

from ai_service import AIUnavailableError
from main import RespostaIAInvalidaError, executar_cli, processar_mensagem


RESPOSTA_VALIDA = {
    "classificacao": "alto_risco",
    "confianca": 0.92,
    "sinais": ["urgencia"],
    "recomendacoes": ["usar_canal_oficial"],
    "explicacao_simples": "A mensagem cria pressão.",
    "informacao_insuficiente": False,
}


class MainTests(unittest.TestCase):
    @patch("main.analisar_mensagem")
    def test_processa_mensagem_anonimizada(self, analisar) -> None:
        analisar.return_value = json.dumps(RESPOSTA_VALIDA)

        resultado = processar_mensagem("Meu CPF é 123.456.789-00")

        self.assertEqual(resultado, RESPOSTA_VALIDA)
        mensagem_enviada = analisar.call_args.args[0]
        self.assertIn("[CPF OCULTADO]", mensagem_enviada)
        self.assertNotIn("123.456.789-00", mensagem_enviada)

    @patch("main.analisar_mensagem", return_value="não é json")
    def test_rejeita_json_invalido(self, _analisar) -> None:
        with self.assertRaises(RespostaIAInvalidaError):
            processar_mensagem("mensagem fictícia")

    @patch("main.analisar_mensagem")
    def test_rejeita_resposta_incompleta(self, analisar) -> None:
        analisar.return_value = json.dumps({"classificacao": "alto_risco"})

        with self.assertRaises(RespostaIAInvalidaError):
            processar_mensagem("mensagem fictícia")

    @patch("main.processar_mensagem", return_value=RESPOSTA_VALIDA)
    def test_cli_exibe_resultado_amigavel(self, _processar) -> None:
        saidas = []

        codigo = executar_cli(
            entrada=lambda _prompt: "mensagem fictícia",
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

        codigo = executar_cli(
            entrada=lambda _prompt: "mensagem fictícia",
            saida=saidas.append,
        )

        self.assertEqual(codigo, 1)
        self.assertIn("temporariamente indisponível", "\n".join(saidas))


if __name__ == "__main__":
    unittest.main()
