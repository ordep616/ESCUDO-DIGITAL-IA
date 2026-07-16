"""Testes das regras auxiliares da interface web."""

import unittest

from web import avancar_exercicio, formatar_confianca
from web import registrar_feedback_analise, registrar_resposta_aprender
from web import rotulo_classificacao


class WebTests(unittest.TestCase):
    def test_formata_classificacao_para_leitura_humana(self) -> None:
        self.assertEqual(rotulo_classificacao("baixo_risco"), "Baixo risco")
        self.assertEqual(
            rotulo_classificacao("informacao_insuficiente"),
            "Informação insuficiente",
        )

    def test_formata_confianca_com_nivel_e_valor_normalizado(self) -> None:
        texto, valor = formatar_confianca(0.92)

        self.assertEqual(texto, "Alta (92%)")
        self.assertEqual(valor, 0.92)

    def test_registra_feedback_sem_receber_mensagem(self) -> None:
        chamadas = []

        mensagem = registrar_feedback_analise("util", chamadas.append)

        self.assertEqual(chamadas, ["util"])
        self.assertIn("sem salvar a mensagem", mensagem)

    def test_resposta_do_aprender_contabiliza_uma_unica_vez(self) -> None:
        estado = {
            "acertos": 0,
            "respondido": False,
            "ultimo_acerto": None,
            "ultima_classificacao_esperada": None,
        }

        primeira = registrar_resposta_aprender(
            estado,
            "alto_risco",
            "alto_risco",
        )
        segunda = registrar_resposta_aprender(
            estado,
            "alto_risco",
            "alto_risco",
        )

        self.assertTrue(primeira)
        self.assertTrue(segunda)
        self.assertEqual(estado["acertos"], 1)
        self.assertTrue(estado["respondido"])

    def test_resposta_errada_do_aprender_nao_incrementa_acertos(self) -> None:
        estado = {
            "acertos": 2,
            "respondido": False,
            "ultimo_acerto": None,
            "ultima_classificacao_esperada": None,
        }

        acertou = registrar_resposta_aprender(
            estado,
            "baixo_risco",
            "alto_risco",
        )

        self.assertFalse(acertou)
        self.assertEqual(estado["acertos"], 2)
        self.assertEqual(estado["ultima_classificacao_esperada"], "alto_risco")

    def test_avancar_exercicio_reabre_resposta(self) -> None:
        estado = {
            "indice_exercicio": 3,
            "respondido": True,
            "ultimo_acerto": True,
            "ultima_classificacao_esperada": "moderado",
        }

        avancar_exercicio(estado)

        self.assertEqual(estado["indice_exercicio"], 4)
        self.assertFalse(estado["respondido"])
        self.assertIsNone(estado["ultimo_acerto"])
        self.assertIsNone(estado["ultima_classificacao_esperada"])


if __name__ == "__main__":
    unittest.main()
