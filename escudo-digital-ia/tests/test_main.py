"""Testes do fluxo principal sem chamadas externas."""

import json
import unittest
from unittest.mock import patch

from ai_service import AIUnavailableError
from main import RespostaIAInvalidaError, executar_cli, processar_mensagem
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
